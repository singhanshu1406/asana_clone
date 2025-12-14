from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.story import Story
from models.task import Task
from models.user import User
from schemas.story import (
    StoryResponse, StoryResponseWrapper, StoryListResponse,
    StoryCompact, StoryRequest, EmptyResponse
)

router = APIRouter()


@router.get("/tasks/{task_gid}/stories", response_model=StoryListResponse)
def get_stories(
    task_gid: str = Path(..., description="Globally unique identifier for the task"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Stories (GET request): Returns compact story records.
    """
    try:
        task_id = int(task_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task GID format"
        )
    
    stories = db.query(Story).filter(Story.task_id == task_id).limit(limit).all()
    
    story_compacts = []
    for story in stories:
        created_by_obj = None
        if story.created_by_id:
            user = db.query(User).filter(User.id == story.created_by_id).first()
            if user:
                created_by_obj = {
                    "gid": user.gid,
                    "resource_type": "user",
                    "name": user.name or "",
                    "email": user.email
                }
        
        story_data = {
            "gid": story.gid,
            "resource_type": story.resource_type,
            "created_at": story.created_at,
            "resource_subtype": story.type or "comment_added",
            "text": story.text,
            "created_by": created_by_obj
        }
        story_compacts.append(StoryCompact(**story_data))
    
    return StoryListResponse(data=story_compacts)


@router.get("/stories/{story_gid}", response_model=StoryResponseWrapper)
def get_story(
    story_gid: str = Path(..., description="Globally unique identifier for the story"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Story (GET request): Returns the complete story record.
    """
    try:
        story_id = int(story_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid story GID format"
        )
    
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    story_data = {
        "gid": story.gid,
        "resource_type": story.resource_type,
        "created_at": story.created_at,
        "resource_subtype": story.type or "comment_added",
        "text": story.text,
        "html_text": story.html_text,
        "is_pinned": story.is_pinned
    }
    
    return StoryResponseWrapper(data=StoryResponse(**story_data))


@router.post("/tasks/{task_gid}/stories", response_model=StoryResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_story(
    task_gid: str = Path(..., description="Globally unique identifier for the task"),
    story_data: StoryRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Story (POST request): Creates a new story on a task.
    """
    try:
        task_id = int(task_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task GID format"
        )
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    story = Story(
        gid=generate_gid(),
        resource_type="story",
        task_id=task_id,
        text=story_data.text or "",
        html_text=story_data.html_text,
        type="comment_added",
        is_pinned=story_data.is_pinned or False,
        created_by_id=1  # Default user
    )
    
    db.add(story)
    db.commit()
    db.refresh(story)
    
    story_response = StoryResponse(
        gid=story.gid,
        resource_type=story.resource_type,
        created_at=story.created_at,
        resource_subtype=story.type or "comment_added",
        text=story.text,
        html_text=story.html_text,
        is_pinned=story.is_pinned
    )
    
    return StoryResponseWrapper(data=story_response)


@router.delete("/stories/{story_gid}", response_model=EmptyResponse)
def delete_story(
    story_gid: str = Path(..., description="Globally unique identifier for the story"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Story (DELETE request): A specific, existing story can be deleted.
    """
    story = db.query(Story).filter(Story.gid == story_gid).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    try:
        db.delete(story)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete story: it has dependent records (e.g., reactions). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting story: {str(e)}"
        )
    
    return EmptyResponse()

