from pydantic import BaseModel
from typing import Optional
from schemas.base import ProjectCompact, TaskCompact, ProjectTemplateCompact, GraphExportCompact, ResourceExportCompact


class JobCompact(BaseModel):
    """Compact job representation"""
    gid: str
    resource_type: str
    resource_subtype: Optional[str] = None
    status: Optional[str] = None  # "not_started", "in_progress", "succeeded", "failed"
    new_project: Optional[ProjectCompact] = None
    new_task: Optional[TaskCompact] = None
    new_project_template: Optional[ProjectTemplateCompact] = None
    new_graph_export: Optional[GraphExportCompact] = None
    new_resource_export: Optional[ResourceExportCompact] = None

    class Config:
        from_attributes = True


class JobResponse(JobCompact):
    """Job response"""
    class Config:
        from_attributes = True


# Response wrappers
class JobResponseWrapper(BaseModel):
    """Job response wrapper"""
    data: JobResponse

    class Config:
        from_attributes = True

