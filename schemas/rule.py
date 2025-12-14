from pydantic import BaseModel
from typing import Optional, Dict, Any


class RuleTriggerRequest(BaseModel):
    """Rule trigger request"""
    variables: Optional[Dict[str, Any]] = None


class RuleTriggerResponse(BaseModel):
    """Rule trigger response"""
    success: bool
    message: Optional[str] = None


class RuleTriggerResponseWrapper(BaseModel):
    """Rule trigger response wrapper"""
    data: RuleTriggerResponse

