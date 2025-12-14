from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class BatchRequest(BaseModel):
    """Batch request item"""
    method: str
    relative_path: str
    data: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


class BatchRequestWrapper(BaseModel):
    """Batch request wrapper"""
    data: List[BatchRequest]


class BatchResponse(BaseModel):
    """Batch response item"""
    status_code: int
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None


class BatchResponseWrapper(BaseModel):
    """Batch response wrapper"""
    data: List[BatchResponse]

