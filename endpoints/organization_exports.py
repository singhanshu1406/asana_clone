from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.workspace import Workspace
from schemas.organization_export import (
    OrganizationExportResponse, OrganizationExportResponseWrapper,
    OrganizationExportRequest
)
from utils import generate_gid

router = APIRouter()


@router.post("/organization_exports", response_model=OrganizationExportResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_organization_export(
    export_data: OrganizationExportRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create an organization export request"""
    workspace = db.query(Workspace).filter(Workspace.gid == export_data.organization).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Organization not found")

    # In a real implementation, you'd create an OrganizationExport record
    # For now, we'll return a mock response
    export = OrganizationExportResponse(
        gid=generate_gid(),
        resource_type="organization_export",
        state="pending",
        download_url=None,
        organization=workspace,
        created_at=None
    )

    return OrganizationExportResponseWrapper(data=export)


@router.get("/organization_exports/{organization_export_gid}", response_model=OrganizationExportResponseWrapper)
def get_organization_export(
    organization_export_gid: str = Path(..., description="Globally unique identifier for the organization export."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get details on an org export request"""
    # In a real implementation, you'd query the OrganizationExport model
    # For now, we'll return a mock response
    export = OrganizationExportResponse(
        gid=organization_export_gid,
        resource_type="organization_export",
        state="completed",
        download_url="https://example.com/export.zip",
        organization=None,
        created_at=None
    )

    return OrganizationExportResponseWrapper(data=export)

