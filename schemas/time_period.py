from pydantic import BaseModel
from typing import Optional, List
from schemas.base import TimePeriodCompact


class TimePeriodResponse(TimePeriodCompact):
    """Full time period response"""
    parent: Optional[TimePeriodCompact] = None

    class Config:
        from_attributes = True


# Response wrappers
class TimePeriodResponseWrapper(BaseModel):
    """Time period response wrapper"""
    data: TimePeriodResponse

    class Config:
        from_attributes = True


class TimePeriodListResponse(BaseModel):
    """Time period list response"""
    data: List[TimePeriodCompact]

    class Config:
        from_attributes = True

