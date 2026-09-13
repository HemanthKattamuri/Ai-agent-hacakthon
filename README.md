# 🤖 ResolveFlow — Autonomous Customer Resolution Agent

> **ResolveFlow** is an enterprise-grade autonomous AI customer resolution agent that executes end-to-end multi-step issue investigations, enforces return/replacement policies, handles out-of-stock replanning, interacts with database records across 11 simulated enterprise tools, and streams real-time ReAct thoughts and tool actions over Server-Sent Events (SSE).

---

## 🌟 Key Features

### 1. 🧠 Dynamic ReAct Agent Architecture
- **Reason + Act Loop**: Formulates step-by-step reasoning (`THOUGHT`), selects and executes tools (`ACTION`), inspects outputs (`OBSERVATION`), and arrives at certified resolutions (`RESOLUTION`).
- **Autonomous Replanning**: When an initial resolution path fails (e.g., warehouse inventory is out-of-stock), the agent detects the bottleneck, replans on the fly, and routes to alternative remediation paths (such as full refunds + goodwill VIP store credit).
- **Policy Enforcement**: Automatically checks warranty timeframes, delivery dates, and return windows. Out-of-policy requests are escalated to human supervisors with structured rationale.
- **Cryptographic Verification**: Every completed resolution generates a SHA-256 integrity verification badge tying the ticket, order, action, and timestamp.

### 2. 🛠️ 11 Enterprise Simulated Tools
1. `get_customer(customer_id)` — Inspect customer profile, tier (Standard/VIP), and lifetime value.
2. `get_order(order_id)` — Retrieve order details, line items, timestamps, and status.
3. `get_inventory(sku)` — Check live warehouse inventory and reserve units.
4. `search_policy(issue_type, order_id)` — Evaluate enterprise policy windows (returns, replacements, cancellations).
5. `get_customer_history(customer_id)` — Query lifetime ticket resolution history and fraud indicators.
6. `create_replacement(order_id, sku, address)` — Place zero-cost replacement shipments and decrement warehouse stock.
7. `issue_refund(order_id, amount, reason)` — Issue partial or 100% payments refunds.
8. `cancel_order(order_id, reason)` — Cancel pending/processing orders and restock reserved items.
9. `create_store_credit(customer_id, amount, reason)` — Issue promotional or goodwill credits to customer accounts.
10. `verify_resolution(ticket_id, action_type, metadata)` — Perform cryptographic safety assertion and seal case.
11. `escalate_to_human(ticket_id, reason, priority)` — Flag edge cases and policy violations to Tier 2 human teams.

### 3. 🖥️ Interactive Web Station (`index.html`)
- **Single Unified Frontend**: All UI components, ReAct timeline, live DB inspector, scenario switcher, interactive policy sandbox, and verification modals in a standalone responsive single-page application.
- **Real-Time Live Timeline**: Watch the agent stream live thoughts, tool executions, parameter inspections, and payload responses via SSE (`/api/agent/stream/{case_id}`).
- **Interactive Database Inspector**: View and query the 11 SQLite enterprise tables in real time as actions are committed.
- **Policy Sandbox**: Adjust policy constraints (e.g. 30-day window, VIP credits) and test real-time agent reactions.
- **Interactive Scenario Hub**: 4 pre-configured enterprise benchmark scenarios (`TCK-1042`, `TCK-2089`, `TCK-3341`, `TCK-4510`).

---

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.10+
- Modern Web Browser

### 1-Command All-in-One Launch
```bash
./run.sh
```
*Sets up Python virtualenv, installs backend packages, initializes the SQLite database with benchmark scenarios, and runs both servers concurrently!*

- **Website Station**: `http://localhost:5173` (or open `index.html` directly)
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

### Manual Execution

#### 1. Setup & Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/seed.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Open Frontend
Open `index.html` in your web browser or serve it with:
```bash
python3 -m http.server 5173
```

---

## 🧪 Automated Test Suite

Run the full pytest suite verifying all 11 enterprise tools, ReAct engine flows, replanning, and policy guardrails:

```bash
./.venv/bin/pytest backend/test_resolveflow.py -v
```

---

## 🏛️ System Architecture

```
resolveflow/
├── backend/
│   ├── database.py         # SQLite schema & foreign key connections (11 enterprise tables)
│   ├── tools.py            # 11 simulated enterprise tools with latency simulation
│   ├── agent_engine.py     # ReAct reasoning loop, tool dispatcher, SSE event generator
│   ├── models.py           # Pydantic validation schemas
│   ├── seed.py             # 4 benchmark test scenarios & enterprise sample data
│   ├── main.py             # FastAPI REST endpoints & SSE streaming router
│   └── test_resolveflow.py # Full pytest verification suite (6 automated tests)
├── index.html              # Standalone ResolveFlow Single-Page Application (HTML/CSS/JS)
├── run.sh                  # All-in-one launcher script
└── README.md               # Project documentation
```
