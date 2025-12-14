from pydantic import BaseModel
from typing import Optional, List
from schemas.base import AsanaResource, UserCompact, ProjectCompact, PortfolioCompact


class AccessRequestCompact(AsanaResource):
    """Compact access request representation"""
    approval_status: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class AccessRequestResponse(AccessRequestCompact):
    """Full access request response"""
    requester: Optional[UserCompact] = None
    target: Optional[dict] = None  # Can be ProjectCompact or PortfolioCompact

    class Config:
        from_attributes = True


class AccessRequestCreateRequest(BaseModel):
    """Access request create request"""
    target: str
    message: Optional[str] = None

    class Config:
        from_attributes = True


class AccessRequestListResponse(BaseModel):
    """Access request list response"""
    data: List[AccessRequestResponse]

    class Config:
        from_attributes = True


class AccessRequestResponseWrapper(BaseModel):
    """Access request response wrapper"""
    data: AccessRequestResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: dict = {}

    class Config:
        from_attributes = True

