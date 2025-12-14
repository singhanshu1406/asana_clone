from pydantic import BaseModel
from typing import Optional, List, Dict
from schemas.base import AsanaResource, ProjectCompact


class BudgetEstimate(BaseModel):
    """Budget estimate"""
    enabled: Optional[bool] = None
    source: Optional[str] = None
    billable_status_filter: Optional[str] = None
    value: Optional[float] = None
    units: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetActual(BaseModel):
    """Budget actual"""
    billable_status_filter: Optional[str] = None
    value: Optional[float] = None
    units: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetTotal(BaseModel):
    """Budget total"""
    enabled: Optional[bool] = None
    value: Optional[float] = None
    units: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetCompact(AsanaResource):
    """Compact budget representation"""
    budget_type: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetResponse(BudgetCompact):
    """Full budget response"""
    estimate: Optional[BudgetEstimate] = None
    actual: Optional[BudgetActual] = None
    total: Optional[BudgetTotal] = None
    parent: Optional[ProjectCompact] = None

    class Config:
        from_attributes = True


class BudgetRequest(BaseModel):
    """Budget create/update request"""
    parent: Optional[str] = None
    budget_type: Optional[str] = None
    estimate_enabled: Optional[bool] = None
    estimate_source: Optional[str] = None
    estimate_billable_status_filter: Optional[str] = None
    estimate_value: Optional[float] = None
    estimate_units: Optional[str] = None
    actual_billable_status_filter: Optional[str] = None
    actual_value: Optional[float] = None
    actual_units: Optional[str] = None
    total_enabled: Optional[bool] = None
    total_value: Optional[float] = None
    total_units: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    """Budget list response"""
    data: List[BudgetResponse]

    class Config:
        from_attributes = True


class BudgetResponseWrapper(BaseModel):
    """Budget response wrapper"""
    data: BudgetResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

