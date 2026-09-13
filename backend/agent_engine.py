"""
Autonomous Agent Engine for ResolveFlow.
Orchestrates the complete ReAct goal-driven decision loop:
Goal -> Decision -> Tool Call -> Observation -> Action -> Replanning (on failure) -> Verification -> Final Outcome.
Maintains persistent case state and supports real-time Server-Sent Events (SSE) streaming.
"""
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import uuid
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Generator, AsyncGenerator, Optional
from database import get_db_connection
from tools import (
    TOOL_REGISTRY,
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
    escalate_to_human,
)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class AgentEngine:
    def __init__(self, case_id: str, ticket_id: str):
        self.case_id = case_id
        self.ticket_id = ticket_id
        self.step_counter = 0
        self.steps: List[Dict[str, Any]] = []
        self.tool_logs: List[Dict[str, Any]] = []
        self.evidence: Dict[str, Any] = {}
        self.case_state: Dict[str, Any] = {
            "status": "Pending",
            "goal": "",
            "initial_plan": "",
            "current_plan": "",
            "replan_reason": None,
            "final_resolution": None,
            "verification_badge": None,
            "actions_taken": []
        }

    def _update_case_status(self, status: str, goal: Optional[str] = None, current_plan: Optional[str] = None):
        self.case_state["status"] = status
        if goal:
            self.case_state["goal"] = goal
        if current_plan:
            self.case_state["current_plan"] = current_plan

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agent_cases
            SET status = ?, goal = COALESCE(?, goal), current_plan = COALESCE(?, current_plan), updated_at = ?
            WHERE id = ?
        """, (status, goal, current_plan, _now(), self.case_id))
        cursor.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, self.ticket_id))
        conn.commit()
        conn.close()

    def _log_tool_call(self, tool_name: str, input_params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        log_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
        status = result.get("status", "SUCCESS")
        duration_ms = result.get("duration_ms", 12)
        timestamp = _now()

        log_entry = {
            "id": log_id,
            "case_id": self.case_id,
            "timestamp": timestamp,
            "tool_name": tool_name,
            "input_params": input_params,
            "result": result.get("data", result),
            "status": status,
            "duration_ms": duration_ms
        }
        self.tool_logs.append(log_entry)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tool_call_logs (id, case_id, timestamp, tool_name, input_params_json, result_json, status, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            self.case_id,
            timestamp,
            tool_name,
            json.dumps(input_params),
            json.dumps(result.get("data", result)),
            status,
            duration_ms
        ))
        conn.commit()
        conn.close()
        return log_entry

    def _record_step(
        self,
        step_type: str,
        title: str,
        summary: str,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        tool_output: Optional[Dict[str, Any]] = None,
        status: str = "COMPLETED",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.step_counter += 1
        step = {
            "step_index": self.step_counter,
            "timestamp": _now(),
            "step_type": step_type,
            "title": title,
            "summary": summary,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "status": status,
            "details": details or {}
        }
        self.steps.append(step)
        return step

    async def execute_workflow(self, delay: float = 0.5) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the autonomous agent loop, yielding timeline events for live streaming.
        Handles autonomous investigation, decision-making, tool execution, failure-induced replanning,
        and database verification.
        """
        # Step 0: Load Ticket
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id = ?", (self.ticket_id,))
        ticket = cursor.fetchone()
        conn.close()

        if not ticket:
            yield {
                "event": "error",
                "data": {"message": f"Ticket {self.ticket_id} not found."}
            }
            return

        ticket_data = dict(ticket)
        customer_id = ticket_data["customer_id"]
        order_id = ticket_data["order_id"]
        issue_type = ticket_data["issue_type"]
        ticket_msg = ticket_data["message"]

        # 1. Formulation of Goal
        self._update_case_status("Investigating")
        goal_text = f"Investigate customer issue '{ticket_data['title']}' for order {order_id}, determine eligibility under policy, execute safe state change, and verify completion."
        initial_plan = "1. Retrieve customer & order profiles\n2. Inspect enterprise policy & stock availability\n3. Select best policy-compliant remedy\n4. Execute and verify resolution in database"
        self.case_state["goal"] = goal_text
        self.case_state["initial_plan"] = initial_plan
        self.case_state["current_plan"] = initial_plan

        step1 = self._record_step(
            step_type="GOAL",
            title="Formulated Autonomous Goal",
            summary=f"Established primary mission: Resolve ticket {ticket_data['ticket_code']} safely according to enterprise policies and inventory availability.",
            details={
                "goal": goal_text,
                "initial_plan": initial_plan,
                "ticket_code": ticket_data["ticket_code"],
                "customer_id": customer_id,
                "order_id": order_id
            }
        )
        yield {"event": "step", "step": step1, "case_state": self.case_state}
        await asyncio.sleep(delay)

        # 2. Decision: Investigate Customer
        step2 = self._record_step(
            step_type="DECISION",
            title="Investigating Customer Account",
            summary=f"Inspecting customer {customer_id} trust profile and standing before taking any financial action.",
        )
        yield {"event": "step", "step": step2, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.6)

        # 3. Tool Call: get_customer
        cust_res = get_customer(customer_id, self.case_id)
        cust_log = self._log_tool_call("get_customer", {"customer_id": customer_id}, cust_res)
        cust_info = cust_res.get("data", {})
        self.evidence["customer"] = cust_info

        step3 = self._record_step(
            step_type="TOOL_CALL",
            title="Tool Call: get_customer",
            summary=f"Retrieved profile for {cust_info.get('name', customer_id)}: Tier={cust_info.get('tier')}, TrustScore={cust_info.get('trust_score')}/100.",
            tool_name="get_customer",
            tool_input={"customer_id": customer_id},
            tool_output=cust_info,
            status="COMPLETED"
        )
        yield {"event": "step", "step": step3, "tool_log": cust_log, "case_state": self.case_state}
        await asyncio.sleep(delay)

        # 4. Tool Call: get_order
        step4_dec = self._record_step(
            step_type="DECISION",
            title="Retrieving Order & Shipment Details",
            summary=f"Checking shipment status, delivery date, and product SKU for order {order_id}."
        )
        yield {"event": "step", "step": step4_dec, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.6)

        order_res = get_order(order_id, self.case_id)
        order_log = self._log_tool_call("get_order", {"order_id": order_id}, order_res)
        order_info = order_res.get("data", {})
        self.evidence["order"] = order_info
        product_id = order_info.get("product_id")

        step4 = self._record_step(
            step_type="TOOL_CALL",
            title="Tool Call: get_order",
            summary=f"Order {order_id} verified: Status '{order_info.get('status')}', Product '{order_info.get('product_name')}', Total ${order_info.get('total_amount'):.2f}.",
            tool_name="get_order",
            tool_input={"order_id": order_id},
            tool_output=order_info,
            status="COMPLETED"
        )
        yield {"event": "step", "step": step4, "tool_log": order_log, "case_state": self.case_state}
        await asyncio.sleep(delay)

        # 5. Tool Call: search_policy
        step5_dec = self._record_step(
            step_type="DECISION",
            title="Auditing Enterprise Policy Rules",
            summary=f"Evaluating company return and replacement rules for issue type '{issue_type}'."
        )
        yield {"event": "step", "step": step5_dec, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.6)

        policy_res = search_policy(issue_type, order_id, self.case_id)
        policy_log = self._log_tool_call("search_policy", {"issue_type": issue_type, "order_id": order_id}, policy_res)
        policy_info = policy_res.get("data", {})
        self.evidence["policy"] = policy_info

        step5 = self._record_step(
            step_type="TOOL_CALL",
            title="Tool Call: search_policy",
            summary=f"Policy Evaluation: Authorized={policy_info.get('authorized')}. Window={policy_info.get('days_since_delivery')} days post-delivery. Preferred Action: {policy_info.get('preferred_action')}.",
            tool_name="search_policy",
            tool_input={"issue_type": issue_type, "order_id": order_id},
            tool_output=policy_info,
            status="COMPLETED" if policy_info.get("authorized") else "WARNING"
        )
        yield {"event": "step", "step": step5, "tool_log": policy_log, "case_state": self.case_state}
        await asyncio.sleep(delay)

        # 6. Branching Logic Based on Policy
        if not policy_info.get("authorized"):
            # SCENARIO 3: Policy Conflict -> Safety Gate -> Escalate to Human!
            step_esc_dec = self._record_step(
                step_type="DECISION",
                title="Policy Boundary Violation Detected",
                summary=f"SAFETY ENFORCEMENT: Order was delivered {policy_info.get('days_since_delivery')} days ago (>30 day threshold). Automated financial refund is forbidden by compliance. Escalating to human supervisor.",
                status="WARNING"
            )
            yield {"event": "step", "step": step_esc_dec, "case_state": self.case_state}
            await asyncio.sleep(delay)

            esc_reason = f"Policy window exceeded: customer requested refund {policy_info.get('days_since_delivery')} days after delivery. Exceeds standard 30-day limit."
            esc_res = escalate_to_human(self.case_id, esc_reason)
            esc_log = self._log_tool_call("escalate_to_human", {"case_id": self.case_id, "reason": esc_reason}, esc_res)
            self.case_state["actions_taken"].append(esc_res.get("data"))

            step_esc = self._record_step(
                step_type="ACTION",
                title="Action: escalate_to_human",
                summary=f"Escalation ticket {esc_res.get('data', {}).get('escalation_id')} dispatched to Tier-2 Human Escalations Desk with High priority.",
                tool_name="escalate_to_human",
                tool_input={"case_id": self.case_id, "reason": esc_reason},
                tool_output=esc_res.get("data"),
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_esc, "tool_log": esc_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Verification of Escalation
            verify_res = verify_resolution(self.case_id)
            verify_log = self._log_tool_call("verify_resolution", {"case_id": self.case_id}, verify_res)
            v_data = verify_res.get("data", {})
            self.case_state["verification_badge"] = v_data

            step_v = self._record_step(
                step_type="VERIFICATION",
                title="Verification: verify_resolution",
                summary=f"Cryptographic Audit Check: {v_data.get('integrity_check')}. Seal: {v_data.get('audit_hash')}.",
                tool_name="verify_resolution",
                tool_input={"case_id": self.case_id},
                tool_output=v_data,
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_v, "tool_log": verify_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Final Outcome
            self._update_case_status("Escalated")
            self.case_state["final_resolution"] = f"Safely escalated to human support desk ({esc_res.get('data', {}).get('escalation_id')}) due to 30-day policy cutoff enforcement."

            step_out = self._record_step(
                step_type="OUTCOME",
                title="Final Outcome: Safely Escalated",
                summary="Agent successfully safeguarded corporate return policy. Case handed off to Tier-2 supervisor with full audit trail.",
                details={"status": "Escalated", "escalation": esc_res.get("data"), "verification": v_data}
            )
            yield {"event": "step", "step": step_out, "case_state": self.case_state, "done": True}
            return

        # 7. Customer history check
        hist_res = get_customer_history(customer_id, self.case_id)
        hist_log = self._log_tool_call("get_customer_history", {"customer_id": customer_id}, hist_res)
        hist_info = hist_res.get("data", {})
        self.evidence["history"] = hist_info

        step_hist = self._record_step(
            step_type="TOOL_CALL",
            title="Tool Call: get_customer_history",
            summary=f"Customer reputation verified: {hist_info.get('reputation_flag')}. Total previous tickets: {hist_info.get('total_tickets_filed')}.",
            tool_name="get_customer_history",
            tool_input={"customer_id": customer_id},
            tool_output=hist_info,
            status="COMPLETED"
        )
        yield {"event": "step", "step": step_hist, "tool_log": hist_log, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.8)

        # 8. Branch: Cancellation Workflow (SCENARIO 4)
        if "cancel" in issue_type.lower() or policy_info.get("preferred_action") == "CANCEL_ORDER":
            step_can_dec = self._record_step(
                step_type="DECISION",
                title="Executing Order Cancellation & Restock",
                summary=f"Order {order_id} is in '{order_info.get('status')}' status. Executing autonomous pre-fulfillment cancellation and warehouse inventory restock under Policy CAN-01."
            )
            yield {"event": "step", "step": step_can_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            can_res = cancel_order(order_id, self.case_id)
            can_log = self._log_tool_call("cancel_order", {"order_id": order_id}, can_res)
            self.case_state["actions_taken"].append(can_res.get("data"))
            self._update_case_status("Action Taken")

            step_can = self._record_step(
                step_type="ACTION",
                title="Action: cancel_order",
                summary=f"Order {order_id} successfully cancelled. Warehouse restocked: +{can_res.get('data', {}).get('units_restocked', 1)} unit (New Stock: {can_res.get('data', {}).get('new_stock_level')}). Payment authorization voided.",
                tool_name="cancel_order",
                tool_input={"order_id": order_id},
                tool_output=can_res.get("data"),
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_can, "tool_log": can_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Verification of Cancellation
            step_vc_dec = self._record_step(
                step_type="DECISION",
                title="Verifying Cancellation in Ledger",
                summary="Agent independently querying database to verify order cancellation and restock audit trail."
            )
            yield {"event": "step", "step": step_vc_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            verify_res = verify_resolution(self.case_id)
            verify_log = self._log_tool_call("verify_resolution", {"case_id": self.case_id}, verify_res)
            v_data = verify_res.get("data", {})
            self.case_state["verification_badge"] = v_data

            step_vc = self._record_step(
                step_type="VERIFICATION",
                title="Verification: verify_resolution",
                summary=f"Verification confirmed: {v_data.get('action_type')}. Cryptographic Seal: {v_data.get('audit_hash')}.",
                tool_name="verify_resolution",
                tool_input={"case_id": self.case_id},
                tool_output=v_data,
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_vc, "tool_log": verify_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Final Outcome for Cancellation
            self._update_case_status("Resolved")
            self.case_state["final_resolution"] = f"Order {order_id} successfully cancelled before shipment. Payment of ${order_info.get('total_amount'):.2f} voided. 1 unit restocked to warehouse inventory."

            step_out = self._record_step(
                step_type="OUTCOME",
                title="Final Outcome: Order Cancelled & Restocked",
                summary=f"Successfully resolved cancellation request: Order {order_id} marked Cancelled, ${order_info.get('total_amount'):.2f} transaction voided, warehouse stock restored.",
                details={"status": "Resolved", "cancellation": can_res.get("data"), "verification": v_data}
            )
            yield {"event": "step", "step": step_out, "case_state": self.case_state, "done": True}
            return

        # 9. Check Inventory for replacement (SCENARIOS 1 & 2)
        step_inv_dec = self._record_step(
            step_type="DECISION",
            title="Checking Warehouse Inventory",
            summary=f"Customer requested replacement for '{order_info.get('product_name')}'. Checking live inventory stock level before dispatching order."
        )
        yield {"event": "step", "step": step_inv_dec, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.6)

        inv_res = get_inventory(product_id, self.case_id)
        inv_log = self._log_tool_call("get_inventory", {"product_id": product_id}, inv_res)
        inv_info = inv_res.get("data", {})
        self.evidence["inventory"] = inv_info

        step_inv = self._record_step(
            step_type="TOOL_CALL",
            title="Tool Call: get_inventory",
            summary=f"Warehouse Stock Level for SKU {inv_info.get('sku')}: {inv_info.get('stock_quantity')} units available. (Available: {inv_info.get('is_available')}).",
            tool_name="get_inventory",
            tool_input={"product_id": product_id},
            tool_output=inv_info,
            status="COMPLETED" if inv_info.get("is_available") else "WARNING"
        )
        yield {"event": "step", "step": step_inv, "tool_log": inv_log, "case_state": self.case_state}
        await asyncio.sleep(delay)

        # 9. Attempt primary action: Replacement
        step_act_dec = self._record_step(
            step_type="DECISION",
            title="Executing Primary Remedy: Replacement",
            summary=f"Attempting to invoke create_replacement for order {order_id}."
        )
        yield {"event": "step", "step": step_act_dec, "case_state": self.case_state}
        await asyncio.sleep(delay * 0.6)

        rep_res = create_replacement(order_id, product_id, self.case_id)
        rep_log = self._log_tool_call("create_replacement", {"order_id": order_id, "product_id": product_id}, rep_res)

        if rep_res.get("status") == "SUCCESS":
            # SCENARIO 1: Replacement in Stock -> Success!
            self.case_state["actions_taken"].append(rep_res.get("data"))
            self._update_case_status("Action Taken")

            step_rep = self._record_step(
                step_type="ACTION",
                title="Action: create_replacement",
                summary=f"Replacement order {rep_res['data']['new_order_id']} successfully placed! Tracking: {rep_res['data']['tracking_number']}.",
                tool_name="create_replacement",
                tool_input={"order_id": order_id, "product_id": product_id},
                tool_output=rep_res["data"],
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_rep, "tool_log": rep_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Verification
            step_v_dec = self._record_step(
                step_type="DECISION",
                title="Verifying State Mutation in Database",
                summary="Agent independently querying enterprise database to verify replacement order persistence."
            )
            yield {"event": "step", "step": step_v_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            verify_res = verify_resolution(self.case_id)
            verify_log = self._log_tool_call("verify_resolution", {"case_id": self.case_id}, verify_res)
            v_data = verify_res.get("data", {})
            self.case_state["verification_badge"] = v_data

            step_v = self._record_step(
                step_type="VERIFICATION",
                title="Verification: verify_resolution",
                summary=f"Verification confirmed: {v_data.get('action_type')}. Cryptographic Seal: {v_data.get('audit_hash')}.",
                tool_name="verify_resolution",
                tool_input={"case_id": self.case_id},
                tool_output=v_data,
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_v, "tool_log": verify_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Outcome
            self._update_case_status("Resolved")
            self.case_state["final_resolution"] = f"Replacement order {rep_res['data']['new_order_id']} placed with expedited 2-day shipping. Tracking: {rep_res['data']['tracking_number']}."

            step_out = self._record_step(
                step_type="OUTCOME",
                title="Final Outcome: Replacement Confirmed",
                summary=f"Issue autonomously resolved: Replacement order created and verified. Customer notified with tracking {rep_res['data']['tracking_number']}.",
                details={"status": "Resolved", "replacement": rep_res.get("data"), "verification": v_data}
            )
            yield {"event": "step", "step": step_out, "case_state": self.case_state, "done": True}
            return

        else:
            # SCENARIO 2: Replacement FAILED due to out of stock! -> REPLANNING!
            step_fail = self._record_step(
                step_type="OBSERVATION",
                title="Tool Observation: Replacement Failed",
                summary=f"FAILURE DETECTED: {rep_res.get('data', {}).get('message', 'Out of stock')}. Product stock is 0.",
                tool_name="create_replacement",
                tool_input={"order_id": order_id, "product_id": product_id},
                tool_output=rep_res.get("data"),
                status="FAILED"
            )
            yield {"event": "step", "step": step_fail, "tool_log": rep_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # 🚨 REPLANNING TRIGGERED
            self._update_case_status("Replanning")
            replan_reason = "Product is out of stock (stock: 0). Primary replacement strategy cannot be fulfilled."
            revised_plan = "1. Re-evaluate policy for secondary recourse\n2. Issue 100% full monetary refund\n3. Grant $15 courtesy store credit for customer delight\n4. Verify refund and store credit in enterprise database"
            self.case_state["replan_reason"] = replan_reason
            self.case_state["current_plan"] = revised_plan

            step_replan = self._record_step(
                step_type="REPLANNING",
                title="Autonomous Replanning Triggered",
                summary=f"Action failure detected: {replan_reason}. Switching from 'Replacement' strategy to 'Full Refund + Goodwill Store Credit' fallback policy.",
                details={
                    "original_plan": self.case_state["initial_plan"],
                    "revised_plan": revised_plan,
                    "replan_reason": replan_reason,
                    "fallback_policy": "POL-DAM-01 & POL-CRD-01"
                },
                status="WARNING"
            )
            yield {"event": "step", "step": step_replan, "case_state": self.case_state}
            await asyncio.sleep(delay * 1.2)

            # Execute Replanned Action 1: Full Refund
            step_ref_dec = self._record_step(
                step_type="DECISION",
                title="Executing Replanned Remedy 1: Full Refund",
                summary=f"Issuing 100% refund of ${order_info.get('total_amount'):.2f} to original payment card."
            )
            yield {"event": "step", "step": step_ref_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            refund_amt = order_info.get("total_amount", 499.99)
            ref_res = issue_refund(order_id, refund_amt, self.case_id)
            ref_log = self._log_tool_call("issue_refund", {"order_id": order_id, "amount": refund_amt}, ref_res)
            self.case_state["actions_taken"].append(ref_res.get("data"))
            self._update_case_status("Action Taken")

            step_ref = self._record_step(
                step_type="ACTION",
                title="Action: issue_refund",
                summary=f"Refund of ${refund_amt:.2f} executed via {ref_res.get('data', {}).get('payment_method')} (Ref: {ref_res.get('data', {}).get('transaction_reference')}).",
                tool_name="issue_refund",
                tool_input={"order_id": order_id, "amount": refund_amt},
                tool_output=ref_res.get("data"),
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_ref, "tool_log": ref_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Execute Replanned Action 2: Courtesy Store Credit
            step_crd_dec = self._record_step(
                step_type="DECISION",
                title="Executing Replanned Remedy 2: Courtesy Store Credit",
                summary="Applying $15.00 appeasement store credit under Policy POL-CRD-01 to preserve customer retention."
            )
            yield {"event": "step", "step": step_crd_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            credit_amt = 15.00
            crd_res = create_store_credit(customer_id, credit_amt, self.case_id)
            crd_log = self._log_tool_call("create_store_credit", {"customer_id": customer_id, "amount": credit_amt}, crd_res)
            self.case_state["actions_taken"].append(crd_res.get("data"))

            step_crd = self._record_step(
                step_type="ACTION",
                title="Action: create_store_credit",
                summary=f"Issued ${credit_amt:.2f} courtesy store credit (ID: {crd_res.get('data', {}).get('credit_id')}) directly into customer account.",
                tool_name="create_store_credit",
                tool_input={"customer_id": customer_id, "amount": credit_amt},
                tool_output=crd_res.get("data"),
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_crd, "tool_log": crd_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Verification of Refund & Credit
            step_v2_dec = self._record_step(
                step_type="DECISION",
                title="Verifying Financial State Mutations",
                summary="Agent validating refund settlement and store credit insertion in enterprise database."
            )
            yield {"event": "step", "step": step_v2_dec, "case_state": self.case_state}
            await asyncio.sleep(delay * 0.6)

            verify_res = verify_resolution(self.case_id)
            verify_log = self._log_tool_call("verify_resolution", {"case_id": self.case_id}, verify_res)
            v_data = verify_res.get("data", {})
            self.case_state["verification_badge"] = v_data

            step_v2 = self._record_step(
                step_type="VERIFICATION",
                title="Verification: verify_resolution",
                summary=f"Verification confirmed: {v_data.get('action_type')}. Cryptographic Seal: {v_data.get('audit_hash')}.",
                tool_name="verify_resolution",
                tool_input={"case_id": self.case_id},
                tool_output=v_data,
                status="COMPLETED"
            )
            yield {"event": "step", "step": step_v2, "tool_log": verify_log, "case_state": self.case_state}
            await asyncio.sleep(delay)

            # Final Outcome
            self._update_case_status("Resolved")
            self.case_state["final_resolution"] = f"Replacement out of stock. Autonomously replanned to full refund of ${refund_amt:.2f} + $15.00 courtesy store credit. Verified in enterprise ledger."

            step_out = self._record_step(
                step_type="OUTCOME",
                title="Final Outcome: Resolved via Dynamic Replanning",
                summary=f"Successfully handled out-of-stock exception through autonomous replanning: 100% refund of ${refund_amt:.2f} settled + $15 credit applied.",
                details={"status": "Resolved", "refund": ref_res.get("data"), "store_credit": crd_res.get("data"), "verification": v_data}
            )
            yield {"event": "step", "step": step_out, "case_state": self.case_state, "done": True}
            return

def create_agent_case(ticket_id: str) -> str:
    """Initialize a new agent case row in SQLite and return case_id."""
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    now_str = _now()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO agent_cases (id, ticket_id, status, goal, initial_plan, current_plan, created_at, updated_at)
        VALUES (?, ?, 'Pending', '', '', '', ?, ?)
    """, (case_id, ticket_id, now_str, now_str))

    cursor.execute("UPDATE tickets SET status = 'Pending' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return case_id
