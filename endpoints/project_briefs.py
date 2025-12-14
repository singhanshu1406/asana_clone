from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.project_brief import ProjectBrief
from models.project import Project
from schemas.project_brief import (
    ProjectBriefResponse, ProjectBriefResponseWrapper, EmptyResponse,
    ProjectBriefRequest
)

router = APIRouter()


@router.get("/projects/{project_gid}/project_brief", response_model=ProjectBriefResponseWrapper)
def get_project_brief(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Project Brief (GET request): Returns the complete project brief record.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    project_brief = db.query(ProjectBrief).filter(ProjectBrief.project_id == project_id).first()
    if not project_brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project brief not found"
        )
    
    brief_data = {
        "gid": project_brief.gid,
        "resource_type": project_brief.resource_type,
        "title": project_brief.title,
        "html_text": project_brief.html_text,
        "text": project_brief.text
    }
    
    return ProjectBriefResponseWrapper(data=ProjectBriefResponse(**brief_data))


@router.put("/projects/{project_gid}/project_brief", response_model=ProjectBriefResponseWrapper)
def update_project_brief(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    brief_data: ProjectBriefRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Project Brief (PUT request): Updates the project brief for a project.
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
    
    project_brief = db.query(ProjectBrief).filter(ProjectBrief.project_id == project_id).first()
    
    if not project_brief:
        # Create new brief
        project_brief = ProjectBrief(
            gid=generate_gid(),
            resource_type="project_brief",
            project_id=project_id,
            title=brief_data.title,
            text=brief_data.text,
            html_text=brief_data.html_text
        )
        db.add(project_brief)
    else:
        # Update existing brief
        if brief_data.title is not None:
            project_brief.title = brief_data.title
        if brief_data.text is not None:
            project_brief.text = brief_data.text
        if brief_data.html_text is not None:
            project_brief.html_text = brief_data.html_text
    
    db.commit()
    db.refresh(project_brief)
    
    brief_response = ProjectBriefResponse(
        gid=project_brief.gid,
        resource_type=project_brief.resource_type,
        title=project_brief.title,
        html_text=project_brief.html_text,
        text=project_brief.text
    )
    
    return ProjectBriefResponseWrapper(data=brief_response)


@router.delete("/projects/{project_gid}/project_brief", response_model=EmptyResponse)
def delete_project_brief(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Project Brief (DELETE request): Deletes the project brief for a project.
    """
    project = db.query(Project).filter(Project.gid == project_gid).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project_brief = db.query(ProjectBrief).filter(ProjectBrief.project_id == project.id).first()
    if not project_brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project brief not found"
        )
    
    try:
        db.delete(project_brief)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project brief: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project brief: {str(e)}"
        )
    
    return EmptyResponse()

