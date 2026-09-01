from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class AutomationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 0

class AutomationRuleCreate(AutomationRuleBase):
    pass

class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None

class AutomationRuleResponse(AutomationRuleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
