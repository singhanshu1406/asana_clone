from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from schemas.base import AsanaResource, UserCompact, ProjectCompact


class RateCompact(AsanaResource):
    """Compact rate representation"""
    rate: Optional[Decimal] = None
    currency_code: Optional[str] = None

    class Config:
        from_attributes = True


class RateResponse(RateCompact):
    """Full rate response"""
    parent: Optional[ProjectCompact] = None
    resource: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class RateRequest(BaseModel):
    """Rate create/update request"""
    rate: Optional[Decimal] = None
    currency_code: Optional[str] = None
    parent: str
    resource: Optional[str] = None


class RateListResponse(BaseModel):
    """List of rates"""
    data: List[RateResponse]
    next_page: Optional[dict] = None


class RateResponseWrapper(BaseModel):
    """Single rate response wrapper"""
    data: RateResponse

