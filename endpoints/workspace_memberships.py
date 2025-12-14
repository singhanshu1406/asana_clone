from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.workspace_membership import WorkspaceMembership
from models.workspace import Workspace
from models.user import User
from schemas.workspace_membership import (
    WorkspaceMembershipResponse, WorkspaceMembershipResponseWrapper,
    WorkspaceMembershipListResponse, WorkspaceMembershipCompact
)

router = APIRouter()


@router.get("/workspaces/{workspace_gid}/workspace_memberships", response_model=WorkspaceMembershipListResponse)
def get_workspace_memberships(
    workspace_gid: str = Path(..., description="Globally unique identifier for the workspace"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Workspace Memberships (GET request): Returns compact workspace membership records.
    """
    try:
        workspace_id = int(workspace_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace GID format"
        )
    
    query = db.query(WorkspaceMembership).filter(WorkspaceMembership.workspace_id == workspace_id)
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(WorkspaceMembership.user_id == user_obj.id)
        else:
            try:
                user_id = int(user)
                query = query.filter(WorkspaceMembership.user_id == user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user GID format"
                )
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        workspace_obj = db.query(Workspace).filter(Workspace.id == membership.workspace_id).first()
        user_obj = db.query(User).filter(User.id == membership.user_id).first() if membership.user_id else None
        
        membership_data = {
            "gid": membership.gid,
            "resource_type": membership.resource_type,
            "user": {
                "gid": user_obj.gid,
                "resource_type": "user",
                "name": user_obj.name or "",
                "email": user_obj.email
            } if user_obj else None,
            "workspace": {
                "gid": workspace_obj.gid if workspace_obj else "",
                "resource_type": "workspace",
                "name": workspace_obj.name if workspace_obj else "",
                "is_organization": workspace_obj.is_organization if workspace_obj else None
            } if workspace_obj else None
        }
        membership_compacts.append(WorkspaceMembershipCompact(**membership_data))
    
    return WorkspaceMembershipListResponse(data=membership_compacts)


@router.get("/workspace_memberships/{workspace_membership_gid}", response_model=WorkspaceMembershipResponseWrapper)
def get_workspace_membership(
    workspace_membership_gid: str = Path(..., description="Globally unique identifier for the workspace membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Workspace Membership (GET request): Returns the complete workspace membership record.
    """
    try:
        membership_id = int(workspace_membership_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace membership GID format"
        )
    
    membership = db.query(WorkspaceMembership).filter(WorkspaceMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace membership not found"
        )
    
    workspace_obj = db.query(Workspace).filter(Workspace.id == membership.workspace_id).first()
    user_obj = db.query(User).filter(User.id == membership.user_id).first() if membership.user_id else None
    
    membership_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "user": {
            "gid": user_obj.gid,
            "resource_type": "user",
            "name": user_obj.name or "",
            "email": user_obj.email
        } if user_obj else None,
        "workspace": {
            "gid": workspace_obj.gid if workspace_obj else "",
            "resource_type": "workspace",
            "name": workspace_obj.name if workspace_obj else "",
            "is_organization": workspace_obj.is_organization if workspace_obj else None
        } if workspace_obj else None,
        "is_active": membership.is_active,
        "is_admin": membership.is_admin,
        "is_guest": False,
        "is_view_only": False,
        "vacation_dates": None,
        "created_at": membership.created_at
    }
    
    return WorkspaceMembershipResponseWrapper(data=WorkspaceMembershipResponse(**membership_data))

