from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.workspace import Workspace
from schemas.workspace import (
    WorkspaceResponse, WorkspaceResponseWrapper, WorkspaceListResponse,
    WorkspaceCompact, WorkspaceRequest, WorkspaceAddUserRequest,
    WorkspaceRemoveUserRequest, EmptyResponse
)

router = APIRouter()


@router.get("/workspaces", response_model=WorkspaceListResponse)
def get_workspaces(
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Workspaces (GET request): Returns compact workspace records.
    """
    workspaces = db.query(Workspace).limit(limit).all()
    
    workspace_compacts = []
    for workspace in workspaces:
        workspace_data = {
            "gid": workspace.gid,
            "resource_type": workspace.resource_type,
            "name": workspace.name,
            "is_organization": workspace.is_organization
        }
        workspace_compacts.append(WorkspaceCompact(**workspace_data))
    
    return WorkspaceListResponse(data=workspace_compacts)


@router.get("/workspaces/{workspace_gid}", response_model=WorkspaceResponseWrapper)
def get_workspace(
    workspace_gid: str = Path(..., description="Globally unique identifier for the workspace"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Workspace (GET request): Returns the complete workspace record.
    """
    try:
        workspace_id = int(workspace_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace GID format"
        )
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    workspace_data = {
        "gid": workspace.gid,
        "resource_type": workspace.resource_type,
        "name": workspace.name,
        "is_organization": workspace.is_organization,
        "email_domains": workspace.email_domains or []
    }
    
    return WorkspaceResponseWrapper(data=WorkspaceResponse(**workspace_data))

