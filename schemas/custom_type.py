from pydantic import BaseModel
from typing import Optional, List
from schemas.base import AsanaResource, AsanaNamedResource


class CustomTypeStatusOptionCompact(AsanaNamedResource):
    """Compact custom type status option representation"""
    color: Optional[str] = None
    enabled: Optional[bool] = None
    completion_state: Optional[str] = None

    class Config:
        from_attributes = True


class CustomTypeCompact(AsanaNamedResource):
    """Compact custom type representation"""
    class Config:
        from_attributes = True


class CustomTypeResponse(CustomTypeCompact):
    """Full custom type response"""
    status_options: Optional[List[CustomTypeStatusOptionCompact]] = None

    class Config:
        from_attributes = True


class CustomTypeListResponse(BaseModel):
    """List of custom types"""
    data: List[CustomTypeResponse]
    next_page: Optional[dict] = None


class CustomTypeResponseWrapper(BaseModel):
    """Single custom type response wrapper"""
    data: CustomTypeResponse

