from pydantic import BaseModel
from typing import Optional, List
from schemas.base import AsanaResource, AsanaNamedResource, UserCompact, WorkspaceCompact, CustomFieldCompact


class EnumOptionCompact(AsanaNamedResource):
    """Compact enum option representation"""
    color: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        from_attributes = True


class EnumOptionResponse(EnumOptionCompact):
    """Full enum option response"""
    pass


class EnumOptionRequest(BaseModel):
    """Enum option create/update request"""
    name: str
    color: Optional[str] = None
    enabled: Optional[bool] = True
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None


class CustomFieldBase(AsanaNamedResource):
    """Base custom field representation"""
    type: Optional[str] = None
    resource_subtype: Optional[str] = None
    """Base custom field representation"""
    enabled: Optional[bool] = None
    description: Optional[str] = None
    format: Optional[str] = None
    precision: Optional[int] = None
    currency_code: Optional[str] = None
    custom_label: Optional[str] = None
    custom_label_position: Optional[str] = None
    is_global_to_workspace: Optional[bool] = None
    has_notifications_enabled: Optional[bool] = None
    is_value_read_only: Optional[bool] = None
    asana_created_field: Optional[bool] = None
    is_formula_field: Optional[bool] = None
    id_prefix: Optional[str] = None
    input_restrictions: Optional[List[str]] = None
    representation_type: Optional[str] = None
    default_access_level: Optional[str] = None
    privacy_setting: Optional[str] = None

    class Config:
        from_attributes = True


class CustomFieldResponse(CustomFieldBase):
    """Full custom field response"""
    workspace: Optional[WorkspaceCompact] = None
    created_by: Optional[UserCompact] = None
    enum_options: Optional[List[EnumOptionCompact]] = None

    class Config:
        from_attributes = True


class CustomFieldRequest(BaseModel):
    """Custom field create request"""
    name: str
    type: str
    description: Optional[str] = None
    enabled: Optional[bool] = True
    workspace: str
    precision: Optional[int] = None
    format: Optional[str] = None
    currency_code: Optional[str] = None
    custom_label: Optional[str] = None
    custom_label_position: Optional[str] = None
    is_global_to_workspace: Optional[bool] = None
    has_notifications_enabled: Optional[bool] = None
    is_value_read_only: Optional[bool] = None
    default_access_level: Optional[str] = None
    privacy_setting: Optional[str] = None


class CustomFieldUpdateRequest(BaseModel):
    """Custom field update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    precision: Optional[int] = None
    format: Optional[str] = None
    currency_code: Optional[str] = None
    custom_label: Optional[str] = None
    custom_label_position: Optional[str] = None
    is_global_to_workspace: Optional[bool] = None
    has_notifications_enabled: Optional[bool] = None
    is_value_read_only: Optional[bool] = None
    default_access_level: Optional[str] = None
    privacy_setting: Optional[str] = None


class CustomFieldListResponse(BaseModel):
    """List of custom fields"""
    data: List[CustomFieldResponse]
    next_page: Optional[dict] = None


class CustomFieldResponseWrapper(BaseModel):
    """Single custom field response wrapper"""
    data: CustomFieldResponse


class EnumOptionResponseWrapper(BaseModel):
    """Single enum option response wrapper"""
    data: EnumOptionResponse


class EnumOptionListResponse(BaseModel):
    """List of enum options"""
    data: List[EnumOptionResponse]

