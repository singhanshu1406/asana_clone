from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from models.time_tracking_entry import TimeTrackingEntry
from models.task import Task
from models.project import Project
from models.user import User
from schemas.time_tracking_entry import (
    TimeTrackingEntryResponse, TimeTrackingEntryListResponse,
    TimeTrackingEntryResponseWrapper, TimeTrackingEntryRequest
)
from schemas.project_membership import EmptyResponse
from utils import generate_gid

router = APIRouter()


@router.get("/tasks/{task_gid}/time_tracking_entries", response_model=TimeTrackingEntryListResponse)
def get_time_tracking_entries_for_task(
    task_gid: str = Path(..., description="The task to operate on."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get time tracking entries for a task"""
    task = db.query(Task).filter(Task.gid == task_gid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    entries = db.query(TimeTrackingEntry).filter(TimeTrackingEntry.task_id == task.id).limit(limit).all()

    return TimeTrackingEntryListResponse(
        data=[TimeTrackingEntryResponse.from_orm(entry) for entry in entries]
    )


@router.post("/tasks/{task_gid}/time_tracking_entries", response_model=TimeTrackingEntryResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_time_tracking_entry(
    task_gid: str = Path(..., description="The task to operate on."),
    entry_data: TimeTrackingEntryRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create a time tracking entry"""
    task = db.query(Task).filter(Task.gid == task_gid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attributable_to_id = None
    if entry_data.attributable_to:
        project = db.query(Project).filter(Project.gid == entry_data.attributable_to).first()
        if project:
            attributable_to_id = project.id

    entry = TimeTrackingEntry(
        gid=generate_gid(),
        duration_minutes=entry_data.duration_minutes,
        entered_on=entry_data.entered_on,
        task_id=task.id,
        attributable_to_id=attributable_to_id,
        user_id=user.id,
        created_by_id=user.id
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return TimeTrackingEntryResponseWrapper(data=TimeTrackingEntryResponse.from_orm(entry))


@router.get("/time_tracking_entries/{time_tracking_entry_gid}", response_model=TimeTrackingEntryResponseWrapper)
def get_time_tracking_entry(
    time_tracking_entry_gid: str = Path(..., description="Globally unique identifier for the time tracking entry."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a time tracking entry"""
    entry = db.query(TimeTrackingEntry).filter(TimeTrackingEntry.gid == time_tracking_entry_gid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time tracking entry not found")

    return TimeTrackingEntryResponseWrapper(data=TimeTrackingEntryResponse.from_orm(entry))


@router.put("/time_tracking_entries/{time_tracking_entry_gid}", response_model=TimeTrackingEntryResponseWrapper)
def update_time_tracking_entry(
    time_tracking_entry_gid: str = Path(..., description="Globally unique identifier for the time tracking entry."),
    entry_data: TimeTrackingEntryRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Update a time tracking entry"""
    entry = db.query(TimeTrackingEntry).filter(TimeTrackingEntry.gid == time_tracking_entry_gid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time tracking entry not found")

    if entry_data.duration_minutes is not None:
        entry.duration_minutes = entry_data.duration_minutes
    if entry_data.entered_on is not None:
        entry.entered_on = entry_data.entered_on
    if entry_data.description is not None:
        entry.description = entry_data.description

    db.commit()
    db.refresh(entry)

    return TimeTrackingEntryResponseWrapper(data=TimeTrackingEntryResponse.from_orm(entry))


@router.delete("/time_tracking_entries/{time_tracking_entry_gid}", response_model=EmptyResponse)
def delete_time_tracking_entry(
    time_tracking_entry_gid: str = Path(..., description="Globally unique identifier for the time tracking entry."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Delete a time tracking entry"""
    entry = db.query(TimeTrackingEntry).filter(TimeTrackingEntry.gid == time_tracking_entry_gid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time tracking entry not found")

    try:
        db.delete(entry)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete time tracking entry: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting time tracking entry: {str(e)}"
        )

    return EmptyResponse()

