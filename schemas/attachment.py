from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from schemas.base import AsanaResource, UserCompact, ProjectCompact, TaskCompact


class AttachmentCompact(AsanaResource):
    """Compact attachment representation"""
    name: Optional[str] = None
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class AttachmentResponse(AttachmentCompact):
    """Full attachment response"""
    connected_to_app: Optional[bool] = None
    created_at: Optional[datetime] = None
    download_url: Optional[str] = None
    host: Optional[str] = None
    permanent_url: Optional[str] = None
    size: Optional[int] = None
    view_url: Optional[str] = None
    parent: Optional[dict] = None  # Can be ProjectCompact, TaskCompact, or ProjectBriefCompact
    created_by: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class AttachmentRequest(BaseModel):
    """Attachment create request"""
    parent: str
    file: Optional[str] = None  # File path or URL
    url: Optional[str] = None
    name: Optional[str] = None
    connect_to_app: Optional[bool] = None
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Attachment list response"""
    data: List[AttachmentCompact]

    class Config:
        from_attributes = True


class AttachmentResponseWrapper(BaseModel):
    """Attachment response wrapper"""
    data: AttachmentResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

