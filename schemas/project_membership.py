from pydantic import BaseModel
from typing import Optional, Dict
from schemas.base import ProjectCompact, UserCompact, MemberCompact


class ProjectMembershipCompact(BaseModel):
    """Compact project membership representation"""
    gid: str
    resource_type: str
    parent: Optional[ProjectCompact] = None
    member: Optional[MemberCompact] = None
    access_level: Optional[str] = None  # "admin", "editor", "commenter", "viewer"

    class Config:
        from_attributes = True


class ProjectMembershipCompactResponse(ProjectMembershipCompact):
    """Project membership compact response with resource_type override"""
    resource_type: str = "membership"
    resource_subtype: Optional[str] = "project_membership"

    class Config:
        from_attributes = True


class ProjectMembershipNormalResponse(BaseModel):
    """Project membership normal response (deprecated format)"""
    gid: str
    resource_type: str = "project_membership"
    user: Optional[UserCompact] = None
    project: Optional[ProjectCompact] = None
    write_access: Optional[str] = None  # "full_write", "comment_only"

    class Config:
        from_attributes = True


class ProjectMembershipResponse(ProjectMembershipCompact):
    """Full project membership response"""
    class Config:
        from_attributes = True


class ProjectMembershipRequest(BaseModel):
    """Project membership request"""
    user: Optional[str] = None
    team: Optional[str] = None
    access_level: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class ProjectMembershipResponseWrapper(BaseModel):
    """Project membership response wrapper"""
    data: ProjectMembershipResponse

    class Config:
        from_attributes = True


class ProjectMembershipListResponse(BaseModel):
    """Project membership list response"""
    data: list[ProjectMembershipCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

