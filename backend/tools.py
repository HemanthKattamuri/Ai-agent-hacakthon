"""
Simulated Enterprise Backend Tools for ResolveFlow.
Implements the 11 required tools interacting with the enterprise SQLite database.
All tools return structured, auditable JSON dictionaries.
"""
import json
import uuid
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database import get_db_connection

def _format_time() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_customer(customer_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Inspect customer profile, tier, trust score, and lifetime spend."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    if not row:
        result = {"error": f"Customer '{customer_id}' not found", "found": False}
        return {"status": "FAILURE", "duration_ms": duration_ms, "data": result}

    customer_data = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "tier": row["tier"],
        "account_created": row["account_created"],
        "trust_score": row["trust_score"],
        "total_spend": row["total_spend"],
        "address": row["address"],
        "vip_status": row["tier"].upper() in ["VIP", "PLATINUM", "GOLD"],
    }
    return {"status": "SUCCESS", "duration_ms": duration_ms, "data": customer_data}

def get_order(order_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Inspect order details, shipment tracking, product purchased, delivery date, and payment status."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, p.name as product_name, p.sku as product_sku, p.price as product_catalog_price
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.id = ?
    """, (order_id,))
    row = cursor.fetchone()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    if not row:
        result = {"error": f"Order '{order_id}' not found", "found": False}
        return {"status": "FAILURE", "duration_ms": duration_ms, "data": result}

    order_data = {
        "order_id": row["id"],
        "customer_id": row["customer_id"],
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "product_sku": row["product_sku"],
        "quantity": row["quantity"],
        "unit_price": row["unit_price"],
        "total_amount": row["total_amount"],
        "order_date": row["order_date"],
        "status": row["status"],
        "delivery_date": row["delivery_date"],
        "tracking_number": row["tracking_number"],
        "payment_method": row["payment_method"]
    }
    return {"status": "SUCCESS", "duration_ms": duration_ms, "data": order_data}

def get_inventory(product_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Check live warehouse inventory stock levels for a product."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    if not row:
        result = {"error": f"Product '{product_id}' not found in inventory catalog", "found": False}
        return {"status": "FAILURE", "duration_ms": duration_ms, "data": result}

    stock = row["stock_quantity"]
    inventory_data = {
        "product_id": row["id"],
        "product_name": row["name"],
        "sku": row["sku"],
        "stock_quantity": stock,
        "is_available": stock > 0,
        "restock_eta": "14 business days" if stock == 0 else "In stock"
    }
    return {"status": "SUCCESS", "duration_ms": duration_ms, "data": inventory_data}

def search_policy(issue_type: str, order_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Evaluate company return, refund, replacement, and warranty policy against order parameters."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    cursor.execute("SELECT * FROM policies WHERE category LIKE ?", (f"%{issue_type}%",))
    policies = cursor.fetchall()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    if not order:
        return {
            "status": "FAILURE",
            "duration_ms": duration_ms,
            "data": {"error": f"Order {order_id} not found to check policy constraints"}
        }

    # Policy date calculations
    delivery_date_str = order["delivery_date"]
    days_since_delivery = 0
    if delivery_date_str:
        try:
            deliv_dt = datetime.fromisoformat(delivery_date_str.replace("Z", "+00:00"))
            days_since_delivery = max(0, (datetime.now(timezone.utc) - deliv_dt).days)
        except Exception:
            days_since_delivery = 5

    # Evaluation logic
    policy_evaluation = {
        "issue_type": issue_type,
        "order_id": order_id,
        "days_since_delivery": days_since_delivery,
        "policy_window_days": 30,
        "within_policy_window": days_since_delivery <= 30
    }

    if "damage" in issue_type.lower() or "defect" in issue_type.lower() or "replace" in issue_type.lower():
        if days_since_delivery <= 30:
            policy_evaluation.update({
                "authorized": True,
                "permitted_actions": ["REPLACEMENT", "FULL_REFUND", "STORE_CREDIT"],
                "preferred_action": "REPLACEMENT",
                "rules_applied": [
                    "Policy DAM-01: In-transit damage reported within 30 days is 100% covered.",
                    "Primary resolution: Ship brand-new replacement at zero cost.",
                    "Secondary resolution (if out of stock): 100% full refund + discretionary $15 goodwill store credit for VIP/high-trust customers."
                ]
            })
        else:
            policy_evaluation.update({
                "authorized": False,
                "permitted_actions": ["ESCALATE_TO_HUMAN"],
                "preferred_action": "ESCALATE_TO_HUMAN",
                "reason": f"Damage reported {days_since_delivery} days after delivery exceeds standard 30-day window.",
                "rules_applied": ["Policy DAM-03: Exceptions require Tier 2 human supervisor signoff."]
            })
    elif "refund" in issue_type.lower() or "return" in issue_type.lower():
        if days_since_delivery <= 30:
            policy_evaluation.update({
                "authorized": True,
                "permitted_actions": ["FULL_REFUND", "STORE_CREDIT"],
                "preferred_action": "FULL_REFUND",
                "rules_applied": [
                    "Policy RET-01: Standard returns within 30 days eligible for 100% refund."
                ]
            })
        else:
            policy_evaluation.update({
                "authorized": False,
                "permitted_actions": ["ESCALATE_TO_HUMAN"],
                "preferred_action": "ESCALATE_TO_HUMAN",
                "reason": f"Refund request initiated {days_since_delivery} days after delivery. Exceeds standard 30-day return policy window.",
                "rules_applied": [
                    "Policy RET-04: Returns >30 days strictly require human manager authorization.",
                    "Automated refund is locked and forbidden by system safety policy."
                ]
            })
    elif "cancel" in issue_type.lower():
        order_status = order["status"]
        if order_status in ["Processing", "Pending_Fulfillment"]:
            policy_evaluation.update({
                "authorized": True,
                "permitted_actions": ["CANCEL_ORDER", "RESTOCK_INVENTORY"],
                "preferred_action": "CANCEL_ORDER",
                "rules_applied": [
                    "Policy CAN-01: Pre-fulfillment orders in 'Processing' status can be autonomously cancelled.",
                    "Order payment transaction is voided and warehouse inventory is automatically restocked."
                ]
            })
        else:
            policy_evaluation.update({
                "authorized": False,
                "permitted_actions": ["ESCALATE_TO_HUMAN"],
                "preferred_action": "ESCALATE_TO_HUMAN",
                "reason": f"Order is already in status '{order_status}' and cannot be cancelled directly before delivery.",
                "rules_applied": [
                    "Policy CAN-02: Orders in transit or delivered must follow the standard return process once received."
                ]
            })
    else:
        policy_evaluation.update({
            "authorized": True,
            "permitted_actions": ["STORE_CREDIT", "ESCALATE_TO_HUMAN"],
            "preferred_action": "ESCALATE_TO_HUMAN",
            "rules_applied": ["Policy GEN-01: Ambiguous requests escalate to support team."]
        })

    return {"status": "SUCCESS", "duration_ms": duration_ms, "data": policy_evaluation}

def get_customer_history(customer_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical interactions, prior claims, and dispute records for customer."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM customer_history
        WHERE customer_id = ?
        ORDER BY timestamp DESC
    """, (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    history = [dict(row) for row in rows]
    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "customer_id": customer_id,
            "total_tickets_filed": len(history),
            "history_records": history,
            "reputation_flag": "CLEAN" if len(history) < 4 else "HIGH_ACTIVITY"
        }
    }

def create_replacement(order_id: str, product_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Attempt to order a replacement item.
    Enforces inventory check: FAILS if inventory is 0 to test autonomous agent replanning.
    """
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check order
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Order {order_id} not found."}
        }

    # Check inventory
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Product {product_id} not found in catalog."}
        }

    current_stock = product["stock_quantity"]
    if current_stock <= 0:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {
                "error": "INSUFFICIENT_INVENTORY",
                "message": f"Cannot create replacement: Product '{product['name']}' ({product_id}) is currently out of stock (Stock: 0).",
                "product_name": product["name"],
                "stock_quantity": 0,
                "action_required": "REPLAN_RESOLUTION"
            }
        }

    # Decrement stock and create replacement record
    new_order_id = f"ORD-REP-{uuid.uuid4().hex[:6].upper()}"
    tracking_number = f"TRK-REP-{uuid.uuid4().hex[:8].upper()}"
    replacement_id = f"REP-{uuid.uuid4().hex[:6].upper()}"
    now_str = _format_time()

    cursor.execute("UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = ?", (product_id,))
    cursor.execute("""
        INSERT INTO replacements (id, original_order_id, new_order_id, product_id, quantity, status, tracking_number, timestamp)
        VALUES (?, ?, ?, ?, 1, 'Ordered', ?, ?)
    """, (replacement_id, order_id, new_order_id, product_id, tracking_number, now_str))

    # Add customer history
    hist_id = f"HIST-{uuid.uuid4().hex[:6].upper()}"
    cursor.execute("""
        INSERT INTO customer_history (id, customer_id, order_id, event_type, notes, timestamp)
        VALUES (?, ?, ?, 'Replacement_Issued', ?, ?)
    """, (hist_id, order["customer_id"], order_id, f"Replacement order {new_order_id} dispatched (Tracking: {tracking_number})", now_str))

    conn.commit()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "action": "CREATE_REPLACEMENT",
            "replacement_id": replacement_id,
            "new_order_id": new_order_id,
            "original_order_id": order_id,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": 1,
            "status": "Ordered",
            "tracking_number": tracking_number,
            "shipping_method": "Expedited 2-Day Air (Complimentary)",
            "estimated_delivery": "Within 48 hours"
        }
    }

def issue_refund(order_id: str, amount: float, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Issue a full or partial financial refund to the customer's original payment method."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Order {order_id} not found."}
        }

    if amount > order["total_amount"]:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Refund amount ${amount:.2f} exceeds original order total ${order['total_amount']:.2f}."}
        }

    refund_id = f"REF-{uuid.uuid4().hex[:6].upper()}"
    tx_ref = f"TX-GATEWAY-{uuid.uuid4().hex[:8].upper()}"
    now_str = _format_time()

    cursor.execute("""
        INSERT INTO refunds (id, order_id, customer_id, amount, reason, status, timestamp, transaction_reference)
        VALUES (?, ?, ?, ?, 'Automated Resolution: Customer Damage / Out of Stock', 'Completed', ?, ?)
    """, (refund_id, order_id, order["customer_id"], amount, now_str, tx_ref))

    cursor.execute("UPDATE orders SET status = 'Refunded' WHERE id = ?", (order_id,))

    # Log history
    hist_id = f"HIST-{uuid.uuid4().hex[:6].upper()}"
    cursor.execute("""
        INSERT INTO customer_history (id, customer_id, order_id, event_type, notes, timestamp)
        VALUES (?, ?, ?, 'Refund_Issued', ?, ?)
    """, (hist_id, order["customer_id"], order_id, f"Refund of ${amount:.2f} credited via {order['payment_method']} (Ref: {tx_ref})", now_str))

    conn.commit()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "action": "ISSUE_REFUND",
            "refund_id": refund_id,
            "order_id": order_id,
            "customer_id": order["customer_id"],
            "amount_refunded": amount,
            "currency": "USD",
            "payment_method": order["payment_method"],
            "transaction_reference": tx_ref,
            "status": "Settled",
            "message": f"Successfully refunded ${amount:.2f} to original payment card."
        }
    }

def cancel_order(order_id: str, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Cancel an active pending or in-transit order."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Order {order_id} not found."}
        }

    if order["status"] in ["Delivered", "Returned", "Cancelled"]:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Order {order_id} is already in status '{order['status']}' and cannot be cancelled directly."}
        }

    now_str = _format_time()
    product_id = order["product_id"]
    quantity = order["quantity"]

    cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE id = ?", (order_id,))
    cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?", (quantity, product_id))
    cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
    prod_row = cursor.fetchone()
    new_stock = prod_row["stock_quantity"] if prod_row else 0

    cursor.execute("""
        INSERT INTO customer_history (id, customer_id, order_id, event_type, notes, timestamp)
        VALUES (?, ?, ?, 'Order_Cancelled', 'Order cancelled by autonomous resolution system. Warehouse inventory restored.', ?)
    """, (f"HIST-{uuid.uuid4().hex[:6].upper()}", order["customer_id"], order_id, now_str))

    conn.commit()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "action": "CANCEL_ORDER",
            "order_id": order_id,
            "product_id": product_id,
            "units_restocked": quantity,
            "new_stock_level": new_stock,
            "previous_status": order["status"],
            "new_status": "Cancelled",
            "timestamp": now_str,
            "message": f"Order {order_id} successfully cancelled. Payment voided and {quantity} unit(s) restocked to warehouse inventory."
        }
    }

def create_store_credit(customer_id: str, amount: float, case_id: Optional[str] = None) -> Dict[str, Any]:
    """Grant goodwill or appeasement store credit to the customer's wallet."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Customer {customer_id} not found."}
        }

    credit_id = f"CRD-{uuid.uuid4().hex[:6].upper()}"
    now_str = _format_time()

    cursor.execute("""
        INSERT INTO store_credits (id, customer_id, amount, balance_remaining, reason, timestamp)
        VALUES (?, ?, ?, ?, 'Goodwill Appeasement for Inconvenience', ?)
    """, (credit_id, customer_id, amount, amount, now_str))

    cursor.execute("""
        INSERT INTO customer_history (id, customer_id, order_id, event_type, notes, timestamp)
        VALUES (?, ?, NULL, 'Store_Credit_Issued', ?, ?)
    """, (f"HIST-{uuid.uuid4().hex[:6].upper()}", customer_id, f"Granted ${amount:.2f} store credit (ID: {credit_id})", now_str))

    conn.commit()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "action": "CREATE_STORE_CREDIT",
            "credit_id": credit_id,
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "amount": amount,
            "currency": "USD",
            "status": "Available",
            "message": f"Issued ${amount:.2f} courtesy store credit to customer's account."
        }
    }

def verify_resolution(case_id: str) -> Dict[str, Any]:
    """
    Independently inspect database state to confirm that the promised state-changing action
    actually materialized in enterprise tables (Replacements, Refunds, or Escalations).
    Calculates cryptographic verification seal.
    """
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agent_cases WHERE id = ?", (case_id,))
    case_row = cursor.fetchone()

    if not case_row:
        conn.close()
        return {
            "status": "FAILURE",
            "duration_ms": int((time.time() - t0) * 1000),
            "data": {"error": f"Case '{case_id}' not found."}
        }

    ticket_id = case_row["ticket_id"]
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    order_id = ticket["order_id"] if ticket else None
    customer_id = ticket["customer_id"] if ticket else None

    # Check replacements
    cursor.execute("SELECT * FROM replacements WHERE original_order_id = ? ORDER BY timestamp DESC LIMIT 1", (order_id,))
    rep = cursor.fetchone()

    # Check refunds
    cursor.execute("SELECT * FROM refunds WHERE order_id = ? ORDER BY timestamp DESC LIMIT 1", (order_id,))
    ref = cursor.fetchone()

    # Check credits
    cursor.execute("SELECT * FROM store_credits WHERE customer_id = ? ORDER BY timestamp DESC LIMIT 1", (customer_id,))
    crd = cursor.fetchone()

    # Check escalations
    cursor.execute("SELECT * FROM escalations WHERE case_id = ? ORDER BY timestamp DESC LIMIT 1", (case_id,))
    esc = cursor.fetchone()

    # Check orders
    order = None
    if order_id:
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()

    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    db_proof = {}
    verified = False
    action_type = "UNKNOWN"
    target_id = ""

    if rep:
        verified = True
        action_type = "REPLACEMENT_VERIFIED"
        target_id = rep["id"]
        db_proof = {
            "table": "replacements",
            "record_id": rep["id"],
            "new_order_id": rep["new_order_id"],
            "tracking_number": rep["tracking_number"],
            "status": rep["status"],
            "db_timestamp": rep["timestamp"]
        }
    elif ref:
        verified = True
        action_type = "REFUND_VERIFIED"
        target_id = ref["id"]
        db_proof = {
            "table": "refunds",
            "record_id": ref["id"],
            "amount": ref["amount"],
            "transaction_reference": ref["transaction_reference"],
            "status": ref["status"],
            "db_timestamp": ref["timestamp"]
        }
        if crd:
            db_proof["courtesy_store_credit"] = {
                "credit_id": crd["id"],
                "amount": crd["amount"]
            }
    elif esc:
        verified = True
        action_type = "ESCALATION_VERIFIED"
        target_id = esc["id"]
        db_proof = {
            "table": "escalations",
            "record_id": esc["id"],
            "assigned_team": esc["assigned_team"],
            "reason": esc["reason"],
            "priority": esc["priority"],
            "db_timestamp": esc["timestamp"]
        }
    elif order and order["status"] == "Cancelled":
        verified = True
        action_type = "ORDER_CANCELLATION_VERIFIED"
        target_id = order["id"]
        db_proof = {
            "table": "orders",
            "record_id": order["id"],
            "order_status": "Cancelled",
            "product_id": order["product_id"],
            "amount_voided": order["total_amount"],
            "payment_method": order["payment_method"],
            "inventory_restocked": True
        }

    now_str = _format_time()
    raw_hash_input = f"{case_id}:{action_type}:{target_id}:{now_str}"
    audit_hash = hashlib.sha256(raw_hash_input.encode("utf-8")).hexdigest()[:24].upper()

    verification_data = {
        "verified": verified,
        "action_type": action_type,
        "target_id": target_id,
        "audit_hash": f"SEAL-{audit_hash}",
        "verified_at": now_str,
        "db_proof": db_proof,
        "integrity_check": "PASSED" if verified else "FAILED_NO_ACTION_RECORDED"
    }

    return {
        "status": "SUCCESS" if verified else "FAILURE",
        "duration_ms": duration_ms,
        "data": verification_data
    }

def escalate_to_human(case_id: str, reason: str) -> Dict[str, Any]:
    """Escalate a non-standard, policy-violating, or high-risk case to tier-2 human supervisor."""
    t0 = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agent_cases WHERE id = ?", (case_id,))
    case_row = cursor.fetchone()
    ticket_id = case_row["ticket_id"] if case_row else "UNKNOWN_TICKET"

    esc_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
    now_str = _format_time()

    cursor.execute("""
        INSERT INTO escalations (id, case_id, ticket_id, reason, priority, assigned_team, status, timestamp)
        VALUES (?, ?, ?, ?, 'High', 'Tier-2 Human Escalations Desk', 'Open', ?)
    """, (esc_id, case_id, ticket_id, reason, now_str))

    cursor.execute("UPDATE agent_cases SET status = 'Escalated' WHERE id = ?", (case_id,))
    cursor.execute("UPDATE tickets SET status = 'Escalated' WHERE id = ?", (ticket_id,))

    conn.commit()
    conn.close()
    duration_ms = int((time.time() - t0) * 1000)

    return {
        "status": "SUCCESS",
        "duration_ms": duration_ms,
        "data": {
            "action": "ESCALATE_TO_HUMAN",
            "escalation_id": esc_id,
            "case_id": case_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "assigned_team": "Tier-2 Human Escalations Desk",
            "priority": "High",
            "status": "Dispatched",
            "sla_response_time": "Under 1 hour",
            "summary": "Case safely routed away from automated actions to human review due to policy parameters."
        }
    }

# Mapping dict for dynamic tool lookup
TOOL_REGISTRY = {
    "get_customer": get_customer,
    "get_order": get_order,
    "get_inventory": get_inventory,
    "search_policy": search_policy,
    "get_customer_history": get_customer_history,
    "create_replacement": create_replacement,
    "issue_refund": issue_refund,
    "cancel_order": cancel_order,
    "create_store_credit": create_store_credit,
    "verify_resolution": verify_resolution,
    "escalate_to_human": escalate_to_human,
}
