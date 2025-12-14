from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date, datetime
from schemas.base import UserCompact, WorkspaceCompact
from schemas.user_task_list import UserTaskListResponse


class VacationDates(BaseModel):
    """Vacation dates"""
    start_on: Optional[str] = None
    end_on: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceMembershipCompact(BaseModel):
    """Compact workspace membership representation"""
    gid: str
    resource_type: str
    user: Optional[UserCompact] = None
    workspace: Optional[WorkspaceCompact] = None

    class Config:
        from_attributes = True


class WorkspaceMembershipResponse(WorkspaceMembershipCompact):
    """Full workspace membership response"""
    user_task_list: Optional[UserTaskListResponse] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_guest: Optional[bool] = None
    is_view_only: Optional[bool] = None
    vacation_dates: Optional[VacationDates] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Response wrappers
class WorkspaceMembershipResponseWrapper(BaseModel):
    """Workspace membership response wrapper"""
    data: WorkspaceMembershipResponse

    class Config:
        from_attributes = True


class WorkspaceMembershipListResponse(BaseModel):
    """Workspace membership list response"""
    data: list[WorkspaceMembershipCompact]

    class Config:
        from_attributes = True

