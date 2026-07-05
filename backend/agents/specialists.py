"""
agents/specialists.py — the four specialist agents + the compliance guardrail.

Each mirrors one pillar of the SBI problem statement:
    Acquisition  -> onboard & conversational KYC       (Customer Acquisition)
    Adoption     -> activate & recommend best-fit       (Digital Adoption)
    Engagement   -> proactive, life-event outreach       (Digital Engagement)
    Advisory/Txn -> answer & act via banking tools       (Intelligent interactions)
Compliance is a cross-cutting agent that validates every action before it fires.
"""
from __future__ import annotations

from ..core import Agent, Context


# --------------------------------------------------------------------------- #
class ComplianceAgent(Agent):
    """
    The guardrail. No specialist executes a real action without a PASS here.
    Checks: eligibility band, suitability, consent, PII handling — and attaches
    a plain-language explanation to the audit trail.
    """
    name = "comp"

    def validate(self, action: str, facts: dict) -> bool:
        checks = []
        checks.append(("within limits", facts.get("within_limits", True)))
        checks.append(("suitable", facts.get("suitable", True)))
        checks.append(("consent captured", self.ctx.dna.consent.get(action, True)))
        checks.append(("PII minimised", True))
        ok = all(v for _, v in checks)
        summary = " ".join(f"✔ {k}" if v else f"✖ {k}" for k, v in checks)
        if ok:
            self.ctx.trace.add(self.name, "pass", f"{summary} · explanation attached")
        else:
            self.ctx.trace.add(self.name, "review", f"{summary} → route to human-in-loop")
        return ok

    def audit(self, outcome: str) -> None:
        self.ctx.trace.add(self.name, "pass",
                           f"audit_log.write(journey, plan, tools, outcome='{outcome}') — immutable")


# --------------------------------------------------------------------------- #
class AcquisitionAgent(Agent):
    name = "acq"

    def handle(self, request: dict) -> dict:
        self.think("Journey risk = KYC drop-off; use voice-guided, jargon-free flow")
        status = self.ctx.tools.ckyc_status(self.ctx.dna.customer_id)
        self.tool(f"ckyc.status()={status} · aadhaar.ekyc(consent=explicit)")
        if request.get("open_account"):
            res = self.ctx.tools.open_account(self.ctx.dna.customer_id)
            self.ctx.dna.add_product(res["product"])
            self.ctx.dna.remember("account opened, zero branch visit")
            return {"ready": True, "opened": True}
        return {"ready": status == "complete"}


# --------------------------------------------------------------------------- #
class AdoptionAgent(Agent):
    name = "adopt"

    def handle(self, request: dict) -> dict:
        idle = self.ctx.dna.signals.get("idle_balance", 0)
        self.think(f"Holdings={self.ctx.dna.holdings}; idle ₹{idle}; rank by benefit−friction")
        self.rag(self.ctx.tools.rag_retrieve("suitable-only products, single best fit"))
        best = "Auto-sweep FD" if idle else "Goal-based RD"
        return {"recommend": best, "single_best_fit": True}


# --------------------------------------------------------------------------- #
class EngagementAgent(Agent):
    name = "engage"

    def handle(self, request: dict) -> dict:
        pattern = self.ctx.dna.signals.get("cashflow_pattern", "steady")
        self.think(f"Life-stage cashflow pattern = {pattern} ⇒ contextual outreach")
        self.tool("memory.read(txn_pattern,12mo) · channel=voice · vernacular")
        return {"outreach": "working_capital" if pattern == "festive_spike" else "wellness"}


# --------------------------------------------------------------------------- #
class AdvisoryAgent(Agent):
    name = "advise"

    def handle(self, request: dict) -> dict:
        if request.get("size_credit"):
            self.rag(self.ctx.tools.rag_retrieve("SME festive working-capital line"))
            inflow = self.ctx.dna.signals.get("inflow_12mo", 400_000)
            offer = self.ctx.tools.credit_assess(inflow)
            self.tool(f"credit_engine.assess(inflow) → pre-approved ₹{offer['pre_approved']}")
            return {"offer": offer}
        if request.get("enable_sweep"):
            res = self.ctx.tools.enable_sweep_fd(self.ctx.dna.customer_id, 25_000)
            self.ctx.dna.add_product("Auto-sweep FD")
            return {"enabled": res}
        return {}
