from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from utils import generate_gid
from models.graph_export import GraphExport
from models.job import Job
from schemas.graph_export import (
    GraphExportResponse, GraphExportResponseWrapper,
    GraphExportRequest, GraphExportCompactResponseWrapper
)

router = APIRouter()


@router.post("/graph_exports", response_model=GraphExportResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_graph_export(
    export_data: GraphExportRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Graph Export (POST request): Creates a new graph export job.
    """
    # Create a job for the export
    job = Job(
        gid=generate_gid(),
        resource_type="job",
        resource_subtype="graph_export_request",
        status="in_progress"
    )
    
    # Create the graph export
    graph_export = GraphExport(
        gid=generate_gid(),
        resource_type="graph_export",
        state="pending"
    )
    
    db.add(job)
    db.add(graph_export)
    db.commit()
    db.refresh(job)
    db.refresh(graph_export)
    
    export_response = GraphExportResponse(
        gid=job.gid,
        resource_type="job",
        resource_subtype="graph_export_request",
        status="in_progress",
        new_graph_export={
            "gid": graph_export.gid,
            "resource_type": graph_export.resource_type,
            "created_at": graph_export.created_at,
            "download_url": None,
            "completed_at": None
        }
    )
    
    return GraphExportResponseWrapper(data=export_response)


@router.get("/graph_exports/{graph_export_gid}", response_model=GraphExportCompactResponseWrapper)
def get_graph_export(
    graph_export_gid: str = Path(..., description="Globally unique identifier for the graph export"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Graph Export (GET request): Returns the complete graph export record.
    """
    try:
        export_id = int(graph_export_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid graph export GID format"
        )
    
    graph_export = db.query(GraphExport).filter(GraphExport.id == export_id).first()
    if not graph_export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Graph export not found"
        )
    
    export_data = {
        "gid": graph_export.gid,
        "resource_type": graph_export.resource_type,
        "created_at": graph_export.created_at,
        "download_url": graph_export.download_url,
        "completed_at": graph_export.updated_at if graph_export.state == "finished" else None,
        "state": graph_export.state
    }
    
    return GraphExportCompactResponseWrapper(data=GraphExportCompact(**export_data))

