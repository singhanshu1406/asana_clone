from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from datetime import date, datetime
from schemas.base import (
    UserCompact, TeamCompact, WorkspaceCompact, TimePeriodCompact,
    StatusUpdateCompact, CustomFieldCompact, CustomFieldSettingCompact,
    Like
)


class GoalMetricBase(BaseModel):
    """Goal metric base schema"""
    gid: str
    resource_type: str
    resource_subtype: Optional[str] = None
    precision: Optional[int] = None
    unit: Optional[str] = None  # "none", "currency", "percentage"
    currency_code: Optional[str] = None
    initial_number_value: Optional[float] = None
    target_number_value: Optional[float] = None
    current_number_value: Optional[float] = None
    current_display_value: Optional[str] = None
    progress_source: Optional[str] = None  # "manual", "subgoal_progress", etc.
    is_custom_weight: Optional[bool] = None

    class Config:
        from_attributes = True


class GoalMetricResponse(GoalMetricBase):
    """Goal metric response"""
    can_manage: Optional[bool] = None

    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    """Goal base schema"""
    gid: str
    resource_type: str
    name: str
    html_notes: Optional[str] = None
    notes: Optional[str] = None
    due_on: Optional[date] = None
    start_on: Optional[date] = None
    is_workspace_level: Optional[bool] = None
    liked: Optional[bool] = None

    class Config:
        from_attributes = True


class GoalCompact(GoalBase):
    """Compact goal representation"""
    owner: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class GoalResponse(GoalBase):
    """Full goal response"""
    likes: Optional[List[Like]] = None
    num_likes: Optional[int] = None
    team: Optional[TeamCompact] = None
    workspace: Optional[WorkspaceCompact] = None
    followers: Optional[List[UserCompact]] = None
    time_period: Optional[TimePeriodCompact] = None
    metric: Optional[GoalMetricResponse] = None
    owner: Optional[UserCompact] = None
    current_status_update: Optional[StatusUpdateCompact] = None
    status: Optional[str] = None
    custom_fields: Optional[List[CustomFieldCompact]] = None
    custom_field_settings: Optional[List[CustomFieldSettingCompact]] = None

    class Config:
        from_attributes = True


class GoalRequestBase(BaseModel):
    """Base goal request"""
    name: Optional[str] = None
    html_notes: Optional[str] = None
    notes: Optional[str] = None
    due_on: Optional[date] = None
    start_on: Optional[date] = None
    team: Optional[str] = None
    workspace: Optional[str] = None
    time_period: Optional[str] = None
    owner: Optional[str] = None

    class Config:
        from_attributes = True


class GoalRequest(GoalRequestBase):
    """Goal create request"""
    followers: Optional[List[str]] = None

    class Config:
        from_attributes = True


class GoalUpdateRequest(GoalRequestBase):
    """Goal update request"""
    status: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class GoalAddSubgoalRequest(BaseModel):
    """Add subgoal request"""
    subgoal: str
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None

    class Config:
        from_attributes = True


class GoalRemoveSubgoalRequest(BaseModel):
    """Remove subgoal request"""
    subgoal: str

    class Config:
        from_attributes = True


class GoalAddSupportingWorkRequest(BaseModel):
    """Add supporting work request"""
    supporting_work: str

    class Config:
        from_attributes = True


class GoalAddSupportingRelationshipRequest(BaseModel):
    """Add supporting relationship request"""
    supporting_resource: str
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None
    contribution_weight: Optional[float] = None

    class Config:
        from_attributes = True


class GoalRemoveSupportingRelationshipRequest(BaseModel):
    """Remove supporting relationship request"""
    supporting_resource: str

    class Config:
        from_attributes = True


class GoalMetricRequest(BaseModel):
    """Goal metric request"""
    precision: Optional[int] = None
    unit: Optional[str] = None
    currency_code: Optional[str] = None
    initial_number_value: Optional[float] = None
    target_number_value: Optional[float] = None
    progress_source: Optional[str] = None
    is_custom_weight: Optional[bool] = None

    class Config:
        from_attributes = True


class GoalMetricCurrentValueRequest(BaseModel):
    """Update goal metric current value"""
    current_number_value: Optional[float] = None

    class Config:
        from_attributes = True


# Response wrappers
class GoalResponseWrapper(BaseModel):
    """Goal response wrapper"""
    data: GoalResponse

    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """Goal list response"""
    data: List[GoalCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

