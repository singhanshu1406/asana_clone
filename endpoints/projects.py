from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.project import Project
from models.user import User
from models.workspace import Workspace
from models.team import Team
from schemas.project import (
    ProjectResponse, ProjectResponseWrapper, ProjectListResponse,
    ProjectCompact, ProjectRequest, ProjectUpdateRequest, EmptyResponse
)

router = APIRouter()


@router.get("/projects", response_model=ProjectListResponse)
def get_projects(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    team: Optional[str] = Query(None, description="The team to filter projects on"),
    archived: Optional[bool] = Query(None, description="Only return projects whose archived field takes on the value of this parameter"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Projects (GET request): Returns compact project records.
    """
    query = db.query(Project)
    
    if workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        query = query.filter(Project.workspace_id == workspace_obj.id)
    
    if team:
        team_obj = db.query(Team).filter(Team.gid == team).first()
        if not team_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        query = query.filter(Project.team_id == team_obj.id)
    
    if archived is not None:
        query = query.filter(Project.archived == archived)
    
    projects = query.limit(limit).all()
    
    project_compacts = []
    for project in projects:
        project_data = {
            "gid": project.gid,
            "resource_type": project.resource_type,
            "name": project.name,
            "resource_subtype": None
        }
        project_compacts.append(ProjectCompact(**project_data))
    
    return ProjectListResponse(data=project_compacts)


@router.get("/projects/{project_gid}", response_model=ProjectResponseWrapper)
def get_project(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Project (GET request): Returns the complete project record.
    """
    project = db.query(Project).filter(Project.gid == project_gid).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project_data = {
        "gid": project.gid,
        "resource_type": project.resource_type,
        "name": project.name,
        "archived": project.archived,
        "color": project.color,
        "created_at": project.created_at,
        "default_view": project.default_view,
        "due_on": project.due_date,
        "start_on": project.start_on,
        "notes": project.notes,
        "public": project.public
    }
    
    return ProjectResponseWrapper(data=ProjectResponse(**project_data))


@router.post("/projects", response_model=ProjectResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Project (POST request): Creates a new project in a workspace or team.
    """
    project = Project(
        gid=generate_gid(),
        resource_type="project",
        name=project_data.name or "New Project"
    )
    
    if project_data.workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == project_data.workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        project.workspace_id = workspace_obj.id
    
    if project_data.team:
        team_obj = db.query(Team).filter(Team.gid == project_data.team).first()
        if not team_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        project.team_id = team_obj.id
    
    if project_data.archived is not None:
        project.archived = project_data.archived
    if project_data.color:
        project.color = project_data.color
    if project_data.notes:
        project.notes = project_data.notes
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    project_response = ProjectResponse(
        gid=project.gid,
        resource_type=project.resource_type,
        name=project.name,
        archived=project.archived,
        color=project.color,
        created_at=project.created_at,
        notes=project.notes
    )
    
    return ProjectResponseWrapper(data=project_response)


@router.put("/projects/{project_gid}", response_model=ProjectResponseWrapper)
def update_project(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    project_data: ProjectUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Project (PUT request): An existing project can be updated.
    """
    project = db.query(Project).filter(Project.gid == project_gid).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.archived is not None:
        project.archived = project_data.archived
    if project_data.color is not None:
        project.color = project_data.color
    if project_data.notes is not None:
        project.notes = project_data.notes
    if project_data.due_on is not None:
        project.due_date = project_data.due_on
    if project_data.start_on is not None:
        project.start_on = project_data.start_on
    
    db.commit()
    db.refresh(project)
    
    project_response = ProjectResponse(
        gid=project.gid,
        resource_type=project.resource_type,
        name=project.name,
        archived=project.archived,
        color=project.color,
        created_at=project.created_at,
        notes=project.notes
    )
    
    return ProjectResponseWrapper(data=project_response)


@router.delete("/projects/{project_gid}", response_model=EmptyResponse)
def delete_project(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Project (DELETE request): A specific, existing project can be deleted.
    """
    project = db.query(Project).filter(Project.gid == project_gid).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        db.delete(project)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project: it has dependent records (e.g., tasks, sections, project memberships). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        )
    
    return EmptyResponse()

