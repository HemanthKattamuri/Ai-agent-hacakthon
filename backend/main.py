"""
FastAPI Backend Application for QuestFlow — RPG Gamified Task & Habit Progression Engine.
Provides complete REST APIs for Authentication, Task CRUD, RPG Leveling, Character Inventory,
Shop Economy, Boss Raids, and Productivity Analytics.
"""
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, get_db_connection
from seed import seed_database, SHOP_ITEMS_DATA
from rpg_engine import (
    hash_password,
    verify_password,
    calculate_next_level_xp,
    calculate_task_rewards,
    process_xp_gain,
    calculate_streak_update,
    roll_random_loot
)
from models import (
    UserRegisterRequest,
    UserLoginRequest,
    DemoLoginRequest,
    TaskCreateRequest,
    TaskUpdateRequest,
    EquipItemRequest,
    UseItemRequest,
    BuyShopItemRequest,
    UpdateThemeRequest
)

app = FastAPI(
    title="QuestFlow RPG Engine API",
    description="Autonomous RPG Task & Habit Progression Engine API",
    version="2.0.0"
)

# CORS middleware configuration
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

# ---------------------------------------------------------------------------
# Auth Dependency & User Extraction
# ---------------------------------------------------------------------------

def get_current_user_id(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> str:
    """Extract authenticated user ID from headers (fallback to demo user)."""
    if x_user_id:
        return x_user_id
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
    # Default fallback for unauthenticated public requests
    return "usr_alex_chen"

# ---------------------------------------------------------------------------
# System & Health
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "QuestFlow RPG Progression Engine API",
        "status": "online",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/demo/reset")
def reset_database():
    """Reseed the database back to clean demo state."""
    seed_database()
    return {"message": "Database reset to pristine demo state successfully."}

# ---------------------------------------------------------------------------
# Authentication Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/auth/signup")
def signup(req: UserRegisterRequest):
    """Register a new RPG adventurer and initialize character sheet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing email or username
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (req.email.lower(), req.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="A warrior with this email or username already exists.")

    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    pwd_hash, salt = hash_password(req.password)

    # 1. Insert User
    cursor.execute("""
        INSERT INTO users (id, username, email, password_hash, salt, class_name, title, theme_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        req.username,
        req.email.lower(),
        pwd_hash,
        salt,
        req.class_name,
        req.title or "Novice Adventurer",
        "cyberpunk"
    ))

    # 2. Insert Starter Character Stats
    class_stat_boosts = {
        "Code Mage": {"intellect": 14, "strength": 8, "agility": 10, "vitality": 10, "charisma": 10},
        "Iron Warrior": {"intellect": 8, "strength": 16, "agility": 8, "vitality": 14, "charisma": 8},
        "Cyber Rogue": {"intellect": 10, "strength": 8, "agility": 16, "vitality": 10, "charisma": 10},
        "Paladin Scholar": {"intellect": 12, "strength": 10, "agility": 8, "vitality": 14, "charisma": 12},
    }
    stats = class_stat_boosts.get(req.class_name, {"intellect": 10, "strength": 10, "agility": 10, "vitality": 10, "charisma": 10})

    cursor.execute("""
        INSERT INTO character_stats
        (user_id, level, current_xp, next_level_xp, hp, max_hp, mp, max_mp, gold, gems,
         streak_count, last_active_date, intellect, strength, agility, vitality, charisma)
        VALUES (?, 1, 0, 100, 100, 100, 50, 50, 50, 5, 1, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        date.today().isoformat(),
        stats["intellect"],
        stats["strength"],
        stats["agility"],
        stats["vitality"],
        stats["charisma"]
    ))

    # 3. Add starter weapon
    starter_weapon = "wpn_quantum_keyblade" if req.class_name == "Code Mage" else (
        "wpn_titan_cleaver" if req.class_name == "Iron Warrior" else "wpn_cyber_katana"
    )
    shop_item = next((x for x in SHOP_ITEMS_DATA if x["id"] == starter_weapon), SHOP_ITEMS_DATA[0])
    cursor.execute("""
        INSERT INTO inventory
        (id, user_id, item_id, item_name, item_type, rarity, stat_bonus_json, is_equipped, icon, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (
        f"inv_{user_id}_{shop_item['id']}",
        user_id,
        shop_item["id"],
        shop_item["name"],
        shop_item["item_type"],
        shop_item["rarity"],
        shop_item["stat_bonus_json"],
        shop_item["icon"],
        shop_item["description"]
    ))

    # 4. Create Active Boss Raid for User
    cursor.execute("""
        INSERT INTO boss_raids
        (id, user_id, name, description, avatar_icon, current_hp, max_hp, attack_power, reward_xp, reward_gold, reward_gems)
        VALUES (?, ?, ?, ?, ?, 5000, 5000, 20, 600, 250, 15)
    """, (
        f"boss_{user_id}_1",
        user_id,
        "The Dread Procrastination Demon",
        "A titan spawned from delayed deadlines and unfinished tasks. Attack it by completing quests!",
        "Skull"
    ))

    # 5. Insert starter onboarding quests
    starter_tasks = [
        ("Complete QuestFlow Setup & Character Creation", "Welcome to QuestFlow! Explore your character sheet and stats.", "Quest", "intellect", "easy", "high"),
        ("Drink 2L Water Today", "Boost your hydration and daily vitality.", "Habit", "vitality", "trivial", "medium"),
        ("Do 20 Pushups or a Quick Stretch", "Physical workout to boost strength stats.", "Daily", "strength", "easy", "medium")
    ]
    for title, desc, cat, attr, diff, prio in starter_tasks:
        t_id = f"task_{user_id}_{uuid.uuid4().hex[:6]}"
        cursor.execute("""
            INSERT INTO tasks (id, user_id, title, description, category, attribute_tag, difficulty, priority, xp_reward, gold_reward, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 30, 12, ?)
        """, (t_id, user_id, title, desc, cat, attr, diff, prio, date.today().isoformat()))

    conn.commit()

    # Fetch newly created user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats_row = dict(cursor.fetchone())
    conn.close()

    del user_row["password_hash"]
    del user_row["salt"]

    return {
        "token": user_id,
        "user": user_row,
        "character": stats_row,
        "message": f"Welcome Adventurer {req.username}! Your journey begins now."
    }

@app.post("/api/auth/login")
def login(req: UserLoginRequest):
    """Authenticate with email and password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (req.email.lower(),))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user = dict(user_row)
    if not verify_password(req.password, user["password_hash"], user["salt"]):
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Update Streak if needed
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user["id"],))
    stats_row = dict(cursor.fetchone())

    new_streak, today_str = calculate_streak_update(stats_row.get("last_active_date"), stats_row.get("streak_count", 1))
    cursor.execute("""
        UPDATE character_stats
        SET streak_count = ?, last_active_date = ?
        WHERE user_id = ?
    """, (new_streak, today_str, user["id"]))
    conn.commit()

    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user["id"],))
    updated_stats = dict(cursor.fetchone())
    conn.close()

    del user["password_hash"]
    del user["salt"]

    return {
        "token": user["id"],
        "user": user,
        "character": updated_stats,
        "message": f"Welcome back, {user['username']}!"
    }

@app.post("/api/auth/demo-login")
def demo_login(req: DemoLoginRequest):
    """1-Click Instant login with pre-configured persona."""
    persona_map = {
        "code_mage": "usr_alex_chen",
        "paladin": "usr_sarah_lin",
        "cyber_rogue": "usr_marcus_vance",
        "alex_chen": "usr_alex_chen",
        "sarah_lin": "usr_sarah_lin",
        "marcus_vance": "usr_marcus_vance"
    }
    user_id = persona_map.get(req.persona.lower(), "usr_alex_chen")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()

    if not user_row:
        # If DB not seeded, seed now
        conn.close()
        seed_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()

    user = dict(user_row)
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())
    conn.close()

    del user["password_hash"]
    del user["salt"]

    return {
        "token": user["id"],
        "user": user,
        "character": stats,
        "message": f"Signed in as Demo Persona: {user['username']} ({user['class_name']})"
    }

@app.get("/api/auth/me")
def get_me(user_id: str = Depends(get_current_user_id)):
    """Retrieve currently authenticated user and character stats."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")

    user = dict(user_row)
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())
    conn.close()

    del user["password_hash"]
    del user["salt"]

    return {
        "user": user,
        "character": stats
    }

# ---------------------------------------------------------------------------
# Task CRUD & Progression Engine Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/tasks")
def get_tasks(
    category: Optional[str] = None,
    attribute_tag: Optional[str] = None,
    is_completed: Optional[int] = None,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List all tasks for current authenticated user with filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)
    if attribute_tag and attribute_tag.lower() != 'all':
        query += " AND attribute_tag = ?"
        params.append(attribute_tag.lower())
    if is_completed is not None:
        query += " AND is_completed = ?"
        params.append(is_completed)
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY is_completed ASC, priority = 'urgent' DESC, priority = 'high' DESC, created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["subtasks"] = json.loads(d["subtasks_json"]) if d.get("subtasks_json") else []
        except Exception:
            d["subtasks"] = []
        results.append(d)

    return results

@app.post("/api/tasks")
def create_task(req: TaskCreateRequest, user_id: str = Depends(get_current_user_id)):
    """Create a new task and compute non-linear XP and Gold rewards."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user streak and class for reward calculation
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats_row = cursor.fetchone()
    streak = stats_row["streak_count"] if stats_row else 1

    cursor.execute("SELECT class_name FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    class_name = user_row["class_name"] if user_row else "Code Mage"

    rewards = calculate_task_rewards(
        difficulty=req.difficulty,
        streak_count=streak,
        character_class=class_name,
        attribute_tag=req.attribute_tag
    )

    task_id = f"task_{user_id}_{uuid.uuid4().hex[:8]}"
    subtasks_str = json.dumps(req.subtasks or [])

    cursor.execute("""
        INSERT INTO tasks 
        (id, user_id, title, description, category, attribute_tag, difficulty, priority,
         xp_reward, gold_reward, is_completed, due_date, subtasks_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (
        task_id,
        user_id,
        req.title,
        req.description or "",
        req.category,
        req.attribute_tag.lower(),
        req.difficulty.lower(),
        req.priority.lower(),
        rewards["xp"],
        rewards["gold"],
        req.due_date,
        subtasks_str
    ))
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    created = dict(cursor.fetchone())
    created["subtasks"] = json.loads(created["subtasks_json"])
    conn.close()

    return created

@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, req: TaskUpdateRequest, user_id: str = Depends(get_current_user_id)):
    """Update task details and recalculate rewards if difficulty changed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found or not owned by user.")

    task = dict(existing)
    title = req.title if req.title is not None else task["title"]
    description = req.description if req.description is not None else task["description"]
    category = req.category if req.category is not None else task["category"]
    attribute_tag = req.attribute_tag if req.attribute_tag is not None else task["attribute_tag"]
    difficulty = req.difficulty if req.difficulty is not None else task["difficulty"]
    priority = req.priority if req.priority is not None else task["priority"]
    due_date = req.due_date if req.due_date is not None else task["due_date"]
    subtasks_str = json.dumps(req.subtasks) if req.subtasks is not None else task["subtasks_json"]

    # Recalculate rewards
    rewards = calculate_task_rewards(difficulty=difficulty, attribute_tag=attribute_tag)

    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, category = ?, attribute_tag = ?, difficulty = ?,
            priority = ?, due_date = ?, subtasks_json = ?, xp_reward = ?, gold_reward = ?
        WHERE id = ? AND user_id = ?
    """, (
        title, description, category, attribute_tag.lower(), difficulty.lower(),
        priority.lower(), due_date, subtasks_str, rewards["xp"], rewards["gold"],
        task_id, user_id
    ))
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated = dict(cursor.fetchone())
    updated["subtasks"] = json.loads(updated["subtasks_json"])
    conn.close()

    return updated

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a task owned by user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found.")
    conn.commit()
    conn.close()
    return {"message": "Task deleted successfully.", "task_id": task_id}

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Complete task and trigger the Core RPG Progression Loop:
    - Grant XP & Gold (with streak & equipment boosts)
    - Process Level Up check
    - Increase specific attribute point (Intellect, Strength, etc.)
    - Deal attack damage to active Boss Raid
    - Roll loot drops
    - Advance streak
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    task_row = cursor.fetchone()
    if not task_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found.")
    task = dict(task_row)

    if task["is_completed"]:
        conn.close()
        return {"message": "Task already completed."}

    # Fetch User & Character Stats
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())

    # 1. Update streak
    new_streak, today_str = calculate_streak_update(stats.get("last_active_date"), stats.get("streak_count", 1))

    # 2. Calculate rewards
    reward_calc = calculate_task_rewards(
        difficulty=task["difficulty"],
        streak_count=new_streak,
        character_class=user["class_name"],
        attribute_tag=task["attribute_tag"]
    )
    xp_gained = reward_calc["xp"]
    gold_gained = reward_calc["gold"]
    boss_damage = reward_calc["boss_damage"]
    stat_gain = reward_calc["stat_gain"]

    # 3. Process XP and Level Up
    new_level, new_xp, next_level_xp, leveled_up, levels_gained = process_xp_gain(
        current_level=stats["level"],
        current_xp=stats["current_xp"],
        xp_to_add=xp_gained
    )

    # 4. Attribute increment
    attr_key = task["attribute_tag"].lower()
    current_attr_val = stats.get(attr_key, 10) + stat_gain

    # 5. Damage active Boss
    cursor.execute("SELECT * FROM boss_raids WHERE user_id = ? AND is_defeated = 0 ORDER BY created_at DESC LIMIT 1", (user_id,))
    boss_row = cursor.fetchone()
    boss_defeated = False
    new_boss_hp = 0
    boss_name = "Raid Boss"
    boss_rewards = None

    if boss_row:
        boss = dict(boss_row)
        boss_name = boss["name"]
        new_boss_hp = max(0, boss["current_hp"] - boss_damage)
        if new_boss_hp == 0:
            boss_defeated = True
            cursor.execute("""
                UPDATE boss_raids
                SET current_hp = 0, is_defeated = 1
                WHERE id = ?
            """, (boss["id"],))
            # Award boss defeat bonus
            gold_gained += boss["reward_gold"]
            xp_gained += boss["reward_xp"]
            boss_rewards = {
                "xp": boss["reward_xp"],
                "gold": boss["reward_gold"],
                "gems": boss["reward_gems"],
                "name": boss["name"]
            }
            # Spawn next tougher boss!
            next_boss_id = f"boss_{user_id}_{uuid.uuid4().hex[:6]}"
            cursor.execute("""
                INSERT INTO boss_raids
                (id, user_id, name, description, avatar_icon, current_hp, max_hp, attack_power, reward_xp, reward_gold, reward_gems)
                VALUES (?, ?, ?, ?, ?, 8000, 8000, 35, 1000, 450, 25)
            """, (
                next_boss_id,
                user_id,
                "The Deadline Leviathan & Burnout Behemoth",
                "A gargantuan dragon fueled by scope creep and procrastinated sprints.",
                "Flame"
            ))
        else:
            cursor.execute("UPDATE boss_raids SET current_hp = ? WHERE id = ?", (new_boss_hp, boss["id"]))

    # 6. Loot Roll
    loot_drop = roll_random_loot(new_level)
    gems_gained = loot_drop["amount"] if loot_drop and loot_drop.get("type") == "GEMS" else 0

    # 7. Update Stats in Database
    new_gold = stats["gold"] + gold_gained
    new_gems = stats["gems"] + gems_gained
    new_tasks_completed = stats.get("tasks_completed_count", 0) + 1
    new_boss_damage_total = stats.get("boss_damage_dealt", 0) + boss_damage

    # Dynamic attribute column update
    valid_attrs = ['intellect', 'strength', 'agility', 'vitality', 'charisma']
    if attr_key in valid_attrs:
        cursor.execute(f"""
            UPDATE character_stats
            SET level = ?, current_xp = ?, next_level_xp = ?, gold = ?, gems = ?,
                streak_count = ?, last_active_date = ?, tasks_completed_count = ?,
                boss_damage_dealt = ?, {attr_key} = ?
            WHERE user_id = ?
        """, (
            new_level, new_xp, next_level_xp, new_gold, new_gems,
            new_streak, today_str, new_tasks_completed, new_boss_damage_total,
            current_attr_val, user_id
        ))
    else:
        cursor.execute("""
            UPDATE character_stats
            SET level = ?, current_xp = ?, next_level_xp = ?, gold = ?, gems = ?,
                streak_count = ?, last_active_date = ?, tasks_completed_count = ?,
                boss_damage_dealt = ?
            WHERE user_id = ?
        """, (
            new_level, new_xp, next_level_xp, new_gold, new_gems,
            new_streak, today_str, new_tasks_completed, new_boss_damage_total, user_id
        ))

    # 8. Mark Task Completed
    now_iso = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE tasks
        SET is_completed = 1, completed_at = ?
        WHERE id = ?
    """, (now_iso, task_id))

    # 9. Activity Log
    cursor.execute("""
        INSERT INTO activity_logs (id, user_id, action_type, message, xp_gained, gold_gained, attribute_increased)
        VALUES (?, ?, 'TASK_COMPLETED', ?, ?, ?, ?)
    """, (
        f"act_{uuid.uuid4().hex[:8]}",
        user_id,
        f"Completed Quest: '{task['title']}' (+{xp_gained} XP, +{gold_gained} Gold)",
        xp_gained,
        gold_gained,
        attr_key
    ))

    if leveled_up:
        cursor.execute("""
            INSERT INTO activity_logs (id, user_id, action_type, message, xp_gained)
            VALUES (?, ?, 'LEVEL_UP', ?, 0)
        """, (
            f"act_{uuid.uuid4().hex[:8]}",
            user_id,
            f"🎉 LEVEL UP! Reached Level {new_level}! Character attributes bolstered!"
        ))

    conn.commit()

    # Fetch updated state
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    updated_stats = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated_task = dict(cursor.fetchone())
    updated_task["subtasks"] = json.loads(updated_task["subtasks_json"])
    conn.close()

    return {
        "task": updated_task,
        "xp_gained": xp_gained,
        "gold_gained": gold_gained,
        "gems_gained": gems_gained,
        "leveled_up": leveled_up,
        "new_level": new_level,
        "attribute_increased": attr_key,
        "stat_gain": stat_gain,
        "boss_damage": boss_damage,
        "boss_name": boss_name,
        "boss_hp_remaining": new_boss_hp,
        "boss_defeated": boss_defeated,
        "boss_rewards": boss_rewards,
        "loot_drop": loot_drop,
        "character": updated_stats
    }

@app.post("/api/tasks/{task_id}/uncomplete")
def uncomplete_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    """Revert a completed task."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET is_completed = 0, completed_at = NULL
        WHERE id = ? AND user_id = ?
    """, (task_id, user_id))
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = dict(cursor.fetchone())
    task["subtasks"] = json.loads(task["subtasks_json"])
    conn.close()
    return task

# ---------------------------------------------------------------------------
# Character & Inventory Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/character")
def get_character_sheet(user_id: str = Depends(get_current_user_id)):
    """Return complete character sheet, radar stats, equipment bonuses."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")
    user = dict(user_row)
    del user["password_hash"]
    del user["salt"]

    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())

    # Fetch equipped inventory items to compute gear bonuses
    cursor.execute("SELECT * FROM inventory WHERE user_id = ? AND is_equipped = 1", (user_id,))
    equipped_items = [dict(r) for r in cursor.fetchall()]

    gear_bonuses = {"intellect": 0, "strength": 0, "agility": 0, "vitality": 0, "charisma": 0, "boss_atk": 0}
    for item in equipped_items:
        try:
            bonuses = json.loads(item["stat_bonus_json"])
            for k, v in bonuses.items():
                if k in gear_bonuses:
                    gear_bonuses[k] += v
        except Exception:
            pass

    # Total combined stats
    total_stats = {
        "intellect": stats["intellect"] + gear_bonuses["intellect"],
        "strength": stats["strength"] + gear_bonuses["strength"],
        "agility": stats["agility"] + gear_bonuses["agility"],
        "vitality": stats["vitality"] + gear_bonuses["vitality"],
        "charisma": stats["charisma"] + gear_bonuses["charisma"],
    }

    # Radar Chart Normalized Data (Max 100)
    radar_data = [
        {"attribute": "Intellect", "value": min(100, total_stats["intellect"]), "base": stats["intellect"], "gear": gear_bonuses["intellect"]},
        {"attribute": "Strength", "value": min(100, total_stats["strength"]), "base": stats["strength"], "gear": gear_bonuses["strength"]},
        {"attribute": "Agility", "value": min(100, total_stats["agility"]), "base": stats["agility"], "gear": gear_bonuses["agility"]},
        {"attribute": "Vitality", "value": min(100, total_stats["vitality"]), "base": stats["vitality"], "gear": gear_bonuses["vitality"]},
        {"attribute": "Charisma", "value": min(100, total_stats["charisma"]), "base": stats["charisma"], "gear": gear_bonuses["charisma"]},
    ]

    conn.close()

    return {
        "user": user,
        "base_stats": stats,
        "gear_bonuses": gear_bonuses,
        "total_stats": total_stats,
        "radar_data": radar_data,
        "equipped_items": equipped_items
    }

@app.get("/api/inventory")
def get_inventory(user_id: str = Depends(get_current_user_id)):
    """List all inventory items owned by user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE user_id = ? ORDER BY purchased_at DESC", (user_id,))
    items = []
    for r in cursor.fetchall():
        d = dict(r)
        try:
            d["stat_bonus"] = json.loads(d["stat_bonus_json"])
        except Exception:
            d["stat_bonus"] = {}
        items.append(d)
    conn.close()
    return items

@app.post("/api/inventory/equip")
def equip_item(req: EquipItemRequest, user_id: str = Depends(get_current_user_id)):
    """Equip or unequip an inventory item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE id = ? AND user_id = ?", (req.inventory_id, user_id))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not in user inventory.")
    item = dict(item_row)

    if req.equip:
        # Unequip any existing item of the same type
        cursor.execute("""
            UPDATE inventory
            SET is_equipped = 0
            WHERE user_id = ? AND item_type = ?
        """, (user_id, item["item_type"]))

        cursor.execute("UPDATE inventory SET is_equipped = 1 WHERE id = ?", (req.inventory_id,))
    else:
        cursor.execute("UPDATE inventory SET is_equipped = 0 WHERE id = ?", (req.inventory_id,))

    conn.commit()
    conn.close()
    return {"message": f"{'Equipped' if req.equip else 'Unequipped'} {item['item_name']}.", "item_id": req.inventory_id}

@app.post("/api/inventory/use")
def use_item(req: UseItemRequest, user_id: str = Depends(get_current_user_id)):
    """Consume a potion or consumable."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE id = ? AND user_id = ?", (req.inventory_id, user_id))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not in user inventory.")
    item = dict(item_row)

    bonuses = json.loads(item.get("stat_bonus_json") or "{}")

    # Fetch stats
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())

    xp_gain = bonuses.get("instant_xp", 0)
    streak_freeze = bonuses.get("streak_freeze", 0)

    new_level, new_xp, next_level_xp, leveled_up, _ = process_xp_gain(
        stats["level"], stats["current_xp"], xp_gain
    )

    new_streak_freeze = stats.get("streak_freeze_count", 0) + streak_freeze

    cursor.execute("""
        UPDATE character_stats
        SET level = ?, current_xp = ?, next_level_xp = ?, streak_freeze_count = ?
        WHERE user_id = ?
    """, (new_level, new_xp, next_level_xp, new_streak_freeze, user_id))

    # Remove consumable from inventory
    cursor.execute("DELETE FROM inventory WHERE id = ?", (req.inventory_id,))
    conn.commit()
    conn.close()

    return {
        "message": f"Used {item['item_name']}! Gained +{xp_gain} XP.",
        "leveled_up": leveled_up,
        "new_level": new_level
    }

# ---------------------------------------------------------------------------
# Shop & Economy Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/shop")
def get_shop_catalogue(user_id: str = Depends(get_current_user_id)):
    """Return catalogue with user owned status and affordability."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM shop_items ORDER BY min_level ASC, price_gold ASC")
    shop_rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT item_id FROM inventory WHERE user_id = ?", (user_id,))
    owned_ids = set(r["item_id"] for r in cursor.fetchall())

    cursor.execute("SELECT gold, gems, level FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())

    results = []
    for item in shop_rows:
        try:
            item["stat_bonus"] = json.loads(item["stat_bonus_json"])
        except Exception:
            item["stat_bonus"] = {}
        item["is_owned"] = item["id"] in owned_ids
        item["can_afford_gold"] = stats["gold"] >= item["price_gold"]
        item["can_afford_gems"] = stats["gems"] >= item["price_gems"]
        item["is_level_locked"] = stats["level"] < item["min_level"]
        results.append(item)

    conn.close()
    return results

@app.post("/api/shop/buy")
def buy_shop_item(req: BuyShopItemRequest, user_id: str = Depends(get_current_user_id)):
    """Purchase gear or consumable from the armory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM shop_items WHERE id = ?", (req.item_id,))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Shop item does not exist.")
    item = dict(item_row)

    # Check stats
    cursor.execute("SELECT * FROM character_stats WHERE user_id = ?", (user_id,))
    stats = dict(cursor.fetchone())

    if stats["level"] < item["min_level"]:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Requires Level {item['min_level']} to purchase.")

    # Deduct currency
    if req.currency == "gems":
        if stats["gems"] < item["price_gems"]:
            conn.close()
            raise HTTPException(status_code=400, detail="Not enough Soul Gems.")
        new_gems = stats["gems"] - item["price_gems"]
        new_gold = stats["gold"]
    else:
        if stats["gold"] < item["price_gold"]:
            conn.close()
            raise HTTPException(status_code=400, detail="Not enough Gold coins.")
        new_gold = stats["gold"] - item["price_gold"]
        new_gems = stats["gems"]

    # Deduct funds
    cursor.execute("UPDATE character_stats SET gold = ?, gems = ? WHERE user_id = ?", (new_gold, new_gems, user_id))

    # Add to inventory
    inv_id = f"inv_{user_id}_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO inventory
        (id, user_id, item_id, item_name, item_type, rarity, stat_bonus_json, is_equipped, icon, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (
        inv_id,
        user_id,
        item["id"],
        item["name"],
        item["item_type"],
        item["rarity"],
        item["stat_bonus_json"],
        item["icon"],
        item["description"]
    ))

    # Activity Log
    cursor.execute("""
        INSERT INTO activity_logs (id, user_id, action_type, message)
        VALUES (?, ?, 'ITEM_BOUGHT', ?)
    """, (
        f"act_{uuid.uuid4().hex[:8]}",
        user_id,
        f"Purchased from Armory: {item['name']} ({item['rarity'].upper()})"
    ))

    conn.commit()
    conn.close()

    return {
        "message": f"Successfully purchased {item['name']}!",
        "item": item,
        "new_gold": new_gold,
        "new_gems": new_gems
    }

# ---------------------------------------------------------------------------
# Boss Arena Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/boss")
def get_boss(user_id: str = Depends(get_current_user_id)):
    """Retrieve current active boss raid status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM boss_raids 
        WHERE user_id = ? 
        ORDER BY is_defeated ASC, created_at DESC 
        LIMIT 1
    """, (user_id,))
    boss_row = cursor.fetchone()

    if not boss_row:
        # Create default boss if none found
        boss_id = f"boss_{user_id}_1"
        cursor.execute("""
            INSERT INTO boss_raids
            (id, user_id, name, description, avatar_icon, current_hp, max_hp, attack_power, reward_xp, reward_gold, reward_gems)
            VALUES (?, ?, ?, ?, ?, 5000, 5000, 20, 600, 250, 15)
        """, (
            boss_id,
            user_id,
            "The Dread Procrastination Demon",
            "A titan spawned from delayed deadlines and unfinished tasks.",
            "Skull"
        ))
        conn.commit()
        cursor.execute("SELECT * FROM boss_raids WHERE id = ?", (boss_id,))
        boss_row = cursor.fetchone()

    boss = dict(boss_row)
    conn.close()
    return boss

# ---------------------------------------------------------------------------
# Analytics & Streak Matrix Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/analytics")
def get_analytics(user_id: str = Depends(get_current_user_id)):
    """Return 30-day streak heat map and attribute breakdown."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get attribute breakdown of completed tasks
    cursor.execute("""
        SELECT attribute_tag, COUNT(*) as count, SUM(xp_reward) as total_xp
        FROM tasks
        WHERE user_id = ? AND is_completed = 1
        GROUP BY attribute_tag
    """, (user_id,))
    attr_breakdown = [dict(r) for r in cursor.fetchall()]

    # Generate 30-day activity map
    today = date.today()
    days_data = []
    for i in range(29, -1, -1):
        day_date = today - timedelta(days=i)
        day_str = day_date.isoformat()
        cursor.execute("""
            SELECT COUNT(*) as completed_count
            FROM tasks
            WHERE user_id = ? AND is_completed = 1 AND DATE(completed_at) = ?
        """, (user_id, day_str))
        count = cursor.fetchone()["completed_count"]
        days_data.append({
            "date": day_str,
            "day": day_date.strftime("%a"),
            "completed_tasks": count,
            "level": min(4, count)
        })

    # Recent activity logs
    cursor.execute("""
        SELECT * FROM activity_logs 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 15
    """, (user_id,))
    logs = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "attribute_breakdown": attr_breakdown,
        "activity_matrix": days_data,
        "recent_logs": logs
    }
