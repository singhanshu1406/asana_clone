from pydantic import BaseModel
from typing import Optional, List
from schemas.base import AsanaResource, CustomFieldCompact, ProjectCompact, PortfolioCompact


class CustomFieldSettingCompact(AsanaResource):
    """Compact custom field setting representation"""
    is_important: Optional[bool] = None

    class Config:
        from_attributes = True


class CustomFieldSettingResponse(CustomFieldSettingCompact):
    """Full custom field setting response"""
    custom_field: Optional[CustomFieldCompact] = None
    project: Optional[ProjectCompact] = None
    portfolio: Optional[PortfolioCompact] = None

    class Config:
        from_attributes = True


class CustomFieldSettingListResponse(BaseModel):
    """List of custom field settings"""
    data: List[CustomFieldSettingResponse]
    next_page: Optional[dict] = None


class CustomFieldSettingResponseWrapper(BaseModel):
    """Single custom field setting response wrapper"""
    data: CustomFieldSettingResponse

