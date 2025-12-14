from pydantic import BaseModel
from typing import Optional
from schemas.base import UserCompact, WorkspaceCompact


class UserTaskListCompact(BaseModel):
    """Compact user task list representation"""
    gid: str
    resource_type: str
    name: Optional[str] = None
    owner: Optional[UserCompact] = None
    workspace: Optional[WorkspaceCompact] = None

    class Config:
        from_attributes = True


class UserTaskListResponse(UserTaskListCompact):
    """Full user task list response"""
    class Config:
        from_attributes = True


# Response wrappers
class UserTaskListResponseWrapper(BaseModel):
    """User task list response wrapper"""
    data: UserTaskListResponse

    class Config:
        from_attributes = True

