"""
Database initialization and connection management for ResolveFlow.
Uses SQLite for robust local relational storage and simulated enterprise database audits.
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "resolveflow.db"

def get_db_connection() -> sqlite3.Connection:
    """Return a connection with Row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Create all enterprise ResolveFlow tables if they do not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'STANDARD', -- STANDARD, VIP, PLATINUM, ENTERPRISE
            account_created TEXT NOT NULL,
            trust_score INTEGER NOT NULL DEFAULT 85,
            total_spend REAL NOT NULL DEFAULT 0.0,
            address TEXT NOT NULL
        )
    """)

    # 2. Products Catalog Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # 3. Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL, -- DELIVERED, PROCESSING, SHIPPED, CANCELLED, REFUNDED
            delivery_date TEXT,
            tracking_number TEXT,
            payment_method TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 4. Support Tickets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            ticket_code TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            order_id TEXT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            issue_type TEXT NOT NULL, -- DAMAGED_ITEM, RETURN_REQUEST, ORDER_CANCELLATION, POLICY_CONFLICT, GENERAL
            priority TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, URGENT
            status TEXT NOT NULL DEFAULT 'Pending', -- Pending, Investigating, Action Taken, Replanning, Resolved, Escalated
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    # 5. Replacements Table (Action Ledger)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS replacements (
            id TEXT PRIMARY KEY,
            original_order_id TEXT NOT NULL,
            new_order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'DISPATCHED',
            tracking_number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (original_order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 6. Refunds Table (Financial Ledger)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refunds (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PROCESSED',
            timestamp TEXT NOT NULL,
            transaction_reference TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # 7. Store Credits Table (Appeasement Ledger)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_credits (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_remaining REAL NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # 8. Human Escalations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            ticket_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'HIGH',
            assigned_team TEXT NOT NULL DEFAULT 'Tier-2 Support & Compliance',
            status TEXT NOT NULL DEFAULT 'ESCALATED',
            timestamp TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    # 9. Enterprise Policies Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            policy_name TEXT NOT NULL,
            rules_json TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    """)

    # 10. Tool Call Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_call_logs (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            input_params TEXT NOT NULL,
            result TEXT NOT NULL,
            status TEXT NOT NULL, -- SUCCESS, FAILURE, ERROR
            duration_ms INTEGER NOT NULL DEFAULT 0
        )
    """)

    # 11. Agent Cases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            ticket_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            goal TEXT,
            initial_plan TEXT,
            current_plan TEXT,
            replan_reason TEXT,
            final_resolution TEXT,
            verification_badge TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    # 12. Security Operators & User Profiles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operators (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'AGENT_OPERATOR',
            department TEXT NOT NULL DEFAULT 'AI Operations',
            clearance_level TEXT NOT NULL DEFAULT 'Tier-2',
            avatar_color TEXT NOT NULL DEFAULT '#6366f1',
            last_login TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("ResolveFlow SQLite database initialized successfully.")
