from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from datetime import datetime


class ResourceExportFilters(BaseModel):
    """Resource export filters"""
    assigned_by_any: Optional[List[str]] = None
    assignee_any: Optional[List[str]] = None
    commented_on_by_any: Optional[List[str]] = None
    created_at_after: Optional[datetime] = None
    created_at_before: Optional[datetime] = None
    created_by_any: Optional[List[str]] = None
    followers_any: Optional[List[str]] = None
    liked_by_any: Optional[List[str]] = None
    modified_at_after: Optional[datetime] = None
    modified_at_before: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResourceExportRequestParameter(BaseModel):
    """Resource export request parameter"""
    resource_type: str
    filters: Optional[ResourceExportFilters] = None
    fields: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ResourceExportRequest(BaseModel):
    """Resource export request"""
    workspace: str
    export_request_parameters: Optional[Dict[str, ResourceExportRequestParameter]] = None

    class Config:
        from_attributes = True


class ResourceExportCompact(BaseModel):
    """Compact resource export representation"""
    gid: str
    resource_type: str
    created_at: Optional[datetime] = None
    download_url: Optional[str] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResourceExportResponse(BaseModel):
    """Resource export response (job format)"""
    gid: str
    resource_type: str = "job"
    resource_subtype: Optional[str] = "export_request"
    status: Optional[str] = None
    new_resource_export: Optional[ResourceExportCompact] = None

    class Config:
        from_attributes = True


# Response wrappers
class ResourceExportResponseWrapper(BaseModel):
    """Resource export response wrapper"""
    data: ResourceExportResponse

    class Config:
        from_attributes = True


class ResourceExportCompactResponseWrapper(BaseModel):
    """Resource export compact response wrapper"""
    data: ResourceExportCompact

    class Config:
        from_attributes = True

