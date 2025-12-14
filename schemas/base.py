from pydantic import BaseModel
from typing import Optional


class AsanaResource(BaseModel):
    """Base Asana Resource with gid and resource_type"""
    gid: str
    resource_type: str

    class Config:
        from_attributes = True


class AsanaNamedResource(AsanaResource):
    """Asana Resource with name"""
    name: str

    class Config:
        from_attributes = True


class UserCompact(AsanaNamedResource):
    """Compact user representation"""
    email: Optional[str] = None
    photo: Optional[str] = None

    class Config:
        from_attributes = True


class TeamCompact(AsanaNamedResource):
    """Compact team representation"""
    class Config:
        from_attributes = True


class WorkspaceCompact(AsanaNamedResource):
    """Compact workspace representation"""
    is_organization: Optional[bool] = None

    class Config:
        from_attributes = True


class ProjectCompact(AsanaNamedResource):
    """Compact project representation"""
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class TaskCompact(AsanaNamedResource):
    """Compact task representation"""
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class GoalCompact(AsanaNamedResource):
    """Compact goal representation"""
    owner: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class PortfolioCompact(AsanaNamedResource):
    """Compact portfolio representation"""
    class Config:
        from_attributes = True


class TimePeriodCompact(AsanaResource):
    """Compact time period representation"""
    display_name: Optional[str] = None

    class Config:
        from_attributes = True


class StatusUpdateCompact(AsanaResource):
    """Compact status update representation"""
    title: Optional[str] = None
    text: Optional[str] = None

    class Config:
        from_attributes = True


class CustomFieldCompact(AsanaNamedResource):
    """Compact custom field representation"""
    type: Optional[str] = None
    resource_subtype: Optional[str] = None

    class Config:
        from_attributes = True


class CustomFieldSettingCompact(AsanaResource):
    """Compact custom field setting representation"""
    class Config:
        from_attributes = True


class ProjectTemplateCompact(AsanaNamedResource):
    """Compact project template representation"""
    class Config:
        from_attributes = True


class GraphExportCompact(AsanaResource):
    """Compact graph export representation"""
    state: Optional[str] = None

    class Config:
        from_attributes = True


class ResourceExportCompact(AsanaResource):
    """Compact resource export representation"""
    state: Optional[str] = None

    class Config:
        from_attributes = True


class Like(BaseModel):
    """Like object"""
    gid: str
    user: UserCompact

    class Config:
        from_attributes = True


class MemberCompact(AsanaNamedResource):
    """Member can be user or team"""
    class Config:
        from_attributes = True


class ProjectBriefCompact(AsanaResource):
    """Compact project brief representation"""
    class Config:
        from_attributes = True


class SectionCompact(AsanaNamedResource):
    """Compact section representation"""
    class Config:
        from_attributes = True


class TagCompact(AsanaNamedResource):
    """Compact tag representation"""
    class Config:
        from_attributes = True

