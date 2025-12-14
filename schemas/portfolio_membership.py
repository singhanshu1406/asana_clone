from pydantic import BaseModel
from typing import Optional, Dict
from schemas.base import PortfolioCompact, UserCompact, MemberCompact


class PortfolioMembershipCompact(BaseModel):
    """Compact portfolio membership representation"""
    gid: str
    resource_type: str
    parent: Optional[PortfolioCompact] = None
    member: Optional[MemberCompact] = None
    access_level: Optional[str] = None  # "admin", "editor", "viewer"

    class Config:
        from_attributes = True


class PortfolioMembershipCompactResponse(PortfolioMembershipCompact):
    """Portfolio membership compact response with resource_type override"""
    resource_type: str = "membership"
    resource_subtype: Optional[str] = "portfolio_membership"

    class Config:
        from_attributes = True


class PortfolioMembershipResponse(PortfolioMembershipCompact):
    """Full portfolio membership response"""
    class Config:
        from_attributes = True


class PortfolioMembershipRequest(BaseModel):
    """Portfolio membership request"""
    user: Optional[str] = None
    team: Optional[str] = None
    access_level: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class PortfolioMembershipResponseWrapper(BaseModel):
    """Portfolio membership response wrapper"""
    data: PortfolioMembershipResponse

    class Config:
        from_attributes = True


class PortfolioMembershipListResponse(BaseModel):
    """Portfolio membership list response"""
    data: list[PortfolioMembershipCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

