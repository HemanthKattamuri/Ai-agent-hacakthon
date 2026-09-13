"""
Integration tests for QuestFlow API endpoints and RPG Progression Engine.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from main import app
from seed import seed_database
from database import get_db_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Reset all tables for test consistency
    cursor.execute("DELETE FROM activity_logs")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM boss_raids")
    cursor.execute("DELETE FROM character_stats")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM shop_items")
    conn.commit()
    conn.close()
    seed_database()

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_demo_login():
    res = client.post("/api/auth/demo-login", json={"persona": "code_mage"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["username"] == "AlexChen"
    assert data["character"]["level"] == 4
    assert data["character"]["streak_count"] == 7

def test_signup_and_isolation():
    uid = uuid.uuid4().hex[:6]
    # 1. Signup new user
    res = client.post("/api/auth/signup", json={
        "username": f"DragonSlayer_{uid}",
        "email": f"slayer_{uid}@test.com",
        "password": "strongpassword123",
        "class_name": "Iron Warrior"
    })
    assert res.status_code == 200
    data = res.json()
    token = data["token"]
    assert data["character"]["level"] == 1

    # 2. Create task for new user
    headers = {"X-User-Id": token}
    task_res = client.post("/api/tasks", headers=headers, json={
        "title": "Conquer 100 Squats",
        "category": "Daily",
        "attribute_tag": "strength",
        "difficulty": "hard",
        "priority": "urgent"
    })
    assert task_res.status_code == 200
    created_task = task_res.json()
    assert created_task["xp_reward"] >= 120

    # 3. Complete task and verify RPG progression
    comp_res = client.post(f"/api/tasks/{created_task['id']}/complete", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["xp_gained"] >= 120
    assert comp_data["attribute_increased"] == "strength"
    assert comp_data["boss_damage"] > 0

    # 4. Verify user only sees their own tasks
    tasks_res = client.get("/api/tasks", headers=headers)
    assert tasks_res.status_code == 200
    user_tasks = tasks_res.json()
    assert any(t["id"] == created_task["id"] for t in user_tasks)

def test_shop_and_inventory():
    headers = {"X-User-Id": "usr_alex_chen"}
    shop_res = client.get("/api/shop", headers=headers)
    assert shop_res.status_code == 200
    items = shop_res.json()
    assert len(items) > 5

    potion = next((x for x in items if x["item_type"] == "potion" and not x["is_owned"]), items[0])
    buy_res = client.post("/api/shop/buy", headers=headers, json={"item_id": potion["id"], "currency": "gold"})
    assert buy_res.status_code == 200

    inv_res = client.get("/api/inventory", headers=headers)
    assert inv_res.status_code == 200
    inv_items = inv_res.json()
    assert any(x["item_id"] == potion["id"] for x in inv_items)

def test_analytics():
    headers = {"X-User-Id": "usr_alex_chen"}
    res = client.get("/api/analytics", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "activity_matrix" in data
    assert len(data["activity_matrix"]) == 30
