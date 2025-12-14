from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.base import GraphExportCompact


class GraphExportRequest(BaseModel):
    """Graph export request"""
    parent: str

    class Config:
        from_attributes = True


class GraphExportResponse(BaseModel):
    """Graph export response (job format)"""
    gid: str
    resource_type: str = "job"
    resource_subtype: Optional[str] = "graph_export_request"
    status: Optional[str] = None
    new_graph_export: Optional[GraphExportCompact] = None

    class Config:
        from_attributes = True


# Response wrappers
class GraphExportResponseWrapper(BaseModel):
    """Graph export response wrapper"""
    data: GraphExportResponse

    class Config:
        from_attributes = True


class GraphExportCompactResponseWrapper(BaseModel):
    """Graph export compact response wrapper"""
    data: GraphExportCompact

    class Config:
        from_attributes = True

