from pydantic import BaseModel
from typing import Optional, Dict
from schemas.base import ProjectCompact, ProjectBriefCompact


class ProjectBriefBase(ProjectBriefCompact):
    """Project brief base"""
    title: Optional[str] = None
    html_text: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectBriefResponse(ProjectBriefBase):
    """Full project brief response"""
    text: Optional[str] = None
    permalink_url: Optional[str] = None
    project: Optional[ProjectCompact] = None

    class Config:
        from_attributes = True


class ProjectBriefRequest(BaseModel):
    """Project brief request"""
    text: Optional[str] = None
    html_text: Optional[str] = None
    title: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class ProjectBriefResponseWrapper(BaseModel):
    """Project brief response wrapper"""
    data: ProjectBriefResponse

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

