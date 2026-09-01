from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.notification import NotificationSeverity

class NotificationBase(BaseModel):
    title: str
    message: str
    severity: NotificationSeverity = NotificationSeverity.INFO
    link: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
