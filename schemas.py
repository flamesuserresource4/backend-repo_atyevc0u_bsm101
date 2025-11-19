"""
Database Schemas for Smart Ledger

Each Pydantic model represents a MongoDB collection. The collection name
is the lowercase of the class name.

We partition all data by a per-device client_id (stored in the browser).
This replaces third-party auth and keeps each user's data isolated.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Bankbalance(BaseModel):
    """
    Collection: "bankbalance"
    One logical row per client_id (we upsert by client_id)
    """
    client_id: str = Field(..., description="Anonymous client identifier")
    amount: Optional[float] = Field(None, ge=0)
    updated_at: Optional[datetime] = None


class Expense(BaseModel):
    """
    Collection: "expense"
    One logical row per client_id
    """
    client_id: str
    amount: Optional[float] = Field(None, ge=0)
    month: Optional[str] = None
    updated_at: Optional[datetime] = None


class Sale(BaseModel):
    """
    Collection: "sale"
    One logical row per client_id
    """
    client_id: str
    amount: Optional[float] = Field(None, ge=0)
    updated_at: Optional[datetime] = None


class Order(BaseModel):
    """
    Collection: "order"
    One logical row per client_id
    """
    client_id: str
    total_orders: Optional[int] = Field(None, ge=0)
    pending: Optional[int] = Field(None, ge=0)
    completed: Optional[int] = Field(None, ge=0)
    updated_at: Optional[datetime] = None


class Reminder(BaseModel):
    """
    Collection: "reminder"
    One logical row per client_id
    """
    client_id: str
    title: Optional[str] = None
    due_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    updated_at: Optional[datetime] = None
