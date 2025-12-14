from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from models.task_template import TaskTemplate
from models.project import Project
from models.user import User
from models.task import Task
from schemas.task_template import (
    TaskTemplateResponse, TaskTemplateListResponse, TaskTemplateResponseWrapper,
    TaskTemplateRequest, TaskTemplateInstantiateRequest
)
from schemas.project_membership import EmptyResponse
from schemas.task import TaskResponse, TaskResponseWrapper
from utils import generate_gid
import json

router = APIRouter()


@router.get("/task_templates", response_model=TaskTemplateListResponse)
def get_task_templates(
    project: str = Query(..., description="Globally unique identifier for the project."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get task templates"""
    project_obj = db.query(Project).filter(Project.gid == project).first()
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    task_templates = db.query(TaskTemplate).filter(TaskTemplate.project_id == project_obj.id).limit(limit).all()

    return TaskTemplateListResponse(
        data=[TaskTemplateResponse.from_orm(tt) for tt in task_templates]
    )


@router.post("/task_templates", response_model=TaskTemplateResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_task_template(
    task_template_data: TaskTemplateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create a task template"""
    project = db.query(Project).filter(Project.gid == task_template_data.project).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task_template = TaskTemplate(
        gid=generate_gid(),
        name=task_template_data.name,
        template=task_template_data.template,
        project_id=project.id,
        created_by_id=user.id
    )

    db.add(task_template)
    db.commit()
    db.refresh(task_template)

    return TaskTemplateResponseWrapper(data=TaskTemplateResponse.from_orm(task_template))


@router.get("/task_templates/{task_template_gid}", response_model=TaskTemplateResponseWrapper)
def get_task_template(
    task_template_gid: str = Path(..., description="Globally unique identifier for the task template."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a task template"""
    task_template = db.query(TaskTemplate).filter(TaskTemplate.gid == task_template_gid).first()
    if not task_template:
        raise HTTPException(status_code=404, detail="Task template not found")

    return TaskTemplateResponseWrapper(data=TaskTemplateResponse.from_orm(task_template))


@router.post("/task_templates/{task_template_gid}/instantiate", response_model=TaskResponseWrapper)
def instantiate_task_template(
    task_template_gid: str = Path(..., description="Globally unique identifier for the task template."),
    instantiate_data: TaskTemplateInstantiateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Instantiate a task template"""
    task_template = db.query(TaskTemplate).filter(TaskTemplate.gid == task_template_gid).first()
    if not task_template:
        raise HTTPException(status_code=404, detail="Task template not found")

    project_id = task_template.project_id
    if instantiate_data.project:
        project = db.query(Project).filter(Project.gid == instantiate_data.project).first()
        if project:
            project_id = project.id

    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create task from template
    task_name = instantiate_data.name if instantiate_data.name else task_template.name
    task = Task(
        gid=generate_gid(),
        name=task_name,
        project_id=project_id,
        created_by_id=user.id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponseWrapper(data=TaskResponse.from_orm(task))


@router.delete("/task_templates/{task_template_gid}", response_model=EmptyResponse)
def delete_task_template(
    task_template_gid: str = Path(..., description="Globally unique identifier for the task template."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Delete a task template"""
    task_template = db.query(TaskTemplate).filter(TaskTemplate.gid == task_template_gid).first()
    if not task_template:
        raise HTTPException(status_code=404, detail="Task template not found")

    try:
        db.delete(task_template)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete task template: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task template: {str(e)}"
        )

    return EmptyResponse()

