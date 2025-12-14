from pydantic import BaseModel
from typing import Optional, List
from schemas.base import UserCompact, TeamCompact, ProjectTemplateCompact


class DateVariableCompact(BaseModel):
    """Date variable compact"""
    gid: str
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateRole(BaseModel):
    """Template role"""
    gid: str
    resource_type: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectTemplateBase(ProjectTemplateCompact):
    """Project template base"""
    description: Optional[str] = None
    html_description: Optional[str] = None
    public: Optional[bool] = None
    owner: Optional[UserCompact] = None
    team: Optional[TeamCompact] = None
    requested_dates: Optional[List[DateVariableCompact]] = None
    color: Optional[str] = None
    requested_roles: Optional[List[TemplateRole]] = None

    class Config:
        from_attributes = True


class ProjectTemplateResponse(ProjectTemplateBase):
    """Full project template response"""
    class Config:
        from_attributes = True


class DateVariableRequest(BaseModel):
    """Date variable request"""
    gid: str
    value: Optional[str] = None

    class Config:
        from_attributes = True


class RequestedRoleRequest(BaseModel):
    """Requested role request"""
    gid: str
    value: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectTemplateInstantiateProjectRequest(BaseModel):
    """Instantiate project from template request"""
    name: str
    team: Optional[str] = None
    public: Optional[bool] = None
    privacy_setting: Optional[str] = None
    is_strict: Optional[bool] = None
    requested_dates: Optional[List[DateVariableRequest]] = None
    requested_roles: Optional[List[RequestedRoleRequest]] = None

    class Config:
        from_attributes = True


class ProjectSaveAsTemplateRequest(BaseModel):
    """Save project as template request"""
    name: str
    public: bool
    team: Optional[str] = None
    workspace: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class ProjectTemplateResponseWrapper(BaseModel):
    """Project template response wrapper"""
    data: ProjectTemplateResponse

    class Config:
        from_attributes = True


class ProjectTemplateListResponse(BaseModel):
    """Project template list response"""
    data: List[ProjectTemplateCompact]

    class Config:
        from_attributes = True

