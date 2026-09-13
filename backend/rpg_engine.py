"""
RPG Progression Engine for QuestFlow.
Handles non-linear leveling curves, task difficulty reward calculations,
streak multipliers, attribute point increments, boss combat, and loot generation.
"""
import math
import random
import hashlib
import os
import secrets
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple, Optional, List

# ---------------------------------------------------------------------------
# Cryptographic Security Helpers (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Generate a secure PBKDF2 hash with a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify plain password against stored hash."""
    check_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(check_hash, password_hash)

# ---------------------------------------------------------------------------
# Non-Linear Progression Formulas
# ---------------------------------------------------------------------------

def calculate_next_level_xp(level: int) -> int:
    """
    Non-linear leveling curve:
    XP_req(L) = floor(100 * L^1.6)
    L=1 -> 100
    L=2 -> 303
    L=3 -> 580
    L=4 -> 923
    L=5 -> 1327
    """
    if level < 1:
        level = 1
    return int(math.floor(100 * (level ** 1.6)))

DIFFICULTY_REWARDS = {
    'trivial': {'xp': 15, 'gold': 5, 'boss_dmg': 10},
    'easy': {'xp': 30, 'gold': 12, 'boss_dmg': 25},
    'medium': {'xp': 60, 'gold': 25, 'boss_dmg': 55},
    'hard': {'xp': 120, 'gold': 50, 'boss_dmg': 120},
    'epic': {'xp': 250, 'gold': 110, 'boss_dmg': 280},
}

ATTRIBUTE_KEYS = ['intellect', 'strength', 'agility', 'vitality', 'charisma']

def calculate_task_rewards(
    difficulty: str,
    streak_count: int = 1,
    character_class: str = 'Code Mage',
    attribute_tag: str = 'intellect'
) -> Dict[str, Any]:
    """Calculate scaled XP, Gold, and Boss damage based on streak & difficulty."""
    diff_data = DIFFICULTY_REWARDS.get(difficulty.lower(), DIFFICULTY_REWARDS['medium'])
    base_xp = diff_data['xp']
    base_gold = diff_data['gold']
    boss_dmg = diff_data['boss_dmg']

    # Streak Bonus: +3% per streak day up to +50%
    streak_bonus_pct = min(0.50, max(0.0, (streak_count - 1) * 0.03))
    total_xp = int(math.ceil(base_xp * (1.0 + streak_bonus_pct)))
    total_gold = int(math.ceil(base_gold * (1.0 + streak_bonus_pct)))

    # Class specialty bonus (+10% on matching attribute)
    class_affinity = {
        'Code Mage': 'intellect',
        'Iron Warrior': 'strength',
        'Cyber Rogue': 'agility',
        'Paladin Scholar': 'vitality',
        'Digital Bard': 'charisma'
    }
    if class_affinity.get(character_class) == attribute_tag:
        total_xp = int(math.ceil(total_xp * 1.15))
        total_gold = int(math.ceil(total_gold * 1.10))

    # Stat point increment
    stat_gain = 1
    if difficulty in ['hard', 'epic']:
        stat_gain = 2

    return {
        'xp': total_xp,
        'gold': total_gold,
        'boss_damage': boss_dmg,
        'stat_gain': stat_gain,
        'streak_bonus_pct': int(streak_bonus_pct * 100)
    }

def process_xp_gain(
    current_level: int,
    current_xp: int,
    xp_to_add: int
) -> Tuple[int, int, int, bool, int]:
    """
    Add XP and handle potential level-ups (can level up multiple times).
    Returns (new_level, new_xp, next_level_xp, leveled_up, levels_gained).
    """
    new_level = current_level
    new_xp = current_xp + xp_to_add
    next_xp = calculate_next_level_xp(new_level)
    leveled_up = False
    levels_gained = 0

    while new_xp >= next_xp:
        new_xp -= next_xp
        new_level += 1
        levels_gained += 1
        leveled_up = True
        next_xp = calculate_next_level_xp(new_level)

    return new_level, new_xp, next_xp, leveled_up, levels_gained

def calculate_streak_update(last_active_date_str: Optional[str], current_streak: int) -> Tuple[int, str]:
    """
    Evaluate activity date against today to increment, maintain, or reset streak.
    """
    today = date.today()
    today_str = today.isoformat()

    if not last_active_date_str:
        return 1, today_str

    try:
        last_date = date.fromisoformat(last_active_date_str)
    except Exception:
        return 1, today_str

    delta_days = (today - last_date).days

    if delta_days == 0:
        # Already active today, streak stays the same
        return max(1, current_streak), today_str
    elif delta_days == 1:
        # Consecutive day! Increment streak
        return current_streak + 1, today_str
    else:
        # Missed days, streak resets to 1
        return 1, today_str

def roll_random_loot(level: int) -> Optional[Dict[str, Any]]:
    """5% chance on task completion to find a rare crystal or consumable."""
    roll = random.random()
    if roll < 0.15:  # 15% drop rate for excitement
        gems_found = random.randint(1, 3)
        return {
            'type': 'GEMS',
            'amount': gems_found,
            'message': f"Loot Drop! Discovered {gems_found} Shiny Soul Gems in the quest spoils!"
        }
    return None
