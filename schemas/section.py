from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from schemas.base import ProjectCompact, SectionCompact


class SectionResponse(SectionCompact):
    """Full section response"""
    created_at: Optional[datetime] = None
    project: Optional[ProjectCompact] = None
    projects: Optional[List[ProjectCompact]] = None  # Deprecated

    class Config:
        from_attributes = True


class SectionRequest(BaseModel):
    """Section create request"""
    name: str
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectSectionInsertRequest(BaseModel):
    """Project section insert request"""
    section: str
    before_section: Optional[str] = None
    after_section: Optional[str] = None

    class Config:
        from_attributes = True


class SectionTaskInsertRequest(BaseModel):
    """Section task insert request"""
    task: str
    insert_before: Optional[str] = None
    insert_after: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class SectionResponseWrapper(BaseModel):
    """Section response wrapper"""
    data: SectionResponse

    class Config:
        from_attributes = True


class SectionListResponse(BaseModel):
    """Section list response"""
    data: List[SectionCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

