"""
core.py — Foundations for the Sarthi multi-agent system.

Everything an agent needs: a shared Financial DNA memory, a pluggable LLM
interface (mockable so the repo runs with no API key), a governed tool layer,
and a Trace object so every autonomous decision is explainable and auditable.

Design goals:
  * Framework-agnostic — swap in LangGraph / OpenAI Agents SDK without changing
    the agent contracts below.
  * Governance first — no agent touches a tool without the Compliance agent.
  * Explainable — every step is recorded on the Trace for audit / RBI review.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


# --------------------------------------------------------------------------- #
#  Trace — the immutable audit record of a journey
# --------------------------------------------------------------------------- #
@dataclass
class TraceStep:
    agent: str
    kind: str           # intent | plan | think | tool | rag | pass | review
    text: str
    ts: float = field(default_factory=time.time)


@dataclass
class Trace:
    journey_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    steps: list[TraceStep] = field(default_factory=list)

    def add(self, agent: str, kind: str, text: str) -> None:
        self.steps.append(TraceStep(agent, kind, text))
        # In production this also streams to an append-only, tamper-evident log.
        print(f"[{self.journey_id}] {agent.upper():10} {kind:6} {text}")

    def as_dict(self) -> dict:
        return {
            "journey_id": self.journey_id,
            "steps": [s.__dict__ for s in self.steps],
        }


# --------------------------------------------------------------------------- #
#  Financial DNA — the shared, living customer memory
# --------------------------------------------------------------------------- #
@dataclass
class FinancialDNA:
    """Customer-360 + behavioural + episodic memory shared by every agent."""
    customer_id: str
    profile: dict[str, Any] = field(default_factory=dict)     # segment, language, life-stage…
    holdings: list[str] = field(default_factory=list)         # products held
    signals: dict[str, Any] = field(default_factory=dict)     # cashflow, dormancy, life-events
    consent: dict[str, bool] = field(default_factory=dict)    # purpose-bound consent ledger
    engagement_score: int = 0
    episodic: list[str] = field(default_factory=list)         # what happened, in order

    def remember(self, event: str) -> None:
        self.episodic.append(event)

    def add_product(self, product: str) -> None:
        if product not in self.holdings:
            self.holdings.append(product)


# --------------------------------------------------------------------------- #
#  LLM interface — pluggable, with a deterministic mock for offline runs
# --------------------------------------------------------------------------- #
class LLM:
    """Swap MockLLM for a real client (Anthropic / open-weight, on-prem)."""

    def complete(self, system: str, prompt: str, **kw) -> str:  # pragma: no cover
        raise NotImplementedError


class MockLLM(LLM):
    """Returns canned, structure-preserving text so the pipeline runs anywhere."""

    def complete(self, system: str, prompt: str, **kw) -> str:
        return "[mock-llm] " + prompt.strip().split("\n")[0][:120]


# --------------------------------------------------------------------------- #
#  Tool layer — governed integrations (mocked). Real impls call core banking.
# --------------------------------------------------------------------------- #
class Tools:
    """
    A thin, governed facade over bank systems. Every call is intended to be
    wrapped by the Compliance agent before execution (see compliance_agent).
    Exposed to the LLM as MCP-style tools in production.
    """

    def ckyc_status(self, customer_id: str) -> str:
        return "complete"

    def credit_assess(self, income_proxy: float) -> dict:
        limit = min(50_000, round(income_proxy * 0.12, -3))
        return {"pre_approved": limit, "emi": round(limit / 22), "rate": "eligible"}

    def rag_retrieve(self, query: str) -> str:
        # In production: agentic RAG over product catalogue, policy & RBI corpus.
        return f"top-k docs for: {query}"

    def disburse(self, customer_id: str, amount: int) -> dict:
        return {"status": "credited", "amount": amount}

    def enable_sweep_fd(self, customer_id: str, threshold: int) -> dict:
        return {"status": "active", "threshold": threshold}

    def open_account(self, customer_id: str) -> dict:
        return {"status": "opened", "product": "Savings A/c"}


# --------------------------------------------------------------------------- #
#  Agent base class — the shared contract
# --------------------------------------------------------------------------- #
@dataclass
class Context:
    dna: FinancialDNA
    tools: Tools
    llm: LLM
    trace: Trace
    lang: str = "en"


class Agent:
    """All specialist agents implement handle(). Name drives the trace tag."""
    name: str = "agent"

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def think(self, text: str) -> None:
        self.ctx.trace.add(self.name, "think", text)

    def tool(self, text: str) -> None:
        self.ctx.trace.add(self.name, "tool", text)

    def rag(self, text: str) -> None:
        self.ctx.trace.add(self.name, "rag", text)

    def handle(self, request: dict) -> dict:  # pragma: no cover
        raise NotImplementedError
