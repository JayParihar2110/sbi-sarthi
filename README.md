<h1 align="center">SBI Sarthi &nbsp;·&nbsp; सारथी</h1>
<p align="center"><b>The Autonomous Agentic Banking Companion for Bharat</b></p>
<p align="center"><i>A multi-agent AI that turns YONO from an app you open into a banker that comes to you —<br>acquiring, activating and engaging 530&nbsp;million customers, in their own language.</i></p>

<p align="center">
  <img alt="theme" src="https://img.shields.io/badge/Theme-Agentic%20AI%20%26%20Emerging%20Tech-2D6CDF">
  <img alt="event" src="https://img.shields.io/badge/SBI%20Hackathon-GFF%202026-F5A623">
  <img alt="license" src="https://img.shields.io/badge/License-MIT-24C4A8">
  <img alt="status" src="https://img.shields.io/badge/demo-runs%20offline%2C%20no%20API%20key-brightgreen">
</p>

---

## The problem (in one line)

India's largest bank has **53 crore customers** but only **~10 crore** are digitally engaged. A human relationship manager can serve a few hundred people; SBI has 530 million. **Acquisition, adoption and engagement all break at the point where a person is supposed to guide the customer — and that person doesn't exist.**

## The idea

Sarthi is **not a bigger chatbot.** It is a **supervised team of AI agents** inside YONO — one per pillar of the problem statement — that **senses, decides and acts** on the customer's behalf, proactively, in 15+ Indian languages, with a compliance agent checking every step.

| Pillar (SBI problem statement) | Sarthi agent | What it does autonomously |
|---|---|---|
| **Customer Acquisition** | Acquisition Agent | Qualifies leads, runs conversational voice-KYC, onboards with zero branch visit |
| **Digital Adoption** | Adoption Agent | Detects unused products/idle balances, recommends the single best fit, guides first use |
| **Digital Engagement** | Engagement Agent | Reaches out *first* on life-events & cashflow signals — no generic push spam |
| *(cross-cutting)* | Advisory/Txn + **Compliance** | Answers & acts via banking tools; validates, explains & audits every action |

All agents share a living **Financial DNA** memory, so context never resets.

---

## ▶ Run it

### 1. The live demo (no install, no key)
Open **[`frontend/index.html`](frontend/index.html)** in any browser — or host it on GitHub Pages.
Pick a journey, press **Run**, and watch the customer's chat on the left while the **agent orchestration console** on the right shows the orchestrator planning, specialists working, the compliance agent validating, and the Financial DNA updating — live. Toggle **EN / हिंदी**.

### 2. The backend (pure Python, no deps)
```bash
python -m backend.app          # runs all 3 journeys, prints the full agent trace
```
Optional HTTP API:
```bash
pip install -r requirements.txt
uvicorn backend.app:api --reload
curl -X POST localhost:8000/journey -H 'content-type: application/json' -d '{"scenario":"ramesh"}'
```

---

## Three journeys (front-end and back-end tell the same story)

- **`ramesh`** — *Dormant → Working capital.* A festive-cashflow signal triggers a voice outreach in Hindi; Sarthi pre-approves and disburses a ₹50k SME credit line inside the chat. A balance-checker becomes an active borrower — **acquisition, adoption and engagement solved in one conversation.**
- **`anjali`** — *New-prospect onboarding.* A jargon-free, voice-guided KYC opens a first bank account with no branch visit and arms an adoption nudge for next session.
- **`vikram`** — *Idle balance → Adoption.* An exit-risk + idle-cash signal prompts a single, suitable auto-sweep-FD nudge (anti-mis-sell checked), turning ₹1.8L of idle savings into higher earnings in one tap.

---

## How it works

A single **Orchestrator** classifies intent → plans (ReAct) → routes to specialists → runs every action through the **Compliance** guardrail → composes the reply in the customer's language, all over a shared **Financial DNA** memory. Full diagram and control flow in **[`docs/architecture.md`](docs/architecture.md)**.

```
SIGNAL ─▶ ORCHESTRATOR ─▶ [Acquisition · Adoption · Engagement · Advisory] ─▶ COMPLIANCE ─▶ act + audit
                └──────────────── shared Financial DNA · tools (MCP) · agentic RAG ───────────────┘
```

## Why it's built to actually ship in a bank
- **Governance is structural** — Compliance is a gate, not a guideline; nothing executes without a PASS.
- **Explainable & auditable** — every journey emits an immutable `Trace` (intent → plan → tool → RAG → compliance → outcome).
- **Human-in-the-loop** — low-confidence / high-value actions escalate instead of auto-firing.
- **Sovereign-ready** — LLM interface is pluggable; deploy on-prem / sovereign-cloud, PII minimised, purpose-bound consent ledger.

## Tech
`Multi-agent orchestration` (supervisor + specialists, framework-agnostic — LangGraph / OpenAI Agents SDK) · `LLM` (open-weight, on-prem capable) + Indic adapters · `Agentic RAG` (pgvector / Milvus) · `Tools` via MCP over core banking / UPI / CKYC · `Indic ASR/TTS` (15+ languages) · `FastAPI` · vanilla-JS demo.

## Repo layout
```
frontend/index.html          → live orchestration demo (offline, zero-dep)
backend/core.py              → Financial DNA, LLM interface, tools, Trace, Agent base
backend/agents/orchestrator.py → supervisor: classify · plan · route · compose
backend/agents/specialists.py  → Acquisition · Adoption · Engagement · Advisory · Compliance
backend/app.py               → CLI runner + optional FastAPI /journey endpoint
docs/architecture.md         → diagram, control flow, path to production
```

## Roadmap
**Now:** working multi-agent prototype (this repo) → **0–6 mo:** one-pillar sandbox pilot inside YONO with masked APIs & human-in-loop → **6–12 mo:** scale the fleet across pillars & 15 languages → **Vision:** Sarthi becomes YONO 3.0's agentic core — a proactive personal banker for every Indian.

<p align="center"><sub>Built for the SBI Hackathon @ Global Fintech Fest 2026 — advancing GFF's Agentic-AI pillar: from automation to autonomous intelligence.</sub></p>
