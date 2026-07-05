# Sarthi — Architecture

Sarthi is a **supervised multi-agent system**, not a chatbot. A single
Orchestrator senses a signal (or an inbound message), plans a journey, and
routes work to specialist agents — each owning one pillar of the SBI problem
statement — while a Compliance agent validates every action before it fires.

```
                         ┌──────────── SIGNALS IN ────────────┐
                         │ message · voice · life-event ·     │
                         │ cashflow · dormancy                │
                         └───────────────┬────────────────────┘
                                         │
                              ┌──────────▼──────────┐        ┌───────────────────────┐
                              │   ORCHESTRATOR      │◄──────►│  COMPLIANCE & GUARDRAIL│
                              │  intent · plan ·    │        │  validates every action│
                              │  route · compose    │        │  RBI · KYC · PII · audit│
                              └──────────┬──────────┘        └───────────────────────┘
                ┌───────────────┬────────┴────────┬────────────────┐
        ┌───────▼──────┐ ┌──────▼──────┐  ┌────────▼─────┐  ┌────────▼────────┐
        │ ACQUISITION  │ │  ADOPTION   │  │  ENGAGEMENT  │  │  ADVISORY / TXN │
        │ onboard·KYC  │ │ activate·fit│  │ proactive·   │  │ answer & act via│
        │              │ │             │  │ life-events  │  │ banking tools   │
        └──────┬───────┘ └──────┬──────┘  └──────┬───────┘  └────────┬────────┘
               └────────────────┴──────┬─────────┴───────────────────┘
                    ┌──────────────────▼───────────────────┐
                    │  FINANCIAL DNA  (shared memory)       │
                    │  Customer-360 · behavioural · episodic│
                    │  · consent ledger                     │
                    └──────────────────┬────────────────────┘
              ┌──────────────┬─────────┴────────────┬──────────────┐
        ┌─────▼─────┐  ┌─────▼─────┐          ┌──────▼──────┐ ┌─────▼─────┐
        │ TOOL LAYER│  │ AGENTIC   │          │  INDIC ASR/ │ │  LLM      │
        │ (MCP):    │  │ RAG:      │          │  TTS: 15+   │ │ on-prem   │
        │ core bank │  │ products· │          │  languages  │ │ capable   │
        │ ·UPI·CKYC │  │ policy·RBI│          │             │ │           │
        └───────────┘  └───────────┘          └─────────────┘ └───────────┘
```

## Why multi-agent (and not one big prompt)

- **Separation of concerns** — each pillar is an independently ownable,
  testable, evaluable agent. Product teams can ship the Adoption agent without
  touching Acquisition.
- **Governance is structural** — the Compliance agent is a *gate*, not a
  guideline. No specialist calls a tool without a PASS.
- **Explainability** — the `Trace` object records intent → plan → tool → RAG →
  compliance → outcome for every journey, ready for RBI review.

## Control flow (see `backend/agents/orchestrator.py`)

1. **Classify** intent from a signal or message.
2. **Plan** the specialist sequence (ReAct; LLM-produced in production).
3. **Route** to specialists; they read/write the shared `FinancialDNA`.
4. **Validate** each action via `ComplianceAgent.validate(...)`.
5. **Execute** through the governed `Tools` layer (or escalate to a human if the
   guardrail returns REVIEW).
6. **Compose** the reply in the customer's language and **audit** the outcome.

## Extending to production

| Component        | Prototype (this repo)        | Production                                   |
|------------------|------------------------------|----------------------------------------------|
| Reasoning        | deterministic routing        | LLM planner + self-reflection (LangGraph)    |
| Memory           | in-process `FinancialDNA`     | Customer-360 store + vector episodic memory  |
| Tools            | mocked `Tools` facade         | MCP servers over core banking / UPI / CKYC   |
| Grounding        | `rag_retrieve` stub           | Agentic RAG over product/policy/RBI corpus   |
| Language         | EN/HI strings                 | Indic ASR/TTS (Bhashini-style), 15+ langs    |
| Audit            | `print` + `Trace`             | append-only, tamper-evident log              |

The **agent contracts do not change** as you swap these in — that is the point
of the design.
