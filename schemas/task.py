from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from schemas.base import (
    UserCompact, WorkspaceCompact, ProjectCompact, SectionCompact,
    TagCompact, CustomFieldCompact, TaskCompact, AsanaResource
)


class TaskBase(TaskCompact):
    """Task base schema"""
    approval_status: Optional[str] = None
    assignee_status: Optional[str] = None
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[UserCompact] = None
    created_at: Optional[datetime] = None
    dependencies: Optional[List[AsanaResource]] = None
    dependents: Optional[List[AsanaResource]] = None
    due_at: Optional[datetime] = None
    due_on: Optional[date] = None
    external: Optional[Dict[str, Any]] = None
    html_notes: Optional[str] = None
    hearted: Optional[bool] = None
    hearts: Optional[List[Any]] = None
    is_rendered_as_separator: Optional[bool] = None
    liked: Optional[bool] = None
    likes: Optional[List[Any]] = None
    memberships: Optional[List[Dict[str, Any]]] = None
    modified_at: Optional[datetime] = None
    name: Optional[str] = None
    notes: Optional[str] = None
    num_hearts: Optional[int] = None
    num_likes: Optional[int] = None
    num_subtasks: Optional[int] = None
    start_at: Optional[datetime] = None
    start_on: Optional[date] = None
    actual_time_minutes: Optional[float] = None

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """Full task response"""
    assignee: Optional[UserCompact] = None
    assignee_section: Optional[SectionCompact] = None
    custom_fields: Optional[List[CustomFieldCompact]] = None
    custom_type: Optional[Any] = None
    custom_type_status_option: Optional[Any] = None
    followers: Optional[List[UserCompact]] = None
    parent: Optional[TaskCompact] = None
    projects: Optional[List[ProjectCompact]] = None
    tags: Optional[List[TagCompact]] = None
    workspace: Optional[WorkspaceCompact] = None
    permalink_url: Optional[str] = None

    class Config:
        from_attributes = True


class TaskRequest(BaseModel):
    """Task create request"""
    name: Optional[str] = None
    notes: Optional[str] = None
    html_notes: Optional[str] = None
    completed: Optional[bool] = None
    due_on: Optional[date] = None
    due_at: Optional[datetime] = None
    start_on: Optional[date] = None
    start_at: Optional[datetime] = None
    assignee: Optional[str] = None
    assignee_section: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    followers: Optional[List[str]] = None
    parent: Optional[str] = None
    projects: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    workspace: Optional[str] = None
    custom_type: Optional[str] = None
    custom_type_status_option: Optional[str] = None

    class Config:
        from_attributes = True


class TaskUpdateRequest(BaseModel):
    """Task update request"""
    name: Optional[str] = None
    notes: Optional[str] = None
    html_notes: Optional[str] = None
    completed: Optional[bool] = None
    due_on: Optional[date] = None
    due_at: Optional[datetime] = None
    start_on: Optional[date] = None
    start_at: Optional[datetime] = None
    assignee: Optional[str] = None
    assignee_section: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    approval_status: Optional[str] = None
    assignee_status: Optional[str] = None

    class Config:
        from_attributes = True


class TaskAddFollowersRequest(BaseModel):
    """Add followers to task request"""
    followers: List[str]

    class Config:
        from_attributes = True


class TaskRemoveFollowersRequest(BaseModel):
    """Remove followers from task request"""
    followers: List[str]

    class Config:
        from_attributes = True


class TaskAddProjectRequest(BaseModel):
    """Add task to project request"""
    project: str
    insert_after: Optional[str] = None
    insert_before: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


class TaskRemoveProjectRequest(BaseModel):
    """Remove task from project request"""
    project: str

    class Config:
        from_attributes = True


class TaskAddTagRequest(BaseModel):
    """Add tag to task request"""
    tag: str

    class Config:
        from_attributes = True


class TaskRemoveTagRequest(BaseModel):
    """Remove tag from task request"""
    tag: str

    class Config:
        from_attributes = True


class TaskSetParentRequest(BaseModel):
    """Set task parent request"""
    parent: str
    insert_after: Optional[str] = None
    insert_before: Optional[str] = None

    class Config:
        from_attributes = True


class ModifyDependenciesRequest(BaseModel):
    """Modify task dependencies request"""
    dependencies: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ModifyDependentsRequest(BaseModel):
    """Modify task dependents request"""
    dependents: Optional[List[str]] = None

    class Config:
        from_attributes = True


class TaskDuplicateRequest(BaseModel):
    """Duplicate task request"""
    name: Optional[str] = None
    include: Optional[str] = None

    class Config:
        from_attributes = True


class TaskCountResponse(BaseModel):
    """Task count response"""
    num_tasks: Optional[int] = None
    num_incomplete_tasks: Optional[int] = None
    num_completed_tasks: Optional[int] = None
    num_milestones: Optional[int] = None
    num_incomplete_milestones: Optional[int] = None
    num_completed_milestones: Optional[int] = None

    class Config:
        from_attributes = True


# Response wrappers
class TaskResponseWrapper(BaseModel):
    """Task response wrapper"""
    data: TaskResponse

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response"""
    data: List[TaskCompact]

    class Config:
        from_attributes = True


class TaskCountResponseWrapper(BaseModel):
    """Task count response wrapper"""
    data: TaskCountResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

