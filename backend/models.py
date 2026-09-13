"""
Pydantic data models for ResolveFlow API requests and responses.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class RunAgentRequest(BaseModel):
    ticket_id: str
    speed_factor: Optional[float] = Field(default=0.5, ge=0.05, le=2.0)

class CustomTicketRequest(BaseModel):
    customer_id: str = "CUST-101"
    order_id: Optional[str] = "ORD-1042"
    title: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10)
    issue_type: str = "DAMAGED_ITEM"
    priority: str = "HIGH"

class PolicyOverrideRequest(BaseModel):
    category: str
    rules: Dict[str, Any]

class InventoryUpdateRequest(BaseModel):
    product_id: str
    stock_quantity: int = Field(..., ge=0)
