from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from utils import generate_gid
from models.resource_export import ResourceExport
from models.job import Job
from schemas.resource_export import (
    ResourceExportResponse, ResourceExportResponseWrapper,
    ResourceExportRequest, ResourceExportCompactResponseWrapper
)

router = APIRouter()


@router.post("/resource_exports", response_model=ResourceExportResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_resource_export(
    export_data: ResourceExportRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Resource Export (POST request): Creates a new resource export job.
    """
    # Create a job for the export
    job = Job(
        gid=generate_gid(),
        resource_type="job",
        resource_subtype="export_request",
        status="in_progress"
    )
    
    # Create the resource export
    resource_export = ResourceExport(
        gid=generate_gid(),
        resource_type="resource_export",
        state="pending"
    )
    
    db.add(job)
    db.add(resource_export)
    db.commit()
    db.refresh(job)
    db.refresh(resource_export)
    
    export_response = ResourceExportResponse(
        gid=job.gid,
        resource_type="job",
        resource_subtype="export_request",
        status="in_progress",
        new_resource_export={
            "gid": resource_export.gid,
            "resource_type": resource_export.resource_type,
            "created_at": resource_export.created_at,
            "download_url": None,
            "completed_at": None
        }
    )
    
    return ResourceExportResponseWrapper(data=export_response)


@router.get("/resource_exports/{resource_export_gid}", response_model=ResourceExportCompactResponseWrapper)
def get_resource_export(
    resource_export_gid: str = Path(..., description="Globally unique identifier for the resource export"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Resource Export (GET request): Returns the complete resource export record.
    """
    try:
        export_id = int(resource_export_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource export GID format"
        )
    
    resource_export = db.query(ResourceExport).filter(ResourceExport.id == export_id).first()
    if not resource_export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource export not found"
        )
    
    export_data = {
        "gid": resource_export.gid,
        "resource_type": resource_export.resource_type,
        "created_at": resource_export.created_at,
        "download_url": resource_export.download_url,
        "completed_at": resource_export.updated_at if resource_export.state == "finished" else None
    }
    
    return ResourceExportCompactResponseWrapper(data=ResourceExportCompact(**export_data))

