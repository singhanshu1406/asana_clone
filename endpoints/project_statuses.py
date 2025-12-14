from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.project_status import ProjectStatus
from models.project import Project
from models.user import User
from schemas.project_status import (
    ProjectStatusResponse, ProjectStatusResponseWrapper, ProjectStatusListResponse,
    ProjectStatusCompact, ProjectStatusRequest, EmptyResponse
)

router = APIRouter()


@router.get("/projects/{project_gid}/project_statuses", response_model=ProjectStatusListResponse)
def get_project_statuses(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Project Statuses (GET request): Returns compact project status records.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    statuses = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).limit(limit).all()
    
    status_compacts = []
    for status in statuses:
        status_data = {
            "gid": status.gid,
            "resource_type": status.resource_type,
            "title": status.title
        }
        status_compacts.append(ProjectStatusCompact(**status_data))
    
    return ProjectStatusListResponse(data=status_compacts)


@router.get("/project_statuses/{project_status_gid}", response_model=ProjectStatusResponseWrapper)
def get_project_status(
    project_status_gid: str = Path(..., description="Globally unique identifier for the project status"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Project Status (GET request): Returns the complete project status record.
    """
    try:
        status_id = int(project_status_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project status GID format"
        )
    
    project_status = db.query(ProjectStatus).filter(ProjectStatus.id == status_id).first()
    if not project_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project status not found"
        )
    
    author_obj = None
    if project_status.author_id:
        author = db.query(User).filter(User.id == project_status.author_id).first()
        if author:
            author_obj = {
                "gid": author.gid,
                "resource_type": "user",
                "name": author.name or "",
                "email": author.email
            }
    
    status_data = {
        "gid": project_status.gid,
        "resource_type": project_status.resource_type,
        "title": project_status.title,
        "text": project_status.text,
        "html_text": project_status.html_text,
        "color": project_status.color,
        "author": author_obj,
        "created_at": project_status.created_at,
        "created_by": author_obj,
        "modified_at": project_status.created_at
    }
    
    return ProjectStatusResponseWrapper(data=ProjectStatusResponse(**status_data))


@router.post("/projects/{project_gid}/project_statuses", response_model=ProjectStatusResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_project_status(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    status_data: ProjectStatusRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Project Status (POST request): Creates a new project status update.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project_status = ProjectStatus(
        gid=generate_gid(),
        resource_type="project_status",
        project_id=project_id,
        text=status_data.text,
        html_text=status_data.html_text,
        color=status_data.color or "green",
        title=f"Status Update",
        author_id=1  # Default user
    )
    
    db.add(project_status)
    db.commit()
    db.refresh(project_status)
    
    status_response = ProjectStatusResponse(
        gid=project_status.gid,
        resource_type=project_status.resource_type,
        title=project_status.title,
        text=project_status.text,
        html_text=project_status.html_text,
        color=project_status.color,
        created_at=project_status.created_at
    )
    
    return ProjectStatusResponseWrapper(data=status_response)


@router.delete("/project_statuses/{project_status_gid}", response_model=EmptyResponse)
def delete_project_status(
    project_status_gid: str = Path(..., description="Globally unique identifier for the project status"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Project Status (DELETE request): A specific, existing project status can be deleted.
    """
    project_status = db.query(ProjectStatus).filter(ProjectStatus.gid == project_status_gid).first()
    if not project_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project status not found"
        )
    
    try:
        db.delete(project_status)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project status: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project status: {str(e)}"
        )
    
    return EmptyResponse()

