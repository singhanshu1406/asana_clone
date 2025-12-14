from pydantic import BaseModel
from typing import Optional
from schemas.base import UserCompact, TeamCompact


class TeamMembershipCompact(BaseModel):
    """Compact team membership representation"""
    gid: str
    resource_type: str
    user: Optional[UserCompact] = None
    team: Optional[TeamCompact] = None
    is_guest: Optional[bool] = None
    is_limited_access: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True


class TeamMembershipResponse(TeamMembershipCompact):
    """Full team membership response"""
    class Config:
        from_attributes = True


# Response wrappers
class TeamMembershipResponseWrapper(BaseModel):
    """Team membership response wrapper"""
    data: TeamMembershipResponse

    class Config:
        from_attributes = True


class TeamMembershipListResponse(BaseModel):
    """Team membership list response"""
    data: list[TeamMembershipCompact]

    class Config:
        from_attributes = True

