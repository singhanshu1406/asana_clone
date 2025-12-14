from pydantic import BaseModel
from typing import Optional
from schemas.base import CustomFieldCompact, MemberCompact


class CustomFieldMembershipCompact(BaseModel):
    """Compact custom field membership representation"""
    gid: str
    resource_type: str
    resource_subtype: Optional[str] = None
    parent: Optional[CustomFieldCompact] = None
    member: Optional[MemberCompact] = None
    access_level: Optional[str] = None  # "admin", "editor", "user"

    class Config:
        from_attributes = True


class CustomFieldMembershipResponse(CustomFieldMembershipCompact):
    """Full custom field membership response"""
    class Config:
        from_attributes = True


# Response wrappers
class CustomFieldMembershipResponseWrapper(BaseModel):
    """Custom field membership response wrapper"""
    data: CustomFieldMembershipResponse

    class Config:
        from_attributes = True


class CustomFieldMembershipListResponse(BaseModel):
    """Custom field membership list response"""
    data: list[CustomFieldMembershipCompact]

    class Config:
        from_attributes = True

