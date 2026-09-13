"""
Database seeder for QuestFlow.
Populates the Virtual Shop catalogue, demo users, starter equipment, default boss raids, and sample quests.
"""
import uuid
import json
import sqlite3
from datetime import datetime, date, timedelta
from database import get_db_connection, init_db
from rpg_engine import hash_password, calculate_next_level_xp

SHOP_ITEMS_DATA = [
    # --- Weapons ---
    {
        "id": "wpn_quantum_keyblade",
        "name": "Quantum Keyblade",
        "description": "Forged in the matrix compiler. Channels logic into devastating focus strikes.",
        "item_type": "weapon",
        "rarity": "rare",
        "price_gold": 120,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"intellect": 5, "boss_atk": 25, "agility": 2}),
        "icon": "CodeXml",
        "min_level": 1
    },
    {
        "id": "wpn_titan_cleaver",
        "name": "Titan Cleaver of Will",
        "description": "Massive gym-forged blade that pulverizes procrastination and lazy thoughts.",
        "item_type": "weapon",
        "rarity": "rare",
        "price_gold": 140,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"strength": 7, "boss_atk": 30, "vitality": 3}),
        "icon": "Dumbbell",
        "min_level": 2
    },
    {
        "id": "wpn_cyber_katana",
        "name": "Cyber Katana Neon-X",
        "description": "Razor-sharp laser blade tuned to sub-second task execution speeds.",
        "item_type": "weapon",
        "rarity": "epic",
        "price_gold": 260,
        "price_gems": 5,
        "stat_bonus_json": json.dumps({"agility": 9, "boss_atk": 45, "intellect": 4}),
        "icon": "Sword",
        "min_level": 3
    },
    {
        "id": "wpn_obsidian_void_blade",
        "name": "Obsidian Void Blade",
        "description": "Legendary weapon pulsing with dark anti-burnout energy. Slices through backlog mountains.",
        "item_type": "weapon",
        "rarity": "legendary",
        "price_gold": 500,
        "price_gems": 15,
        "stat_bonus_json": json.dumps({"intellect": 12, "strength": 8, "boss_atk": 75, "charisma": 6}),
        "icon": "Flame",
        "min_level": 5
    },

    # --- Helmets & Visors ---
    {
        "id": "hlm_neural_visor",
        "name": "Holographic Neural Visor",
        "description": "HUD overlay highlighting high-priority daily quest milestones and sprint blockers.",
        "item_type": "helmet",
        "rarity": "rare",
        "price_gold": 90,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"intellect": 4, "max_mp": 20}),
        "icon": "Glasses",
        "min_level": 1
    },
    {
        "id": "hlm_crown_discipline",
        "name": "Crown of Unshakable Focus",
        "description": "Golden diadem granted to masters of 10+ day task completion streaks.",
        "item_type": "helmet",
        "rarity": "epic",
        "price_gold": 220,
        "price_gems": 4,
        "stat_bonus_json": json.dumps({"vitality": 6, "intellect": 6, "max_mp": 40}),
        "icon": "Crown",
        "min_level": 3
    },

    # --- Armor ---
    {
        "id": "arm_nano_hoodie",
        "name": "Nano-Mesh Stealth Hoodie",
        "description": "Water-resistant, static-shielded developer armor for deep flow work sessions.",
        "item_type": "armor",
        "rarity": "common",
        "price_gold": 75,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"vitality": 4, "max_hp": 30}),
        "icon": "Shield",
        "min_level": 1
    },
    {
        "id": "arm_paladin_plate",
        "name": "Aegis Paladin Battlesuit",
        "description": "Heavy energized battle armor designed to absorb fatigue and sleep deprivation debuffs.",
        "item_type": "armor",
        "rarity": "epic",
        "price_gold": 240,
        "price_gems": 5,
        "stat_bonus_json": json.dumps({"vitality": 10, "max_hp": 80, "strength": 4}),
        "icon": "ShieldCheck",
        "min_level": 3
    },

    # --- Pets & Companions ---
    {
        "id": "pet_cyber_phoenix",
        "name": "Cyber Phoenix Familiar",
        "description": "A radiant neon companion that chirps when habits are done and grants +10% bonus XP.",
        "item_type": "pet",
        "rarity": "epic",
        "price_gold": 300,
        "price_gems": 8,
        "stat_bonus_json": json.dumps({"xp_bonus_pct": 10, "intellect": 3}),
        "icon": "Bird",
        "min_level": 2
    },
    {
        "id": "pet_iron_golem",
        "name": "Mini Iron Golem Buddy",
        "description": "Sturdy stone buddy cheering your gym sets and hydration goals.",
        "item_type": "pet",
        "rarity": "rare",
        "price_gold": 160,
        "price_gems": 2,
        "stat_bonus_json": json.dumps({"xp_bonus_pct": 8, "strength": 4}),
        "icon": "Bot",
        "min_level": 2
    },

    # --- Auras & Cosmetics ---
    {
        "id": "aur_glitch_matrix",
        "name": "Glitch Matrix Aura",
        "description": "Emits cascading green-cyan cyber runes around your character sprite.",
        "item_type": "aura",
        "rarity": "rare",
        "price_gold": 150,
        "price_gems": 3,
        "stat_bonus_json": json.dumps({"charisma": 5}),
        "icon": "Sparkles",
        "min_level": 1
    },
    {
        "id": "aur_solar_flare",
        "name": "Solar Flare Divinity Aura",
        "description": "Bathes your profile in blinding golden starlight and heroic particles.",
        "item_type": "aura",
        "rarity": "legendary",
        "price_gold": 450,
        "price_gems": 12,
        "stat_bonus_json": json.dumps({"charisma": 12, "intellect": 4}),
        "icon": "Sun",
        "min_level": 4
    },

    # --- Consumables ---
    {
        "id": "con_xp_overclock",
        "name": "Potion of Deep Flow (XP Overclock)",
        "description": "Instantly grants +150 bonus XP and fills your Focus MP gauge to max.",
        "item_type": "potion",
        "rarity": "common",
        "price_gold": 45,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"instant_xp": 150, "restore_mp": 50}),
        "icon": "FlaskConical",
        "min_level": 1
    },
    {
        "id": "con_streak_crystal",
        "name": "Streak Shield Crystal",
        "description": "Magical talisman that preserves your consecutive day streak if you miss a day.",
        "item_type": "potion",
        "rarity": "rare",
        "price_gold": 80,
        "price_gems": 2,
        "stat_bonus_json": json.dumps({"streak_freeze": 1}),
        "icon": "ShieldAlert",
        "min_level": 1
    },

    # --- Themes & Badges ---
    {
        "id": "thm_cyberpunk_neon",
        "name": "Theme: Cyberpunk Neon 2077",
        "description": "High-contrast cyan, violet, and obsidian dark glassmorphism theme.",
        "item_type": "theme",
        "rarity": "rare",
        "price_gold": 100,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"theme_key": "cyberpunk"}),
        "icon": "Palette",
        "min_level": 1
    },
    {
        "id": "thm_fantasy_dark",
        "name": "Theme: Obsidian Fantasy Castle",
        "description": "Medieval gothic dark mode with rich gold, crimson, and velvet accents.",
        "item_type": "theme",
        "rarity": "rare",
        "price_gold": 100,
        "price_gems": 0,
        "stat_bonus_json": json.dumps({"theme_key": "fantasy"}),
        "icon": "Castle",
        "min_level": 1
    },
    {
        "id": "bdg_grandmaster_coder",
        "name": "Badge: Grandmaster Code Mage",
        "description": "Exclusive title badge displayed beside your username on all leaderboards.",
        "item_type": "badge",
        "rarity": "legendary",
        "price_gold": 350,
        "price_gems": 10,
        "stat_bonus_json": json.dumps({"title": "Grandmaster Code Mage", "charisma": 8}),
        "icon": "Award",
        "min_level": 4
    }
]

DEMO_USERS = [
    {
        "id": "usr_alex_chen",
        "username": "AlexChen",
        "email": "alex.chen@questflow.io",
        "password": "password123",
        "class_name": "Code Mage",
        "title": "Lead AI Ops Architect",
        "theme_preference": "cyberpunk",
        "stats": {
            "level": 4,
            "current_xp": 420,
            "next_level_xp": calculate_next_level_xp(4),
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "gold": 240,
            "gems": 12,
            "streak_count": 7,
            "intellect": 34,
            "strength": 16,
            "agility": 22,
            "vitality": 20,
            "charisma": 18,
            "tasks_completed_count": 19,
            "boss_damage_dealt": 1420
        },
        "starter_items": ["wpn_quantum_keyblade", "hlm_neural_visor", "arm_nano_hoodie", "pet_cyber_phoenix"],
        "tasks": [
            {
                "title": "Architect Fast React Flow Engine",
                "description": "Design modular pipeline for AI autonomous replanning & tool verification.",
                "category": "Quest",
                "attribute_tag": "intellect",
                "difficulty": "epic",
                "priority": "urgent",
                "is_completed": 0,
                "due_date": (date.today() + timedelta(days=1)).isoformat(),
                "subtasks": [
                    {"id": "sub_1", "title": "Define state machine interfaces", "completed": True},
                    {"id": "sub_2", "title": "Implement backoff retry policy", "completed": True},
                    {"id": "sub_3", "title": "Benchmark sub-100ms response loop", "completed": False}
                ]
            },
            {
                "title": "Complete 45-min High-Intensity Gym Workout",
                "description": "Bench press, pull-ups, squats, and 15 min core cooldown.",
                "category": "Daily",
                "attribute_tag": "strength",
                "difficulty": "hard",
                "priority": "high",
                "is_completed": 0,
                "due_date": date.today().isoformat(),
                "subtasks": [
                    {"id": "sub_4", "title": "Warm up dynamic stretches", "completed": True},
                    {"id": "sub_5", "title": "Main heavy compound sets", "completed": False},
                    {"id": "sub_6", "title": "Post-workout hydration & protein", "completed": False}
                ]
            },
            {
                "title": "Daily Water Hydration Goal (3 Liters)",
                "description": "Maintain cognitive focus and vitality throughout the day.",
                "category": "Habit",
                "attribute_tag": "vitality",
                "difficulty": "easy",
                "priority": "medium",
                "is_completed": 1,
                "due_date": date.today().isoformat(),
                "subtasks": []
            },
            {
                "title": "Speed-run 3 Pull Request Reviews",
                "description": "Analyze code quality, performance benchmarks, and security lints.",
                "category": "Daily",
                "attribute_tag": "agility",
                "difficulty": "medium",
                "priority": "high",
                "is_completed": 0,
                "due_date": date.today().isoformat(),
                "subtasks": []
            },
            {
                "title": "Present AI Architecture Demo to Team",
                "description": "Engage stakeholders and demonstrate autonomous multi-agent systems.",
                "category": "Quest",
                "attribute_tag": "charisma",
                "difficulty": "hard",
                "priority": "medium",
                "is_completed": 0,
                "due_date": (date.today() + timedelta(days=2)).isoformat(),
                "subtasks": []
            }
        ]
    },
    {
        "id": "usr_sarah_lin",
        "username": "SarahLin",
        "email": "sarah.lin@questflow.io",
        "password": "password123",
        "class_name": "Paladin Scholar",
        "title": "Resolution Champion",
        "theme_preference": "solar",
        "stats": {
            "level": 3,
            "current_xp": 310,
            "next_level_xp": calculate_next_level_xp(3),
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "gold": 180,
            "gems": 8,
            "streak_count": 5,
            "intellect": 24,
            "strength": 20,
            "agility": 18,
            "vitality": 28,
            "charisma": 26,
            "tasks_completed_count": 14,
            "boss_damage_dealt": 980
        },
        "starter_items": ["wpn_titan_cleaver", "arm_paladin_plate", "pet_iron_golem"],
        "tasks": [
            {
                "title": "Morning 20-min Mindfulness Meditation",
                "description": "Deep breathing and mental clarity exercise before deep work.",
                "category": "Habit",
                "attribute_tag": "vitality",
                "difficulty": "easy",
                "priority": "medium",
                "is_completed": 1,
                "due_date": date.today().isoformat(),
                "subtasks": []
            },
            {
                "title": "Audit Enterprise Compliance Policies",
                "description": "Review GDPR, SOC2 compliance logs and cryptographic proofs.",
                "category": "Quest",
                "attribute_tag": "intellect",
                "difficulty": "hard",
                "priority": "urgent",
                "is_completed": 0,
                "due_date": date.today().isoformat(),
                "subtasks": []
            }
        ]
    },
    {
        "id": "usr_marcus_vance",
        "username": "MarcusVance",
        "email": "marcus.vance@questflow.io",
        "password": "password123",
        "class_name": "Cyber Rogue",
        "title": "Speedrunner of Tasks",
        "theme_preference": "fantasy",
        "stats": {
            "level": 5,
            "current_xp": 650,
            "next_level_xp": calculate_next_level_xp(5),
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "gold": 380,
            "gems": 20,
            "streak_count": 12,
            "intellect": 30,
            "strength": 22,
            "agility": 42,
            "vitality": 26,
            "charisma": 25,
            "tasks_completed_count": 31,
            "boss_damage_dealt": 2850
        },
        "starter_items": ["wpn_cyber_katana", "hlm_crown_discipline", "aur_glitch_matrix"],
        "tasks": [
            {
                "title": "Execute Zero-Downtime Database Migration",
                "description": "Run schema alterations with rollback scripts ready.",
                "category": "Quest",
                "attribute_tag": "agility",
                "difficulty": "epic",
                "priority": "urgent",
                "is_completed": 0,
                "due_date": date.today().isoformat(),
                "subtasks": []
            }
        ]
    }
]

def seed_database():
    """Seed shop catalogue, users, stats, inventory, boss, and tasks."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Seed Shop Items
    for item in SHOP_ITEMS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO shop_items 
            (id, name, description, item_type, rarity, price_gold, price_gems, stat_bonus_json, icon, min_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["id"],
            item["name"],
            item["description"],
            item["item_type"],
            item["rarity"],
            item["price_gold"],
            item["price_gems"],
            item["stat_bonus_json"],
            item["icon"],
            item["min_level"]
        ))

    # 2. Seed Demo Users
    for user_data in DEMO_USERS:
        pwd_hash, salt = hash_password(user_data["password"])
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, salt, class_name, title, theme_preference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data["id"],
            user_data["username"],
            user_data["email"],
            pwd_hash,
            salt,
            user_data["class_name"],
            user_data["title"],
            user_data["theme_preference"]
        ))

        # Seed Stats
        st = user_data["stats"]
        cursor.execute("""
            INSERT OR REPLACE INTO character_stats
            (user_id, level, current_xp, next_level_xp, hp, max_hp, mp, max_mp, gold, gems,
             streak_count, last_active_date, intellect, strength, agility, vitality, charisma,
             tasks_completed_count, boss_damage_dealt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data["id"],
            st["level"],
            st["current_xp"],
            st["next_level_xp"],
            st["hp"],
            st["max_hp"],
            st["mp"],
            st["max_mp"],
            st["gold"],
            st["gems"],
            st["streak_count"],
            date.today().isoformat(),
            st["intellect"],
            st["strength"],
            st["agility"],
            st["vitality"],
            st["charisma"],
            st["tasks_completed_count"],
            st["boss_damage_dealt"]
        ))

        # Seed Starter Inventory
        for item_id in user_data["starter_items"]:
            # Find item details
            shop_match = next((x for x in SHOP_ITEMS_DATA if x["id"] == item_id), None)
            if shop_match:
                inv_id = f"inv_{user_data['id']}_{item_id}"
                cursor.execute("""
                    INSERT OR REPLACE INTO inventory
                    (id, user_id, item_id, item_name, item_type, rarity, stat_bonus_json, is_equipped, icon, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    inv_id,
                    user_data["id"],
                    shop_match["id"],
                    shop_match["name"],
                    shop_match["item_type"],
                    shop_match["rarity"],
                    shop_match["stat_bonus_json"],
                    1, # Default equipped
                    shop_match["icon"],
                    shop_match["description"]
                ))

        # Seed Active Boss Raid for User
        boss_id = f"boss_{user_data['id']}_1"
        cursor.execute("""
            INSERT OR REPLACE INTO boss_raids
            (id, user_id, name, description, avatar_icon, current_hp, max_hp, attack_power, reward_xp, reward_gold, reward_gems, is_defeated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            boss_id,
            user_data["id"],
            "The Dread Procrastination Demon",
            "A hulking monster of endless distractions, missed alarms, and delayed goals.",
            "Skull",
            3580,
            5000,
            20,
            600,
            250,
            15,
            0
        ))

        # Seed Tasks
        for i, t in enumerate(user_data["tasks"]):
            t_id = f"task_{user_data['id']}_{i+1}"
            cursor.execute("""
                INSERT OR REPLACE INTO tasks
                (id, user_id, title, description, category, attribute_tag, difficulty, priority,
                 xp_reward, gold_reward, is_completed, due_date, subtasks_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t_id,
                user_data["id"],
                t["title"],
                t["description"],
                t["category"],
                t["attribute_tag"],
                t["difficulty"],
                t["priority"],
                60 if t["difficulty"] == "medium" else (120 if t["difficulty"] == "hard" else (250 if t["difficulty"] == "epic" else 30)),
                25 if t["difficulty"] == "medium" else (50 if t["difficulty"] == "hard" else (110 if t["difficulty"] == "epic" else 12)),
                t["is_completed"],
                t["due_date"],
                json.dumps(t["subtasks"])
            ))

    conn.commit()
    conn.close()
    print("QuestFlow Database seeded successfully with demo users, items, quests, and boss raids!")

if __name__ == "__main__":
    seed_database()
