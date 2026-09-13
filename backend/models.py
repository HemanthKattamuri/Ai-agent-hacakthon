"""
Pydantic data models for QuestFlow API requests and responses.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    class_name: str = Field(default="Code Mage")
    title: Optional[str] = Field(default="Novice Adventurer")

class UserLoginRequest(BaseModel):
    email: str
    password: str

class DemoLoginRequest(BaseModel):
    persona: str = Field(default="code_mage") # code_mage, iron_warrior, cyber_rogue

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    category: str = Field(default="Quest") # Habit, Daily, Quest, Todo
    attribute_tag: str = Field(default="intellect") # intellect, strength, agility, vitality, charisma
    difficulty: str = Field(default="medium") # trivial, easy, medium, hard, epic
    priority: str = Field(default="medium") # low, medium, high, urgent
    due_date: Optional[str] = None
    subtasks: Optional[List[Dict[str, Any]]] = []

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    attribute_tag: Optional[str] = None
    difficulty: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    subtasks: Optional[List[Dict[str, Any]]] = None

class EquipItemRequest(BaseModel):
    inventory_id: str
    equip: bool = True

class UseItemRequest(BaseModel):
    inventory_id: str

class BuyShopItemRequest(BaseModel):
    item_id: str
    currency: str = "gold" # gold or gems

class UpdateThemeRequest(BaseModel):
    theme: str # cyberpunk, fantasy, solar, void
