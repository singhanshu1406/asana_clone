from pydantic import BaseModel
from typing import Optional, List
from schemas.base import AsanaResource, UserCompact


class ReactionCompact(AsanaResource):
    """Compact reaction representation"""
    emoji_base: Optional[str] = None
    emoji_skin_tone: Optional[str] = None

    class Config:
        from_attributes = True


class ReactionResponse(ReactionCompact):
    """Full reaction response"""
    user: Optional[UserCompact] = None

    class Config:
        from_attributes = True


class ReactionListResponse(BaseModel):
    """List of reactions"""
    data: List[ReactionResponse]
    next_page: Optional[dict] = None

