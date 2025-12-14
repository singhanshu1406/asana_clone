from pydantic import BaseModel
from typing import Optional, List, Dict
from schemas.base import WorkspaceCompact


class WorkspaceResponse(WorkspaceCompact):
    """Full workspace response"""
    email_domains: Optional[List[str]] = None
    is_organization: Optional[bool] = None

    class Config:
        from_attributes = True


class WorkspaceRequest(BaseModel):
    """Workspace create request"""
    name: Optional[str] = None
    is_organization: Optional[bool] = None

    class Config:
        from_attributes = True


class WorkspaceAddUserRequest(BaseModel):
    """Add user to workspace request"""
    user: str

    class Config:
        from_attributes = True


class WorkspaceRemoveUserRequest(BaseModel):
    """Remove user from workspace request"""
    user: str

    class Config:
        from_attributes = True


# Response wrappers
class WorkspaceResponseWrapper(BaseModel):
    """Workspace response wrapper"""
    data: WorkspaceResponse

    class Config:
        from_attributes = True


class WorkspaceListResponse(BaseModel):
    """Workspace list response"""
    data: List[WorkspaceCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

