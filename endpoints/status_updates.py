from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.status_update import StatusUpdate
from models.user import User
from schemas.status_update import (
    StatusUpdateResponse, StatusUpdateResponseWrapper, StatusUpdateListResponse,
    StatusUpdateCompact, StatusUpdateRequest, EmptyResponse
)

router = APIRouter()


@router.get("/status_updates/{status_update_gid}", response_model=StatusUpdateResponseWrapper)
def get_status_update(
    status_update_gid: str = Path(..., description="Globally unique identifier for the status update"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Status Update (GET request): Returns the complete status update record.
    """
    try:
        status_id = int(status_update_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status update GID format"
        )
    
    status_update = db.query(StatusUpdate).filter(StatusUpdate.id == status_id).first()
    if not status_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status update not found"
        )
    
    author_obj = None
    if status_update.author_id:
        author = db.query(User).filter(User.id == status_update.author_id).first()
        if author:
            author_obj = {
                "gid": author.gid,
                "resource_type": "user",
                "name": author.name or "",
                "email": author.email
            }
    
    status_data = {
        "gid": status_update.gid,
        "resource_type": status_update.resource_type,
        "title": status_update.title,
        "resource_subtype": status_update.resource_subtype,
        "text": status_update.text,
        "html_text": status_update.html_text,
        "status_type": status_update.status_type or "on_track",
        "author": author_obj,
        "created_at": status_update.created_at,
        "created_by": author_obj
    }
    
    return StatusUpdateResponseWrapper(data=StatusUpdateResponse(**status_data))


@router.post("/status_updates", response_model=StatusUpdateResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_status_update(
    status_data: StatusUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Status Update (POST request): Creates a new status update.
    """
    try:
        parent_id = int(status_data.parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent GID format"
        )
    
    status_update = StatusUpdate(
        gid=generate_gid(),
        resource_type="status_update",
        text=status_data.text,
        html_text=status_data.html_text,
        status_type=status_data.status_type,
        title=f"Status Update",
        author_id=1,  # Default user
        resource_subtype="project_status_update"
    )
    
    db.add(status_update)
    db.commit()
    db.refresh(status_update)
    
    status_response = StatusUpdateResponse(
        gid=status_update.gid,
        resource_type=status_update.resource_type,
        title=status_update.title,
        resource_subtype=status_update.resource_subtype,
        text=status_update.text,
        html_text=status_update.html_text,
        status_type=status_update.status_type,
        created_at=status_update.created_at
    )
    
    return StatusUpdateResponseWrapper(data=status_response)


@router.delete("/status_updates/{status_update_gid}", response_model=EmptyResponse)
def delete_status_update(
    status_update_gid: str = Path(..., description="Globally unique identifier for the status update"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Status Update (DELETE request): A specific, existing status update can be deleted.
    """
    status_update = db.query(StatusUpdate).filter(StatusUpdate.gid == status_update_gid).first()
    if not status_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status update not found"
        )
    
    try:
        db.delete(status_update)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete status update: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting status update: {str(e)}"
        )
    
    return EmptyResponse()

