from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from datetime import date, datetime
from schemas.base import (
    UserCompact, TeamCompact, WorkspaceCompact, ProjectCompact,
    CustomFieldCompact, CustomFieldSettingCompact, StatusUpdateCompact,
    ProjectTemplateCompact, ProjectBriefCompact, SectionCompact
)


class ProjectBase(ProjectCompact):
    """Project base schema"""
    archived: Optional[bool] = None
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    current_status: Optional[Any] = None  # Deprecated
    current_status_update: Optional[StatusUpdateCompact] = None
    custom_field_settings: Optional[List[CustomFieldSettingCompact]] = None
    default_view: Optional[str] = None
    due_date: Optional[date] = None  # Deprecated
    due_on: Optional[date] = None
    html_notes: Optional[str] = None
    members: Optional[List[UserCompact]] = None
    modified_at: Optional[datetime] = None
    notes: Optional[str] = None
    public: Optional[bool] = None  # Deprecated
    privacy_setting: Optional[str] = None
    start_on: Optional[date] = None
    default_access_level: Optional[str] = None
    minimum_access_level_for_customization: Optional[str] = None
    minimum_access_level_for_sharing: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Full project response"""
    custom_fields: Optional[List[CustomFieldCompact]] = None
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[UserCompact] = None
    followers: Optional[List[UserCompact]] = None
    owner: Optional[UserCompact] = None
    team: Optional[TeamCompact] = None
    icon: Optional[str] = None
    permalink_url: Optional[str] = None
    project_brief: Optional[ProjectBriefCompact] = None
    created_from_template: Optional[ProjectTemplateCompact] = None
    workspace: Optional[WorkspaceCompact] = None

    class Config:
        from_attributes = True


class ProjectRequest(BaseModel):
    """Project create request"""
    name: Optional[str] = None
    archived: Optional[bool] = None
    color: Optional[str] = None
    default_view: Optional[str] = None
    due_on: Optional[date] = None
    start_on: Optional[date] = None
    html_notes: Optional[str] = None
    notes: Optional[str] = None
    public: Optional[bool] = None
    privacy_setting: Optional[str] = None
    default_access_level: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    followers: Optional[str] = None
    owner: Optional[str] = None
    team: Optional[str] = None
    workspace: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectUpdateRequest(BaseModel):
    """Project update request"""
    name: Optional[str] = None
    archived: Optional[bool] = None
    color: Optional[str] = None
    default_view: Optional[str] = None
    due_on: Optional[date] = None
    start_on: Optional[date] = None
    html_notes: Optional[str] = None
    notes: Optional[str] = None
    privacy_setting: Optional[str] = None
    default_access_level: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    followers: Optional[str] = None
    owner: Optional[str] = None
    team: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectDuplicateRequest(BaseModel):
    """Project duplicate request"""
    name: str
    team: Optional[str] = None
    include: Optional[str] = None
    schedule_dates: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Response wrappers
class ProjectResponseWrapper(BaseModel):
    """Project response wrapper"""
    data: ProjectResponse

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Project list response"""
    data: List[ProjectCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

