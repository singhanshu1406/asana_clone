from pydantic import BaseModel
from typing import Optional
from schemas.base import GoalCompact, MemberCompact


class GoalMembershipCompact(BaseModel):
    """Compact goal membership representation"""
    gid: str
    resource_type: str = "membership"
    resource_subtype: Optional[str] = "goal_membership"
    member: Optional[MemberCompact] = None
    parent: Optional[GoalCompact] = None
    role: Optional[str] = None  # Deprecated
    access_level: Optional[str] = None  # "viewer", "commenter", "editor", "admin"
    goal: Optional[GoalCompact] = None  # Deprecated

    class Config:
        from_attributes = True


class GoalMembershipResponse(GoalMembershipCompact):
    """Full goal membership response"""
    class Config:
        from_attributes = True


# Response wrappers
class GoalMembershipResponseWrapper(BaseModel):
    """Goal membership response wrapper"""
    data: GoalMembershipResponse

    class Config:
        from_attributes = True


class GoalMembershipListResponse(BaseModel):
    """Goal membership list response"""
    data: list[GoalMembershipCompact]

    class Config:
        from_attributes = True

