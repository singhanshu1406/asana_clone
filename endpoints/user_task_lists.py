from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from utils import generate_gid
from models.user_task_list import UserTaskList
from models.user import User
from models.workspace import Workspace
from schemas.user_task_list import (
    UserTaskListResponse, UserTaskListResponseWrapper
)

router = APIRouter()


@router.get("/users/{user_gid}/user_task_list", response_model=UserTaskListResponseWrapper)
def get_user_task_list(
    user_gid: str = Path(..., description="Globally unique identifier for the user"),
    workspace: Optional[str] = Query(None, description="The workspace in which to get the user task list"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get User Task List (GET request): Returns the full user task list record.
    """
    # Handle "me" special case
    if user_gid.lower() == "me":
        user = db.query(User).first()
    else:
        try:
            user_id = int(user_gid)
            user = db.query(User).filter(User.id == user_id).first()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user GID format"
            )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(UserTaskList).filter(UserTaskList.owner_id == user.id)
    
    if workspace:
        try:
            workspace_id = int(workspace)
            query = query.filter(UserTaskList.workspace_id == workspace_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workspace GID format"
            )
    
    user_task_list = query.first()
    if not user_task_list:
        # Create default if not exists
        user_task_list = UserTaskList(
            gid=generate_gid(),
            resource_type="user_task_list",
            name=f"My tasks",
            owner_id=user.id,
            workspace_id=workspace_id if workspace else None
        )
        db.add(user_task_list)
        db.commit()
        db.refresh(user_task_list)
    
    owner_obj = {
        "gid": user.gid,
        "resource_type": "user",
        "name": user.name or "",
        "email": user.email
    }
    
    workspace_obj = None
    if user_task_list.workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == user_task_list.workspace_id).first()
        if workspace:
            workspace_obj = {
                "gid": workspace.gid,
                "resource_type": "workspace",
                "name": workspace.name,
                "is_organization": workspace.is_organization
            }
    
    task_list_data = {
        "gid": user_task_list.gid,
        "resource_type": user_task_list.resource_type,
        "name": user_task_list.name,
        "owner": owner_obj,
        "workspace": workspace_obj
    }
    
    return UserTaskListResponseWrapper(data=UserTaskListResponse(**task_list_data))

