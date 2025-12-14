from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import UserCompact, AsanaNamedResource


class EventChange(BaseModel):
    """Change information in an event"""
    field: Optional[str] = None
    action: Optional[str] = None  # "changed", "added", "removed"
    new_value: Optional[Dict[str, Any]] = None
    added_value: Optional[Dict[str, Any]] = None
    removed_value: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    """Event response schema"""
    user: Optional[UserCompact] = None
    resource: Optional[AsanaNamedResource] = None
    type: Optional[str] = None  # Deprecated
    action: str  # "changed", "added", "removed", "deleted", "undeleted"
    parent: Optional[AsanaNamedResource] = None
    created_at: datetime
    change: Optional[EventChange] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """List of events response"""
    data: list[EventResponse]

    class Config:
        from_attributes = True

