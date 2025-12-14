from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date
from schemas.base import AsanaResource, UserCompact, ProjectCompact


class Effort(BaseModel):
    """Effort object"""
    type: Optional[str] = None  # "hours" or "percent"
    value: Optional[float] = None

    class Config:
        from_attributes = True


class AllocationCompact(AsanaResource):
    """Compact allocation representation"""
    resource_subtype: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        from_attributes = True


class AllocationResponse(AllocationCompact):
    """Full allocation response"""
    assignee: Optional[UserCompact] = None
    parent: Optional[ProjectCompact] = None
    created_by: Optional[UserCompact] = None
    effort: Optional[Effort] = None

    class Config:
        from_attributes = True


class AllocationRequest(BaseModel):
    """Allocation create/update request"""
    assignee: Optional[str] = None
    parent: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    effort_type: Optional[str] = None
    effort_value: Optional[float] = None
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class AllocationListResponse(BaseModel):
    """Allocation list response"""
    data: List[AllocationResponse]

    class Config:
        from_attributes = True


class AllocationResponseWrapper(BaseModel):
    """Allocation response wrapper"""
    data: AllocationResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

