from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime
from schemas.base import UserCompact, ProjectCompact, Like, StatusUpdateCompact


class StatusUpdateBase(StatusUpdateCompact):
    """Status update base"""
    text: str
    html_text: Optional[str] = None
    status_type: str  # "on_track", "at_risk", "off_track", "on_hold", etc.

    class Config:
        from_attributes = True


class StatusUpdateResponse(StatusUpdateBase):
    """Full status update response"""
    author: Optional[UserCompact] = None
    created_at: Optional[datetime] = None
    created_by: Optional[UserCompact] = None
    hearted: Optional[bool] = None
    hearts: Optional[List[Like]] = None
    liked: Optional[bool] = None
    likes: Optional[List[Like]] = None
    reaction_summary: Optional[List[Any]] = None
    modified_at: Optional[datetime] = None
    num_hearts: Optional[int] = None
    num_likes: Optional[int] = None
    parent: Optional[ProjectCompact] = None

    class Config:
        from_attributes = True


class StatusUpdateRequest(BaseModel):
    """Status update create request"""
    text: str
    html_text: Optional[str] = None
    status_type: str
    parent: str

    class Config:
        from_attributes = True


# Response wrappers
class StatusUpdateResponseWrapper(BaseModel):
    """Status update response wrapper"""
    data: StatusUpdateResponse

    class Config:
        from_attributes = True


class StatusUpdateListResponse(BaseModel):
    """Status update list response"""
    data: List[StatusUpdateCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

