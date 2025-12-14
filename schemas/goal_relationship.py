from pydantic import BaseModel
from typing import Optional
from schemas.base import GoalCompact, ProjectCompact, TaskCompact, PortfolioCompact, AsanaNamedResource


class GoalRelationshipCompact(BaseModel):
    """Compact goal relationship representation"""
    gid: str
    resource_type: str
    resource_subtype: Optional[str] = None  # "subgoal", "supporting_work"
    supporting_resource: Optional[AsanaNamedResource] = None
    contribution_weight: Optional[float] = None

    class Config:
        from_attributes = True


class GoalRelationshipBase(GoalRelationshipCompact):
    """Goal relationship base"""
    supported_goal: Optional[GoalCompact] = None

    class Config:
        from_attributes = True


class GoalRelationshipResponse(GoalRelationshipBase):
    """Goal relationship response"""
    class Config:
        from_attributes = True


class GoalRelationshipRequest(BaseModel):
    """Goal relationship request"""
    supporting_resource: Optional[str] = None
    contribution_weight: Optional[float] = None

    class Config:
        from_attributes = True


# Response wrappers
class GoalRelationshipResponseWrapper(BaseModel):
    """Goal relationship response wrapper"""
    data: GoalRelationshipResponse

    class Config:
        from_attributes = True


class GoalRelationshipListResponse(BaseModel):
    """Goal relationship list response"""
    data: list[GoalRelationshipCompact]

    class Config:
        from_attributes = True

