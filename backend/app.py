"""
app.py — two ways to run Sarthi's backend.

1) CLI (no dependencies, no API key):
       python -m backend.app
   Runs all three journeys and prints the full agent trace + resulting DNA.

2) API (needs `pip install fastapi uvicorn`):
       uvicorn backend.app:api --reload
   POST /journey  { "scenario": "ramesh" | "anjali" | "vikram" }
   -> returns { reply, trace, dna }

The scenarios below seed the shared Financial DNA; the Orchestrator does the
rest. This is the same flow the front-end console visualises.
"""
from __future__ import annotations

from .core import Context, FinancialDNA, MockLLM, Tools, Trace
from .agents import Orchestrator


# --------------------------------------------------------------------------- #
#  Scenario seeds
# --------------------------------------------------------------------------- #
def seed(scenario: str) -> tuple[FinancialDNA, dict]:
    if scenario == "ramesh":
        dna = FinancialDNA(
            customer_id="C-RAMESH",
            profile={"segment": "Kirana/SME", "language": "hi", "status": "Dormant"},
            holdings=["Savings A/c"],
            signals={"cashflow_pattern": "festive_spike", "inflow_12mo": 460_000},
            engagement_score=22,
        )
        return dna, {"kind": "signal"}

    if scenario == "anjali":
        dna = FinancialDNA(
            customer_id="C-ANJALI",
            profile={"segment": "first-time/student", "language": "hi", "status": "prospect"},
            holdings=[],
            engagement_score=5,
        )
        return dna, {"kind": "inbound", "new_prospect": True}

    if scenario == "vikram":
        dna = FinancialDNA(
            customer_id="C-VIKRAM",
            profile={"segment": "salaried", "language": "en", "status": "single-product"},
            holdings=["Savings A/c"],
            signals={"idle_balance": 180_000},
            engagement_score=40,
        )
        return dna, {"kind": "signal"}

    raise ValueError(f"unknown scenario: {scenario}")


def run_journey(scenario: str) -> dict:
    dna, request = seed(scenario)
    ctx = Context(dna=dna, tools=Tools(), llm=MockLLM(), trace=Trace(), lang=dna.profile["language"])
    result = Orchestrator(ctx).run(request)
    return {
        "reply": result.get("reply"),
        "escalated": result.get("escalated", False),
        "dna": {
            "status": dna.profile.get("status"),
            "holdings": dna.holdings,
            "engagement_score": dna.engagement_score,
        },
        "trace": ctx.trace.as_dict(),
    }


# --------------------------------------------------------------------------- #
#  Optional FastAPI surface
# --------------------------------------------------------------------------- #
try:
    from fastapi import FastAPI
    from pydantic import BaseModel

    api = FastAPI(title="SBI Sarthi", version="0.1.0")

    class JourneyIn(BaseModel):
        scenario: str

    @api.post("/journey")
    def journey(body: JourneyIn) -> dict:
        return run_journey(body.scenario)

    @api.get("/health")
    def health() -> dict:
        return {"ok": True}
except ImportError:  # FastAPI not installed — CLI mode still works
    api = None


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    for sc in ("ramesh", "anjali", "vikram"):
        print("\n" + "=" * 74)
        print(f"JOURNEY: {sc}")
        print("=" * 74)
        out = run_journey(sc)
        print("\n→ Sarthi reply:", out["reply"])
        print("→ Final DNA   :", out["dna"])
