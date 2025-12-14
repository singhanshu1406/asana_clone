from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from schemas.base import AsanaNamedResource


class WebhookFilter(BaseModel):
    """Webhook filter"""
    resource_type: Optional[str] = None
    resource_subtype: Optional[str] = None
    action: Optional[str] = None
    fields: Optional[List[str]] = None

    class Config:
        from_attributes = True


class WebhookCompact(BaseModel):
    """Compact webhook representation"""
    gid: str
    resource_type: str
    active: Optional[bool] = None
    resource: Optional[AsanaNamedResource] = None
    target: Optional[str] = None

    class Config:
        from_attributes = True


class WebhookResponse(WebhookCompact):
    """Full webhook response"""
    created_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_failure_content: Optional[str] = None
    last_success_at: Optional[datetime] = None
    delivery_retry_count: Optional[int] = None
    next_attempt_after: Optional[datetime] = None
    failure_deletion_timestamp: Optional[datetime] = None
    filters: Optional[List[WebhookFilter]] = None

    class Config:
        from_attributes = True


class WebhookRequest(BaseModel):
    """Webhook create request"""
    resource: str
    target: str
    filters: Optional[List[WebhookFilter]] = None

    class Config:
        from_attributes = True


class WebhookUpdateRequest(BaseModel):
    """Webhook update request"""
    filters: Optional[List[WebhookFilter]] = None

    class Config:
        from_attributes = True


# Response wrappers
class WebhookResponseWrapper(BaseModel):
    """Webhook response wrapper"""
    data: WebhookResponse

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """Webhook list response"""
    data: List[WebhookCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

