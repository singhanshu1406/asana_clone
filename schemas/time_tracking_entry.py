from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from schemas.base import AsanaResource, UserCompact, ProjectCompact, TaskCompact


class TimeTrackingEntryCompact(AsanaResource):
    """Compact time tracking entry representation"""
    duration_minutes: Optional[int] = None
    entered_on: Optional[date] = None

    class Config:
        from_attributes = True


class TimeTrackingEntryResponse(TimeTrackingEntryCompact):
    """Full time tracking entry response"""
    task: Optional[TaskCompact] = None
    attributable_to: Optional[ProjectCompact] = None
    created_by: Optional[UserCompact] = None
    approval_status: Optional[str] = None
    billable_status: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TimeTrackingEntryRequest(BaseModel):
    """Time tracking entry create/update request"""
    duration_minutes: int
    entered_on: date
    task: str
    attributable_to: Optional[str] = None
    description: Optional[str] = None


class TimeTrackingEntryListResponse(BaseModel):
    """List of time tracking entries"""
    data: List[TimeTrackingEntryResponse]
    next_page: Optional[dict] = None


class TimeTrackingEntryResponseWrapper(BaseModel):
    """Single time tracking entry response wrapper"""
    data: TimeTrackingEntryResponse

