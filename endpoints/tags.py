from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.tag import Tag
from models.workspace import Workspace
from schemas.tag import (
    TagResponse, TagResponseWrapper, TagListResponse,
    TagCompact, TagRequest, TagUpdateRequest, EmptyResponse
)

router = APIRouter()


@router.get("/tags", response_model=TagListResponse)
def get_tags(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Tags (GET request): Returns compact tag records.
    """
    query = db.query(Tag)
    
    if workspace:
        try:
            workspace_id = int(workspace)
            query = query.filter(Tag.workspace_id == workspace_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workspace GID format"
            )
    
    tags = query.limit(limit).all()
    
    tag_compacts = []
    for tag in tags:
        tag_data = {
            "gid": tag.gid,
            "resource_type": tag.resource_type,
            "name": tag.name
        }
        tag_compacts.append(TagCompact(**tag_data))
    
    return TagListResponse(data=tag_compacts)


@router.get("/tags/{tag_gid}", response_model=TagResponseWrapper)
def get_tag(
    tag_gid: str = Path(..., description="Globally unique identifier for the tag"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Tag (GET request): Returns the complete tag record.
    """
    try:
        tag_id = int(tag_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tag GID format"
        )
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    tag_data = {
        "gid": tag.gid,
        "resource_type": tag.resource_type,
        "name": tag.name,
        "color": tag.color,
        "notes": tag.notes,
        "created_at": tag.created_at
    }
    
    return TagResponseWrapper(data=TagResponse(**tag_data))


@router.post("/workspaces/{workspace_gid}/tags", response_model=TagResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_tag(
    workspace_gid: str = Path(..., description="Globally unique identifier for the workspace"),
    tag_data: TagRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Tag (POST request): Creates a new tag in a workspace.
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
    
    tag = Tag(
        gid=generate_gid(),
        resource_type="tag",
        name=tag_data.name or "New Tag",
        workspace_id=workspace_id,
        color=tag_data.color,
        notes=tag_data.notes
    )
    
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    tag_response = TagResponse(
        gid=tag.gid,
        resource_type=tag.resource_type,
        name=tag.name,
        color=tag.color,
        notes=tag.notes,
        created_at=tag.created_at
    )
    
    return TagResponseWrapper(data=tag_response)


@router.put("/tags/{tag_gid}", response_model=TagResponseWrapper)
def update_tag(
    tag_gid: str = Path(..., description="Globally unique identifier for the tag"),
    tag_data: TagUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Tag (PUT request): An existing tag can be updated.
    """
    try:
        tag_id = int(tag_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tag GID format"
        )
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    if tag_data.name is not None:
        tag.name = tag_data.name
    if tag_data.color is not None:
        tag.color = tag_data.color
    if tag_data.notes is not None:
        tag.notes = tag_data.notes
    
    db.commit()
    db.refresh(tag)
    
    tag_response = TagResponse(
        gid=tag.gid,
        resource_type=tag.resource_type,
        name=tag.name,
        color=tag.color,
        notes=tag.notes,
        created_at=tag.created_at
    )
    
    return TagResponseWrapper(data=tag_response)


@router.delete("/tags/{tag_gid}", response_model=EmptyResponse)
def delete_tag(
    tag_gid: str = Path(..., description="Globally unique identifier for the tag"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Tag (DELETE request): A specific, existing tag can be deleted.
    """
    tag = db.query(Tag).filter(Tag.gid == tag_gid).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    try:
        db.delete(tag)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tag: it has dependent records. Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tag: {str(e)}"
        )
    
    return EmptyResponse()

