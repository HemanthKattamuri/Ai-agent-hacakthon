"""
Database initialization and connection management for QuestFlow RPG Engine.
Uses SQLite for robust local relational storage.
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "questflow.db"

def get_db_connection() -> sqlite3.Connection:
    """Return a connection with Row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Create all core QuestFlow tables if they do not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            class_name TEXT NOT NULL DEFAULT 'Code Mage',
            avatar_url TEXT,
            title TEXT DEFAULT 'Novice Adventurer',
            theme_preference TEXT DEFAULT 'cyberpunk',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Character Stats Table (1-to-1 with Users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS character_stats (
            user_id TEXT PRIMARY KEY,
            level INTEGER NOT NULL DEFAULT 1,
            current_xp INTEGER NOT NULL DEFAULT 0,
            next_level_xp INTEGER NOT NULL DEFAULT 100,
            hp INTEGER NOT NULL DEFAULT 100,
            max_hp INTEGER NOT NULL DEFAULT 100,
            mp INTEGER NOT NULL DEFAULT 50,
            max_mp INTEGER NOT NULL DEFAULT 50,
            gold INTEGER NOT NULL DEFAULT 50,
            gems INTEGER NOT NULL DEFAULT 5,
            streak_count INTEGER NOT NULL DEFAULT 1,
            last_active_date TEXT,
            streak_freeze_count INTEGER NOT NULL DEFAULT 1,
            intellect INTEGER NOT NULL DEFAULT 10,
            strength INTEGER NOT NULL DEFAULT 10,
            agility INTEGER NOT NULL DEFAULT 10,
            vitality INTEGER NOT NULL DEFAULT 10,
            charisma INTEGER NOT NULL DEFAULT 10,
            tasks_completed_count INTEGER NOT NULL DEFAULT 0,
            boss_damage_dealt INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 3. Tasks Table (CRUD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL DEFAULT 'Quest', -- Habit, Daily, Quest, Todo
            attribute_tag TEXT NOT NULL DEFAULT 'intellect', -- intellect, strength, agility, vitality, charisma
            difficulty TEXT NOT NULL DEFAULT 'medium', -- trivial, easy, medium, hard, epic
            priority TEXT NOT NULL DEFAULT 'medium', -- low, medium, high, urgent
            xp_reward INTEGER NOT NULL DEFAULT 60,
            gold_reward INTEGER NOT NULL DEFAULT 25,
            is_completed INTEGER NOT NULL DEFAULT 0,
            completed_at TIMESTAMP,
            due_date TEXT,
            streak_count INTEGER NOT NULL DEFAULT 0,
            subtasks_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 4. Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_type TEXT NOT NULL, -- weapon, armor, helmet, pet, aura, potion, theme, badge
            rarity TEXT NOT NULL DEFAULT 'common', -- common, rare, epic, legendary
            stat_bonus_json TEXT DEFAULT '{}',
            is_equipped INTEGER NOT NULL DEFAULT 0,
            icon TEXT NOT NULL,
            description TEXT,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 5. Shop Catalogue Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shop_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            item_type TEXT NOT NULL, -- weapon, armor, helmet, pet, aura, potion, theme, badge
            rarity TEXT NOT NULL DEFAULT 'common',
            price_gold INTEGER NOT NULL DEFAULT 0,
            price_gems INTEGER NOT NULL DEFAULT 0,
            stat_bonus_json TEXT DEFAULT '{}',
            icon TEXT NOT NULL,
            min_level INTEGER NOT NULL DEFAULT 1
        )
    """)

    # 6. Boss Raids Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boss_raids (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            avatar_icon TEXT NOT NULL,
            current_hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            attack_power INTEGER NOT NULL DEFAULT 15,
            reward_xp INTEGER NOT NULL DEFAULT 500,
            reward_gold INTEGER NOT NULL DEFAULT 200,
            reward_gems INTEGER NOT NULL DEFAULT 10,
            is_defeated INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 7. Activity & Battle Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL, -- TASK_COMPLETED, LEVEL_UP, BOSS_HIT, ITEM_BOUGHT, STREAK_ADVANCED
            message TEXT NOT NULL,
            xp_gained INTEGER DEFAULT 0,
            gold_gained INTEGER DEFAULT 0,
            attribute_increased TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("QuestFlow SQLite Database Initialized successfully.")
