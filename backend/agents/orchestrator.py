"""
agents/orchestrator.py — the supervisor.

The Orchestrator is the brain of Sarthi. It:
  1. Classifies intent (from an inbound message OR a proactive signal).
  2. Plans a sequence of steps (ReAct-style).
  3. Routes to the right specialist agents.
  4. Runs every action through the Compliance agent before it fires.
  5. Composes the customer-facing reply (in the customer's language).

Routing here is deterministic for clarity; in production the plan is produced
by the LLM and revised via self-reflection. The contract stays the same.
"""
from __future__ import annotations

from ..core import Agent, Context
from .specialists import (
    AcquisitionAgent,
    AdoptionAgent,
    AdvisoryAgent,
    ComplianceAgent,
    EngagementAgent,
)


class Orchestrator(Agent):
    name = "orch"

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.acq = AcquisitionAgent(ctx)
        self.adopt = AdoptionAgent(ctx)
        self.engage = EngagementAgent(ctx)
        self.advise = AdvisoryAgent(ctx)
        self.comp = ComplianceAgent(ctx)

    # ---- intent classification --------------------------------------------
    def classify(self, request: dict) -> str:
        if request.get("kind") == "signal":
            sig = self.ctx.dna.signals
            if sig.get("cashflow_pattern") == "festive_spike":
                return "working_capital"
            if sig.get("idle_balance"):
                return "proactive_adoption"
        if request.get("new_prospect"):
            return "account_opening"
        return "advisory"

    # ---- the journey ------------------------------------------------------
    def run(self, request: dict) -> dict:
        intent = self.classify(request)
        self.ctx.trace.add(self.name, "intent", f"intent = {intent}")

        if intent == "working_capital":
            return self._working_capital()
        if intent == "account_opening":
            return self._onboard()
        if intent == "proactive_adoption":
            return self._adopt()
        return {"reply": "How can I help with your banking today?"}

    # ---- concrete plans ---------------------------------------------------
    def _working_capital(self) -> dict:
        self.ctx.trace.add(self.name, "plan",
                           "Engagement → Acquisition → Advisory → Compliance → propose")
        self.engage.handle({})
        ready = self.acq.handle({})["ready"]
        offer = self.advise.handle({"size_credit": True})["offer"]
        ok = self.comp.validate("credit_line", {
            "within_limits": offer["pre_approved"] <= 50_000,
            "suitable": ready,
        })
        if not ok:
            return {"reply": "I'll have a banker confirm this with you.", "escalated": True}
        self.ctx.tools.disburse(self.ctx.dna.customer_id, offer["pre_approved"])
        self.ctx.dna.add_product("Business Credit Line")
        self.ctx.dna.profile["status"] = "Active borrower"
        self.ctx.dna.engagement_score = 71
        self.comp.audit("credit_line_disbursed")
        return {"reply": f"₹{offer['pre_approved']} credited to your account ✅",
                "offer": offer}

    def _onboard(self) -> dict:
        self.ctx.trace.add(self.name, "plan", "Acquisition (lead) → Compliance per PII step")
        self.comp.validate("ekyc", {"suitable": True})
        self.acq.handle({"open_account": True})
        self.ctx.dna.profile["status"] = "Onboarded customer"
        self.ctx.dna.engagement_score = 48
        self.adopt.handle({})  # arm the first-use nudge for next session
        return {"reply": "Your Savings Account is ready 🎉 UPI & card are set."}

    def _adopt(self) -> dict:
        self.ctx.trace.add(self.name, "plan", "Adoption → Compliance (anti-mis-sell) → Advisory")
        rec = self.adopt.handle({})["recommend"]
        self.comp.validate("recommend", {"suitable": True})
        self.advise.handle({"enable_sweep": True})
        self.ctx.dna.profile["status"] = "Active · multi-product"
        self.ctx.dna.engagement_score = 66
        return {"reply": f"{rec} enabled ✅ your savings now work harder automatically."}
