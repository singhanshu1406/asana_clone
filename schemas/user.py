from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from schemas.base import UserCompact, WorkspaceCompact, CustomFieldCompact


class Photo(BaseModel):
    """User photo object"""
    image_21x21: Optional[str] = None
    image_27x27: Optional[str] = None
    image_36x36: Optional[str] = None
    image_60x60: Optional[str] = None
    image_128x128: Optional[str] = None
    image_1024x1024: Optional[str] = None

    class Config:
        from_attributes = True


class UserBaseResponse(UserCompact):
    """User base response"""
    email: Optional[str] = None
    photo: Optional[Photo] = None

    class Config:
        from_attributes = True


class UserResponse(UserBaseResponse):
    """Full user response"""
    workspaces: Optional[List[WorkspaceCompact]] = None
    custom_fields: Optional[List[CustomFieldCompact]] = None

    class Config:
        from_attributes = True


class UserRequest(BaseModel):
    """User create/update request"""
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(UserRequest):
    """User update request"""
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Response wrappers
class UserResponseWrapper(BaseModel):
    """User response wrapper"""
    data: UserResponse

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response"""
    data: List[UserCompact]

    class Config:
        from_attributes = True

