from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.task import Task
from models.user import User
from models.workspace import Workspace
from schemas.task import (
    TaskResponse, TaskResponseWrapper, TaskListResponse, TaskCompact,
    TaskRequest, TaskUpdateRequest, TaskAddFollowersRequest, TaskRemoveFollowersRequest,
    TaskAddProjectRequest, TaskRemoveProjectRequest, TaskAddTagRequest, TaskRemoveTagRequest,
    TaskSetParentRequest, ModifyDependenciesRequest, ModifyDependentsRequest,
    TaskDuplicateRequest, TaskCountResponse, TaskCountResponseWrapper, EmptyResponse
)

router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
def get_tasks(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    assignee: Optional[str] = Query(None, description="The assignee to filter tasks on"),
    project: Optional[str] = Query(None, description="The project to filter tasks on"),
    section: Optional[str] = Query(None, description="The section to filter tasks on"),
    completed_since: Optional[str] = Query(None, description="Only return tasks that are either incomplete or that have been completed since this time"),
    modified_since: Optional[str] = Query(None, description="Only return tasks that have been modified since the given time"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Tasks (GET request): Returns compact task records.
    """
    query = db.query(Task)
    
    if workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        query = query.filter(Task.workspace_id == workspace_obj.id)
    
    if assignee:
        if assignee.lower() == "me":
            # Would need current user context
            pass
        else:
            assignee_obj = db.query(User).filter(User.gid == assignee).first()
            if assignee_obj:
                query = query.filter(Task.assignee_id == assignee_obj.id)
    
    tasks = query.limit(limit).all()
    
    task_compacts = []
    for task in tasks:
        task_data = {
            "gid": task.gid,
            "resource_type": task.resource_type,
            "name": task.name,
            "resource_subtype": "default_task"
        }
        task_compacts.append(TaskCompact(**task_data))
    
    return TaskListResponse(data=task_compacts)


@router.get("/tasks/{task_gid}", response_model=TaskResponseWrapper)
def get_task(
    task_gid: str = Path(..., description="Globally unique identifier for the task"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Task (GET request): Returns the complete task record.
    """
    task = db.query(Task).filter(Task.gid == task_gid).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task_data = {
        "gid": task.gid,
        "resource_type": task.resource_type,
        "name": task.name,
        "resource_subtype": "default_task",
        "completed": task.completed,
        "completed_at": task.completed_at,
        "due_on": task.due_on,
        "due_at": task.due_at,
        "start_on": task.start_on,
        "notes": task.notes,
        "num_likes": task.num_likes,
        "num_subtasks": task.num_subtasks,
        "created_at": task.created_at,
        "modified_at": task.updated_at
    }
    
    return TaskResponseWrapper(data=TaskResponse(**task_data))


@router.post("/tasks", response_model=TaskResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Task (POST request): Creates a new task.
    """
    task = Task(
        gid=generate_gid(),
        resource_type="task",
        name=task_data.name or "New Task"
    )
    
    if task_data.workspace:
        try:
            workspace_id = int(task_data.workspace)
            task.workspace_id = workspace_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workspace GID format"
            )
    
    if task_data.assignee:
        assignee_obj = db.query(User).filter(User.gid == task_data.assignee).first()
        if not assignee_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )
        task.assignee_id = assignee_obj.id
    
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.notes:
        task.notes = task_data.notes
    if task_data.due_on:
        task.due_on = task_data.due_on
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    task_response = TaskResponse(
        gid=task.gid,
        resource_type=task.resource_type,
        name=task.name,
        resource_subtype="default_task",
        completed=task.completed,
        notes=task.notes,
        due_on=task.due_on
    )
    
    return TaskResponseWrapper(data=task_response)


@router.put("/tasks/{task_gid}", response_model=TaskResponseWrapper)
def update_task(
    task_gid: str = Path(..., description="Globally unique identifier for the task"),
    task_data: TaskUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Task (PUT request): An existing task can be updated.
    """
    task = db.query(Task).filter(Task.gid == task_gid).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task_data.name is not None:
        task.name = task_data.name
    if task_data.notes is not None:
        task.notes = task_data.notes
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.due_on is not None:
        task.due_on = task_data.due_on
    if task_data.start_on is not None:
        task.start_on = task_data.start_on
    
    db.commit()
    db.refresh(task)
    
    task_response = TaskResponse(
        gid=task.gid,
        resource_type=task.resource_type,
        name=task.name,
        resource_subtype="default_task",
        completed=task.completed,
        notes=task.notes,
        due_on=task.due_on
    )
    
    return TaskResponseWrapper(data=task_response)


@router.delete("/tasks/{task_gid}", response_model=EmptyResponse)
def delete_task(
    task_gid: str = Path(..., description="Globally unique identifier for the task"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Task (DELETE request): A specific, existing task can be deleted.
    """
    task = db.query(Task).filter(Task.gid == task_gid).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    try:
        db.delete(task)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete task: it has dependent records (e.g., stories, attachments). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )
    
    return EmptyResponse()

