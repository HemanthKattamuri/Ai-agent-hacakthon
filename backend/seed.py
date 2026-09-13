"""
Enterprise Database Seeder for ResolveFlow.
Populates simulated customers, products catalog, orders, enterprise policies, and benchmark test scenarios.
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from database import get_db_connection, init_db

def seed_database():
    """Seed the SQLite database with pristine enterprise demo data."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Disable foreign keys during table reset
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DELETE FROM tool_call_logs")
    cursor.execute("DELETE FROM cases")
    cursor.execute("DELETE FROM escalations")
    cursor.execute("DELETE FROM store_credits")
    cursor.execute("DELETE FROM refunds")
    cursor.execute("DELETE FROM replacements")
    cursor.execute("DELETE FROM tickets")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM policies")
    cursor.execute("DELETE FROM operators")
    cursor.execute("PRAGMA foreign_keys = ON")

    now = datetime.now(timezone.utc)
    t_3d = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    t_2d = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    t_45d = (now - timedelta(days=45)).strftime("%Y-%m-%d")
    t_now = now.strftime("%Y-%m-%d")

    # 1. Seed Customers
    customers_data = [
        ("CUST-101", "Sarah Jenkins", "sarah.jenkins@acmecorp.com", "VIP", "2023-01-15", 95, 1450.00, "742 Evergreen Terrace, Springfield, IL"),
        ("CUST-202", "Marcus Chen", "marcus.chen@techsphere.io", "STANDARD", "2023-06-20", 82, 420.00, "10880 Wilshire Blvd, Los Angeles, CA"),
        ("CUST-303", "Elena Rostova", "elena.rostova@globalinvest.com", "ENTERPRISE", "2022-11-05", 98, 8900.00, "450 Lexington Ave, New York, NY"),
        ("CUST-404", "David Kim", "david.kim@startupventure.org", "STANDARD", "2024-02-10", 75, 190.00, "201 Mission St, San Francisco, CA"),
    ]
    cursor.executemany("""
        INSERT INTO customers (id, name, email, tier, account_created, trust_score, total_spend, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers_data)

    # 2. Seed Products
    products_data = [
        ("PROD-HEADPHONES-01", "AuraPro Wireless ANC Headphones", "AUR-HP-01", "Audio", 249.99, 15, 1),
        ("PROD-MONITOR-4K", "UltraVision 32\" 4K HDR Monitor", "UV-MON-4K", "Displays", 599.99, 0, 1), # Stock = 0 triggers Replanning!
        ("PROD-CHAIR-ERGONOMIC", "ErgoComfort Executive Mesh Chair", "ERG-CHR-EX", "Furniture", 450.00, 8, 1),
        ("PROD-KEYBOARD-MECH", "Vortex Stealth RGB Mechanical Keyboard", "VRX-KB-RGB", "Accessories", 129.99, 24, 1),
    ]
    cursor.executemany("""
        INSERT INTO products (id, name, sku, category, price, stock_quantity, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, products_data)

    # 3. Seed Orders
    orders_data = [
        ("ORD-1042", "CUST-101", "PROD-HEADPHONES-01", 1, 249.99, 249.99, t_3d, "DELIVERED", t_3d, "TRK-FEDEX-99881", "CREDIT_CARD_VISA"),
        ("ORD-2089", "CUST-202", "PROD-MONITOR-4K", 1, 599.99, 599.99, t_2d, "DELIVERED", t_2d, "TRK-UPS-77412", "CREDIT_CARD_MASTERCARD"),
        ("ORD-3341", "CUST-303", "PROD-CHAIR-ERGONOMIC", 1, 450.00, 450.00, t_45d, "DELIVERED", t_45d, "TRK-DHL-11029", "CORPORATE_INVOICE"),
        ("ORD-4510", "CUST-404", "PROD-KEYBOARD-MECH", 1, 129.99, 129.99, t_now, "PROCESSING", None, None, "PAYPAL"),
    ]
    cursor.executemany("""
        INSERT INTO orders (id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status, delivery_date, tracking_number, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders_data)

    # 4. Seed Support Tickets
    tickets_data = [
        (
            "TCK-1042", "TCK-1042", "CUST-101", "ORD-1042",
            "Headphones arrived with damaged left ear-cup",
            "Hi, I received my AuraPro headphones today but the left ear cup is completely cracked and has no sound. I need a replacement as soon as possible for my upcoming flight.",
            "DAMAGED_ITEM", "HIGH", "Pending", t_3d
        ),
        (
            "TCK-2089", "TCK-2089", "CUST-202", "ORD-2089",
            "Monitor screen shattered in transit",
            "The courier delivered the UltraVision 4K monitor with severe box damage. When I powered it on, the display is completely shattered. Please send a new one right away.",
            "DAMAGED_ITEM", "URGENT", "Pending", t_2d
        ),
        (
            "TCK-3341", "TCK-3341", "CUST-303", "ORD-3341",
            "Requesting return and refund for office chair",
            "We decided to restructure our office layout and no longer need the ergonomic chair purchased 45 days ago. Requesting a full refund.",
            "RETURN_REQUEST", "MEDIUM", "Pending", t_now
        ),
        (
            "TCK-4510", "TCK-4510", "CUST-404", "ORD-4510",
            "Please cancel my order before it ships",
            "I accidentally ordered the wrong keyboard model. The order is still processing. Please cancel it immediately and refund my payment.",
            "ORDER_CANCELLATION", "HIGH", "Pending", t_now
        ),
        (
            "TCK-5902", "TCK-5902", "CUST-101", "ORD-1042",
            "VIP expedited exchange inquiry",
            "Checking status on my exchange. As a VIP member, I appreciate expedited handling.",
            "GENERAL", "LOW", "Pending", t_now
        )
    ]
    cursor.executemany("""
        INSERT INTO tickets (id, ticket_code, customer_id, order_id, title, message, issue_type, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets_data)

    # 5. Seed Enterprise Policies
    policies_data = [
        (
            "POL-DAMAGE", "damage_replacement", "Transit Damage & Defective Item Resolution Policy",
            json.dumps({
                "window_days": 30,
                "action_in_stock": "DISPATCH_FREE_REPLACEMENT",
                "action_out_of_stock": "FULL_REFUND_AND_STORE_CREDIT",
                "store_credit_appeasement_amount": 25.00,
                "requires_return_for_low_value": False
            }),
            "Covers items damaged during transit within 30 days. Prioritizes free replacement if inventory is available. If out of stock, triggers full refund plus $25 customer appeasement credit."
        ),
        (
            "POL-RETURN", "return_refund", "Standard 30-Day Customer Return Policy",
            json.dumps({
                "return_window_days": 30,
                "allowed_conditions": ["UNDAMAGED", "ORIGINAL_PACKAGING"],
                "policy_enforcement": "STRICT_WINDOW",
                "exception_handling": "ESCALATE_TO_COMPLIANCE_IF_EXCEEDED"
            }),
            "Returns and refunds are strictly authorized within 30 days of delivery. Returns exceeding 30 days violate standard policy and must be escalated to Human Support & Compliance."
        ),
        (
            "POL-CANCEL", "order_cancellation", "Pre-Dispatch Order Cancellation Policy",
            json.dumps({
                "allowed_statuses": ["PROCESSING", "PENDING"],
                "action": "CANCEL_AND_FULL_REFUND",
                "restock_inventory": True
            }),
            "Orders still in PROCESSING or PENDING state can be immediately cancelled with a 100% automated refund and automatic inventory restocking."
        ),
        (
            "POL-APPEASE", "appeasement_credit", "VIP & Loyalty Customer Retention Policy",
            json.dumps({
                "vip_multiplier": 1.5,
                "max_automatic_credit": 50.00,
                "trust_score_threshold": 80
            }),
            "Authorizes up to $50 automated store credit appeasement for high-trust (>80) and VIP customers encountering fulfillment friction."
        )
    ]
    cursor.executemany("""
        INSERT INTO policies (id, category, policy_name, rules_json, summary)
        VALUES (?, ?, ?, ?, ?)
    """, policies_data)

    # 6. Seed Security Operators
    operators_data = [
        ("OP-01", "Elena Rostova", "elena@resolveflow.ai", "LEAD_DIRECTOR", "AI Operations", "Tier-3 Admin", "#6366f1", now.isoformat()),
        ("OP-02", "Marcus Vance", "marcus@resolveflow.ai", "SAFETY_AUDITOR", "Policy & Compliance", "Tier-2 Auditor", "#06b6d4", now.isoformat()),
        ("OP-03", "Dr. Liam Thorne", "liam@resolveflow.ai", "SYSTEMS_ARCHITECT", "Core AI Infrastructure", "Tier-3 Root", "#a855f7", now.isoformat()),
        ("OP-04", "Sarah Jenkins", "sarah@resolveflow.ai", "SUPPORT_LEAD", "VIP Resolution Operations", "Tier-2 Supervisor", "#10b981", now.isoformat())
    ]
    cursor.executemany("""
        INSERT INTO operators (id, name, email, role, department, clearance_level, avatar_color, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, operators_data)

    conn.commit()
    conn.close()
    print("ResolveFlow Database seeded successfully with benchmark scenarios, enterprise policies, and operator profiles!")

if __name__ == "__main__":
    seed_database()
