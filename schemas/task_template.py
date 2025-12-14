from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from schemas.base import AsanaResource, AsanaNamedResource, ProjectCompact, UserCompact


class TaskTemplateCompact(AsanaNamedResource):
    """Compact task template representation"""
    class Config:
        from_attributes = True


class TaskTemplateResponse(TaskTemplateCompact):
    """Full task template response"""
    template: Optional[Dict[str, Any]] = None
    project: Optional[ProjectCompact] = None
    created_by: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class TaskTemplateRequest(BaseModel):
    """Task template create request"""
    name: str
    template: Dict[str, Any]
    project: str


class TaskTemplateListResponse(BaseModel):
    """List of task templates"""
    data: List[TaskTemplateResponse]
    next_page: Optional[dict] = None


class TaskTemplateResponseWrapper(BaseModel):
    """Single task template response wrapper"""
    data: TaskTemplateResponse


class TaskTemplateInstantiateRequest(BaseModel):
    """Task template instantiate request"""
    name: Optional[str] = None
    project: Optional[str] = None

