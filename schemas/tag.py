from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from schemas.base import UserCompact, WorkspaceCompact, TagCompact


class TagBase(TagCompact):
    """Tag base schema"""
    color: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class TagResponse(TagBase):
    """Full tag response"""
    created_at: Optional[datetime] = None
    followers: Optional[List[UserCompact]] = None
    workspace: Optional[WorkspaceCompact] = None
    permalink_url: Optional[str] = None

    class Config:
        from_attributes = True


class TagRequest(BaseModel):
    """Tag create request"""
    name: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    followers: Optional[List[str]] = None
    workspace: Optional[str] = None

    class Config:
        from_attributes = True


class TagUpdateRequest(BaseModel):
    """Tag update request"""
    name: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class TagResponseWrapper(BaseModel):
    """Tag response wrapper"""
    data: TagResponse

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Tag list response"""
    data: List[TagCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

