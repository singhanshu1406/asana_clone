from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from datetime import datetime
from schemas.base import (
    UserCompact, TaskCompact, ProjectCompact, TagCompact,
    CustomFieldCompact, SectionCompact, Like
)


class Preview(BaseModel):
    """Preview object"""
    fallback: Optional[str] = None
    footer: Optional[str] = None
    header: Optional[str] = None
    header_link: Optional[str] = None
    html_text: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None

    class Config:
        from_attributes = True


class StoryResponseDates(BaseModel):
    """Story response dates"""
    start_on: Optional[str] = None
    due_at: Optional[datetime] = None
    due_on: Optional[str] = None

    class Config:
        from_attributes = True


class StoryBase(BaseModel):
    """Story base schema"""
    gid: str
    resource_type: str
    created_at: datetime
    resource_subtype: Optional[str] = None
    text: Optional[str] = None
    html_text: Optional[str] = None
    is_pinned: Optional[bool] = None
    sticker_name: Optional[str] = None

    class Config:
        from_attributes = True


class StoryCompact(StoryBase):
    """Compact story representation"""
    created_by: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class StoryResponse(StoryBase):
    """Full story response"""
    created_by: Optional[UserCompact] = None
    type: Optional[str] = None
    is_editable: Optional[bool] = None
    is_edited: Optional[bool] = None
    hearted: Optional[bool] = None
    hearts: Optional[List[Like]] = None
    num_hearts: Optional[int] = None
    liked: Optional[bool] = None
    likes: Optional[List[Like]] = None
    num_likes: Optional[int] = None
    reaction_summary: Optional[List[Any]] = None
    previews: Optional[List[Preview]] = None
    old_name: Optional[str] = None
    new_name: Optional[str] = None
    old_dates: Optional[StoryResponseDates] = None
    new_dates: Optional[StoryResponseDates] = None
    old_resource_subtype: Optional[str] = None
    new_resource_subtype: Optional[str] = None
    story: Optional[StoryCompact] = None
    assignee: Optional[UserCompact] = None
    follower: Optional[UserCompact] = None
    old_section: Optional[SectionCompact] = None
    new_section: Optional[SectionCompact] = None
    task: Optional[TaskCompact] = None
    project: Optional[ProjectCompact] = None
    tag: Optional[TagCompact] = None
    custom_field: Optional[CustomFieldCompact] = None
    old_text_value: Optional[str] = None
    new_text_value: Optional[str] = None
    old_number_value: Optional[int] = None
    new_number_value: Optional[int] = None
    old_enum_value: Optional[Any] = None
    new_enum_value: Optional[Any] = None
    old_date_value: Optional[StoryResponseDates] = None
    new_date_value: Optional[StoryResponseDates] = None
    old_people_value: Optional[List[UserCompact]] = None
    new_people_value: Optional[List[UserCompact]] = None
    old_multi_enum_values: Optional[List[Any]] = None
    new_multi_enum_values: Optional[List[Any]] = None
    new_approval_status: Optional[str] = None
    old_approval_status: Optional[str] = None
    duplicate_of: Optional[TaskCompact] = None
    duplicated_from: Optional[TaskCompact] = None
    dependency: Optional[TaskCompact] = None
    source: Optional[str] = None
    target: Optional[TaskCompact] = None

    class Config:
        from_attributes = True


class StoryRequest(BaseModel):
    """Story create request"""
    text: Optional[str] = None
    html_text: Optional[str] = None
    is_pinned: Optional[bool] = None
    sticker_name: Optional[str] = None

    class Config:
        from_attributes = True


# Response wrappers
class StoryResponseWrapper(BaseModel):
    """Story response wrapper"""
    data: StoryResponse

    class Config:
        from_attributes = True


class StoryListResponse(BaseModel):
    """Story list response"""
    data: List[StoryCompact]

    class Config:
        from_attributes = True


class EmptyResponse(BaseModel):
    """Empty response"""
    data: Dict = {}

    class Config:
        from_attributes = True

