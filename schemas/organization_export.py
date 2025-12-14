from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.base import AsanaResource, WorkspaceCompact


class OrganizationExportResponse(AsanaResource):
    """Organization export response"""
    state: Optional[str] = None
    download_url: Optional[str] = None
    organization: Optional[WorkspaceCompact] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationExportRequest(BaseModel):
    """Organization export request"""
    organization: str


class OrganizationExportResponseWrapper(BaseModel):
    """Single organization export response wrapper"""
    data: OrganizationExportResponse

