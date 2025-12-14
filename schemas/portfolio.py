from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from datetime import date, datetime
from schemas.base import (
    UserCompact, WorkspaceCompact, StatusUpdateCompact,
    CustomFieldCompact, CustomFieldSettingCompact, ProjectTemplateCompact
)


class PortfolioCompact(BaseModel):
    """Compact portfolio representation"""
    gid: str
    resource_type: str
    name: str

    class Config:
        from_attributes = True


class PortfolioBase(PortfolioCompact):
    """Portfolio base schema"""
    archived: Optional[bool] = None
    color: Optional[str] = None
    start_on: Optional[date] = None
    due_on: Optional[date] = None
    default_access_level: Optional[str] = None  # "admin", "editor", "viewer"

    class Config:
        from_attributes = True


class PortfolioResponse(PortfolioBase):
    """Full portfolio response"""
    created_at: Optional[datetime] = None
    created_by: Optional[UserCompact] = None
    custom_field_settings: Optional[List[CustomFieldSettingCompact]] = None
    current_status_update: Optional[StatusUpdateCompact] = None
    custom_fields: Optional[List[CustomFieldCompact]] = None
    members: Optional[List[UserCompact]] = None
    owner: Optional[UserCompact] = None
    workspace: Optional[WorkspaceCompact] = None
    permalink_url: Optional[str] = None
    public: Optional[bool] = None
    privacy_setting: Optional[str] = None  # "public_to_domain", "members_only"
    project_templates: Optional[List[ProjectTemplateCompact]] = None

    class Config:
        from_attributes = True


class PortfolioRequest(BaseModel):
    """Portfolio create request"""
    name: Optional[str] = None
    archived: Optional[bool] = None
    color: Optional[str] = None
    start_on: Optional[date] = None
    due_on: Optional[date] = None
    default_access_level: Optional[str] = None
    workspace: Optional[str] = None
    public: Optional[bool] = None

    class Config:
        from_attributes = True


class PortfolioUpdateRequest(BaseModel):
    """Portfolio update request"""
    name: Optional[str] = None
    archived: Optional[bool] = None
    color: Optional[str] = None
    start_on: Optional[date] = None
    due_on: Optional[date] = None
    default_access_level: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class PortfolioAddItemRequest(BaseModel):
    """Add item to portfolio request"""
    item: str
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None

    class Config:
        from_attributes = True


class PortfolioRemoveItemRequest(BaseModel):
    """Remove item from portfolio request"""
    item: str

    class Config:
        from_attributes = True


# Response wrappers
class PortfolioResponseWrapper(BaseModel):
    """Portfolio response wrapper"""
    data: PortfolioResponse

    class Config:
        from_attributes = True


class PortfolioListResponse(BaseModel):
    """Portfolio list response"""
    data: List[PortfolioCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

