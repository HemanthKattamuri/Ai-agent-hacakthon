"""
FastAPI application for ResolveFlow — Autonomous Customer Resolution Agent.
Provides REST and Server-Sent Events (SSE) streaming endpoints.
"""
import json
import sys
from pathlib import Path

# Ensure backend directory is in python search path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database import init_db, get_db_connection
from seed import seed_database
from tools import TOOL_REGISTRY
from agent_engine import AgentEngine, create_agent_case
from models import (
    RunAgentRequest, CustomTicketRequest, PolicyOverrideRequest,
    InventoryUpdateRequest, AuthLoginRequest, AuthRegisterRequest
)

app = FastAPI(
    title="ResolveFlow API",
    description="Autonomous Customer Resolution Agent API with ReAct execution and live replanning",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {
        "name": "ResolveFlow — Autonomous Customer Resolution Agent API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/api/tickets")
def get_tickets():
    """List all demo tickets with customer and order metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.*,
            c.name as customer_name,
            c.email as customer_email,
            c.tier as customer_tier,
            c.trust_score,
            o.product_id,
            p.name as product_name,
            o.total_amount,
            o.delivery_date,
            o.status as order_status
        FROM tickets t
        LEFT JOIN customers c ON t.customer_id = c.id
        LEFT JOIN orders o ON t.order_id = o.id
        LEFT JOIN products p ON o.product_id = p.id
        ORDER BY t.created_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    """Retrieve detailed information for a single ticket."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.*,
            c.name as customer_name,
            c.email as customer_email,
            c.tier as customer_tier,
            c.trust_score,
            c.total_spend,
            o.product_id,
            p.name as product_name,
            p.stock_quantity as product_stock,
            o.total_amount,
            o.order_date,
            o.delivery_date,
            o.status as order_status,
            o.tracking_number as order_tracking
        FROM tickets t
        LEFT JOIN customers c ON t.customer_id = c.id
        LEFT JOIN orders o ON t.order_id = o.id
        LEFT JOIN products p ON o.product_id = p.id
        WHERE t.id = ?
    """, (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")
    return dict(row)

@app.post("/api/tickets/custom")
def create_custom_ticket(req: CustomTicketRequest):
    """Create a user-defined scenario ticket for sandbox testing."""
    import uuid
    from datetime import datetime, timezone
    conn = get_db_connection()
    cursor = conn.cursor()
    
    ticket_num = len(cursor.execute("SELECT id FROM tickets").fetchall()) + 1
    ticket_id = f"TCK-CUSTOM-{ticket_num:03d}"
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO tickets (id, ticket_code, customer_id, order_id, title, message, issue_type, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
    """, (
        ticket_id, ticket_id, req.customer_id, req.order_id,
        req.title, req.message, req.issue_type, req.priority, created_at
    ))
    conn.commit()
    conn.close()
    return {"message": "Custom scenario ticket created successfully", "ticket_id": ticket_id}

@app.post("/api/agent/start")
def start_case(req: RunAgentRequest):
    """Initialize a case record and return the case_id for SSE stream attachment."""
    case_id = create_agent_case(req.ticket_id)
    return {"case_id": case_id, "ticket_id": req.ticket_id}

@app.get("/api/agent/stream/{case_id}")
async def stream_agent_execution(
    case_id: str,
    ticket_id: str = Query(...),
    speed: float = Query(0.5, ge=0.01, le=2.0)
):
    """
    Server-Sent Events (SSE) stream endpoint for real-time ReAct loop reasoning.
    Streams individual decision steps, tool executions, replanning triggers, and DB verifications.
    """
    engine = AgentEngine(case_id=case_id, ticket_id=ticket_id)

    async def event_generator():
        try:
            async for event_payload in engine.execute_workflow(delay=speed):
                yield f"data: {json.dumps(event_payload)}\n\n"
            yield f"data: {json.dumps({'event': 'DONE', 'case_state': engine.case_state})}\n\n"
        except Exception as e:
            err_payload = {
                "event": "ERROR",
                "error": str(e),
                "case_state": engine.case_state
            }
            yield f"data: {json.dumps(err_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/tools/logs/{case_id}")
def get_tool_logs(case_id: str):
    """Retrieve audit tool execution logs for a case."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tool_call_logs 
        WHERE case_id = ? 
        ORDER BY timestamp ASC
    """, (case_id,))
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        d = dict(r)
        d["input_params"] = json.loads(d["input_params"]) if d["input_params"] else {}
        d["result"] = json.loads(d["result"]) if d["result"] else {}
        logs.append(d)
    return logs

@app.get("/api/tools/registry")
def get_tools_registry():
    """List all 11 enterprise tools in the tool registry."""
    return [
        {
            "name": name,
            "description": doc.get("description", ""),
            "params": doc.get("params", {})
        }
        for name, doc in TOOL_REGISTRY.items()
    ]

@app.get("/api/db/overview")
def get_db_overview():
    """Live Enterprise Database Table Inspector."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    products = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT o.*, c.name as customer_name, p.name as product_name 
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN products p ON o.product_id = p.id
        ORDER BY o.id ASC
    """)
    orders = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT r.*, p.name as product_name
        FROM replacements r
        JOIN products p ON r.product_id = p.id
        ORDER BY r.timestamp DESC
    """)
    replacements = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT rf.*, c.name as customer_name
        FROM refunds rf
        JOIN customers c ON rf.customer_id = c.id
        ORDER BY rf.timestamp DESC
    """)
    refunds = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT sc.*, c.name as customer_name
        FROM store_credits sc
        JOIN customers c ON sc.customer_id = c.id
        ORDER BY sc.timestamp DESC
    """)
    store_credits = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT esc.*, t.title as ticket_title
        FROM escalations esc
        JOIN tickets t ON esc.ticket_id = t.id
        ORDER BY esc.timestamp DESC
    """)
    escalations = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM policies ORDER BY id ASC")
    policies = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "products": products,
        "orders": orders,
        "replacements": replacements,
        "refunds": refunds,
        "store_credits": store_credits,
        "escalations": escalations,
        "policies": policies
    }

@app.post("/api/policy/update")
def update_policy(req: PolicyOverrideRequest):
    """Sandbox: Dynamically override policy rules for live stress testing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies WHERE category = ?", (req.category,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Policy category '{req.category}' not found")

    cursor.execute("""
        UPDATE policies
        SET rules_json = ?
        WHERE category = ?
    """, (json.dumps(req.rules), req.category))
    conn.commit()
    conn.close()
    return {"message": f"Policy '{req.category}' updated successfully", "rules": req.rules}

@app.post("/api/inventory/update")
def update_inventory(req: InventoryUpdateRequest):
    """Sandbox: Dynamically alter product stock level to induce or prevent replanning."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?", (req.product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Product '{req.product_id}' not found")

    cursor.execute("""
        UPDATE products
        SET stock_quantity = ?
        WHERE id = ?
    """, (req.stock_quantity, req.product_id))
    conn.commit()
    conn.close()
    return {"message": f"Product '{req.product_id}' stock updated to {req.stock_quantity}"}

@app.post("/api/demo/reset")
def reset_demo_data():
    """Reset the SQLite database to seeded initial state."""
    seed_database()
    return {"message": "ResolveFlow database reset to clean seeded state successfully."}

@app.get("/api/auth/operators")
def list_operators():
    """List registered security operators for fast login switching."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, department, clearance_level, avatar_color, last_login FROM operators")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"operators": rows}

@app.post("/api/auth/login")
def auth_login(req: AuthLoginRequest):
    """Authenticate operator and return security clearance token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE email = ?", (req.email.strip().lower(),))
    row = cursor.fetchone()
    if not row:
        # Fallback to create dynamic session
        name = req.email.split("@")[0].replace(".", " ").title()
        cursor.execute("""
            INSERT OR REPLACE INTO operators (id, name, email, role, department, clearance_level, avatar_color, last_login)
            VALUES (?, ?, ?, 'AGENT_OPERATOR', 'AI Operations', 'Tier-2 Operator', '#6366f1', datetime('now'))
        """, (f"OP-{abs(hash(req.email)) % 1000:03d}", name, req.email.strip().lower()))
        conn.commit()
        cursor.execute("SELECT * FROM operators WHERE email = ?", (req.email.strip().lower(),))
        row = cursor.fetchone()

    operator = dict(row)
    cursor.execute("UPDATE operators SET last_login = datetime('now') WHERE id = ?", (operator["id"],))
    conn.commit()
    conn.close()

    return {
        "status": "SUCCESS",
        "token": f"jwt-sec-{operator['id']}-live",
        "operator": operator
    }

@app.post("/api/auth/register")
def auth_register(req: AuthRegisterRequest):
    """Register a new enterprise operator with custom clearance and profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    op_id = f"OP-{abs(hash(req.email)) % 900 + 100:03d}"
    colors = ["#6366f1", "#06b6d4", "#a855f7", "#10b981", "#f59e0b"]
    avatar_color = colors[abs(hash(req.name)) % len(colors)]
    
    cursor.execute("""
        INSERT OR REPLACE INTO operators (id, name, email, role, department, clearance_level, avatar_color, last_login)
        VALUES (?, ?, ?, ?, ?, 'Tier-2 Verified', ?, datetime('now'))
    """, (op_id, req.name, req.email.strip().lower(), req.role or 'AGENT_OPERATOR', req.department or 'AI Operations', avatar_color))
    conn.commit()
    cursor.execute("SELECT * FROM operators WHERE id = ?", (op_id,))
    operator = dict(cursor.fetchone())
    conn.close()

    return {
        "status": "SUCCESS",
        "token": f"jwt-sec-{operator['id']}-live",
        "operator": operator
    }

