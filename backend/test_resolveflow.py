"""
Unit and integration tests for ResolveFlow backend.
Verifies all 11 simulated enterprise tools, ReAct workflow,
failure-induced replanning, policy enforcement, and database verification.
"""
import pytest
import asyncio
from database import init_db, get_db_connection
from seed import seed_database
from tools import (
    get_customer,
    get_order,
    get_inventory,
    search_policy,
    get_customer_history,
    create_replacement,
    issue_refund,
    cancel_order,
    create_store_credit,
    verify_resolution,
    escalate_to_human
)
from agent_engine import AgentEngine, create_agent_case

@pytest.fixture(autouse=True)
def setup_pristine_db():
    seed_database()

def test_tools_inspection():
    """Verify inspection tools return expected enterprise records."""
    # 1. get_customer
    cust = get_customer("CUST-101")
    assert cust["status"] == "SUCCESS"
    assert cust["data"]["name"] == "Sarah Jenkins"
    assert cust["data"]["tier"] == "VIP"

    # 2. get_order
    order = get_order("ORD-1042")
    assert order["status"] == "SUCCESS"
    assert order["data"]["product_name"] == "AuraPro Wireless ANC Headphones"
    assert order["data"]["total_amount"] == 249.99

    # 3. get_inventory
    inv = get_inventory("PROD-HEADPHONES-01")
    assert inv["status"] == "SUCCESS"
    assert inv["data"]["stock_quantity"] == 15
    assert inv["data"]["is_available"] is True

    inv_zero = get_inventory("PROD-MONITOR-4K")
    assert inv_zero["status"] == "SUCCESS"
    assert inv_zero["data"]["stock_quantity"] == 0
    assert inv_zero["data"]["is_available"] is False

    # 4. search_policy
    pol_valid = search_policy("damage_replacement", "ORD-1042")
    assert pol_valid["status"] == "SUCCESS"
    assert pol_valid["data"]["authorized"] is True

    pol_expired = search_policy("return_refund", "ORD-3341")
    assert pol_expired["status"] == "SUCCESS"
    assert pol_expired["data"]["authorized"] is False
    assert pol_expired["data"]["within_policy_window"] is False

    # 5. get_customer_history
    hist = get_customer_history("CUST-101")
    assert hist["status"] == "SUCCESS"
    assert len(hist["data"]["history_records"]) >= 2

def test_inventory_failure_and_replanning_action():
    """Verify that create_replacement fails when stock is 0 and requires replanning."""
    fail_rep = create_replacement("ORD-2089", "PROD-MONITOR-4K")
    assert fail_rep["status"] == "FAILURE"
    assert fail_rep["data"]["error"] == "INSUFFICIENT_INVENTORY"
    assert fail_rep["data"]["stock_quantity"] == 0
    assert fail_rep["data"]["action_required"] == "REPLAN_RESOLUTION"

def test_scenario_1_replacement_flow():
    """Scenario 1: Damaged item in stock -> Agent creates replacement and verifies."""
    case_id = create_agent_case("TCK-1042")
    engine = AgentEngine(case_id=case_id, ticket_id="TCK-1042")

    async def run():
        events = []
        async for ev in engine.execute_workflow(delay=0.001):
            events.append(ev)
        return events

    events = asyncio.run(run())
    assert engine.case_state["status"] == "Resolved"
    assert "Replacement" in engine.case_state["final_resolution"]
    assert engine.case_state["verification_badge"] is not None
    assert engine.case_state["verification_badge"]["verified"] is True
    assert engine.case_state["verification_badge"]["action_type"] == "REPLACEMENT_VERIFIED"

def test_scenario_2_replanning_flow():
    """Scenario 2: Damaged item out of stock -> Agent replans -> issues refund & store credit -> verifies."""
    case_id = create_agent_case("TCK-2089")
    engine = AgentEngine(case_id=case_id, ticket_id="TCK-2089")

    async def run():
        events = []
        async for ev in engine.execute_workflow(delay=0.001):
            events.append(ev)
        return events

    events = asyncio.run(run())
    assert engine.case_state["status"] == "Resolved"
    assert engine.case_state["replan_reason"] is not None
    assert "out of stock" in engine.case_state["replan_reason"].lower()
    assert any(step["step_type"] == "REPLANNING" for step in engine.steps)
    assert engine.case_state["verification_badge"]["verified"] is True
    assert engine.case_state["verification_badge"]["action_type"] == "REFUND_VERIFIED"

def test_scenario_3_policy_escalation_flow():
    """Scenario 3: Refund outside policy window -> Agent identifies policy conflict -> escalates to human."""
    case_id = create_agent_case("TCK-3341")
    engine = AgentEngine(case_id=case_id, ticket_id="TCK-3341")

    async def run():
        events = []
        async for ev in engine.execute_workflow(delay=0.001):
            events.append(ev)
        return events

    events = asyncio.run(run())
    assert engine.case_state["status"] == "Escalated"
    assert "escalated" in engine.case_state["final_resolution"].lower()
    assert any(step["tool_name"] == "escalate_to_human" for step in engine.steps)
    assert engine.case_state["verification_badge"]["verified"] is True
    assert engine.case_state["verification_badge"]["action_type"] == "ESCALATION_VERIFIED"

def test_scenario_4_cancellation_flow():
    """Scenario 4: Order cancellation before dispatch -> Agent cancels order, restocks inventory & verifies."""
    case_id = create_agent_case("TCK-4510")
    engine = AgentEngine(case_id=case_id, ticket_id="TCK-4510")

    async def run():
        events = []
        async for ev in engine.execute_workflow(delay=0.001):
            events.append(ev)
        return events

    events = asyncio.run(run())
    assert engine.case_state["status"] == "Resolved"
    assert "cancelled" in engine.case_state["final_resolution"].lower()
    assert any(step["tool_name"] == "cancel_order" for step in engine.steps)
    assert engine.case_state["verification_badge"]["verified"] is True
    assert engine.case_state["verification_badge"]["action_type"] == "ORDER_CANCELLATION_VERIFIED"

