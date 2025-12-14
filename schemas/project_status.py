from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from schemas.base import UserCompact


class ProjectStatusCompact(BaseModel):
    """Compact project status representation"""
    gid: str
    resource_type: str
    title: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectStatusBase(ProjectStatusCompact):
    """Project status base"""
    text: Optional[str] = None
    html_text: Optional[str] = None
    color: Optional[str] = None  # "green", "yellow", "red", "blue", "complete"

    class Config:
        from_attributes = True


class ProjectStatusResponse(ProjectStatusBase):
    """Full project status response"""
    author: Optional[UserCompact] = None
    created_at: Optional[datetime] = None
    created_by: Optional[UserCompact] = None
    modified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectStatusRequest(BaseModel):
    """Project status request"""
    text: str
    html_text: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class ProjectStatusResponseWrapper(BaseModel):
    """Project status response wrapper"""
    data: ProjectStatusResponse

    class Config:
        from_attributes = True


class ProjectStatusListResponse(BaseModel):
    """Project status list response"""
    data: list[ProjectStatusCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

