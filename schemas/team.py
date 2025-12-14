from pydantic import BaseModel
from typing import Optional, List, Dict
from schemas.base import TeamCompact, WorkspaceCompact, CustomFieldSettingCompact


class TeamResponse(TeamCompact):
    """Full team response"""
    description: Optional[str] = None
    html_description: Optional[str] = None
    organization: Optional[WorkspaceCompact] = None
    permalink_url: Optional[str] = None
    visibility: Optional[str] = None
    edit_team_name_or_description_access_level: Optional[str] = None
    edit_team_visibility_or_trash_team_access_level: Optional[str] = None
    member_invite_management_access_level: Optional[str] = None
    guest_invite_management_access_level: Optional[str] = None
    join_request_management_access_level: Optional[str] = None
    team_member_removal_access_level: Optional[str] = None
    team_content_management_access_level: Optional[str] = None
    endorsed: Optional[bool] = None
    custom_field_settings: Optional[List[CustomFieldSettingCompact]] = None

    class Config:
        from_attributes = True


class TeamRequest(BaseModel):
    """Team create request"""
    name: Optional[str] = None
    description: Optional[str] = None
    html_description: Optional[str] = None
    organization: Optional[str] = None
    visibility: Optional[str] = None
    edit_team_name_or_description_access_level: Optional[str] = None
    edit_team_visibility_or_trash_team_access_level: Optional[str] = None
    member_invite_management_access_level: Optional[str] = None
    guest_invite_management_access_level: Optional[str] = None
    join_request_management_access_level: Optional[str] = None
    team_member_removal_access_level: Optional[str] = None
    team_content_management_access_level: Optional[str] = None
    endorsed: Optional[bool] = None

    class Config:
        from_attributes = True


class TeamAddUserRequest(BaseModel):
    """Add user to team request"""
    user: str

    class Config:
        from_attributes = True


class TeamRemoveUserRequest(BaseModel):
    """Remove user from team request"""
    user: str

    class Config:
        from_attributes = True


# Response wrappers
class TeamResponseWrapper(BaseModel):
    """Team response wrapper"""
    data: TeamResponse

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Team list response"""
    data: List[TeamCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

