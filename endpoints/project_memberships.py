from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.project_membership import ProjectMembership
from models.project import Project
from models.user import User
from models.team import Team
from schemas.project_membership import (
    ProjectMembershipResponse, ProjectMembershipResponseWrapper,
    ProjectMembershipListResponse, ProjectMembershipCompact,
    ProjectMembershipRequest, EmptyResponse
)

router = APIRouter()


@router.get("/projects/{project_gid}/project_memberships", response_model=ProjectMembershipListResponse)
def get_project_memberships(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Project Memberships (GET request): Returns compact project membership records.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    query = db.query(ProjectMembership).filter(ProjectMembership.project_id == project_id)
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(ProjectMembership.user_id == user_obj.id)
        else:
            try:
                user_id = int(user)
                query = query.filter(ProjectMembership.user_id == user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user GID format"
                )
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        project_obj = db.query(Project).filter(Project.id == membership.project_id).first()
        member_obj = None
        
        if membership.user_id:
            user_obj = db.query(User).filter(User.id == membership.user_id).first()
            if user_obj:
                member_obj = {
                    "gid": user_obj.gid,
                    "resource_type": "user",
                    "name": user_obj.name or ""
                }
        elif membership.team_id:
            team_obj = db.query(Team).filter(Team.id == membership.team_id).first()
            if team_obj:
                member_obj = {
                    "gid": team_obj.gid,
                    "resource_type": "team",
                    "name": team_obj.name or ""
                }
        
        membership_data = {
            "gid": membership.gid,
            "resource_type": membership.resource_type,
            "parent": {
                "gid": project_obj.gid if project_obj else "",
                "resource_type": "project",
                "name": project_obj.name if project_obj else ""
            } if project_obj else None,
            "member": member_obj,
            "access_level": membership.write_access or "viewer"
        }
        membership_compacts.append(ProjectMembershipCompact(**membership_data))
    
    return ProjectMembershipListResponse(data=membership_compacts)


@router.get("/project_memberships/{project_membership_gid}", response_model=ProjectMembershipResponseWrapper)
def get_project_membership(
    project_membership_gid: str = Path(..., description="Globally unique identifier for the project membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Project Membership (GET request): Returns the complete project membership record.
    """
    try:
        membership_id = int(project_membership_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project membership GID format"
        )
    
    membership = db.query(ProjectMembership).filter(ProjectMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project membership not found"
        )
    
    project_obj = db.query(Project).filter(Project.id == membership.project_id).first()
    member_obj = None
    
    if membership.user_id:
        user_obj = db.query(User).filter(User.id == membership.user_id).first()
        if user_obj:
            member_obj = {
                "gid": user_obj.gid,
                "resource_type": "user",
                "name": user_obj.name or ""
            }
    elif membership.team_id:
        team_obj = db.query(Team).filter(Team.id == membership.team_id).first()
        if team_obj:
            member_obj = {
                "gid": team_obj.gid,
                "resource_type": "team",
                "name": team_obj.name or ""
            }
    
    membership_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "parent": {
            "gid": project_obj.gid if project_obj else "",
            "resource_type": "project",
            "name": project_obj.name if project_obj else ""
        } if project_obj else None,
        "member": member_obj,
        "access_level": membership.write_access or "viewer"
    }
    
    return ProjectMembershipResponseWrapper(data=ProjectMembershipResponse(**membership_data))


@router.post("/projects/{project_gid}/project_memberships", response_model=ProjectMembershipResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_project_membership(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    membership_data: ProjectMembershipRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Project Membership (POST request): Creates a new project membership.
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
    
    membership = ProjectMembership(
        gid=generate_gid(),
        resource_type="project_membership",
        project_id=project_id
    )
    
    if membership_data.user:
        try:
            user_id = int(membership_data.user)
            membership.user_id = user_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user GID format"
            )
    
    if membership_data.team:
        try:
            team_id = int(membership_data.team)
            membership.team_id = team_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid team GID format"
            )
    
    if membership_data.access_level:
        membership.write_access = membership_data.access_level
    
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    # Build response
    member_obj = None
    if membership.user_id:
        user_obj = db.query(User).filter(User.id == membership.user_id).first()
        if user_obj:
            member_obj = {
                "gid": user_obj.gid,
                "resource_type": "user",
                "name": user_obj.name or ""
            }
    elif membership.team_id:
        team_obj = db.query(Team).filter(Team.id == membership.team_id).first()
        if team_obj:
            member_obj = {
                "gid": team_obj.gid,
                "resource_type": "team",
                "name": team_obj.name or ""
            }
    
    membership_response_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "parent": {
            "gid": project.gid,
            "resource_type": "project",
            "name": project.name
        },
        "member": member_obj,
        "access_level": membership.write_access or "viewer"
    }
    
    return ProjectMembershipResponseWrapper(data=ProjectMembershipResponse(**membership_response_data))


@router.delete("/project_memberships/{project_membership_gid}", response_model=EmptyResponse)
def delete_project_membership(
    project_membership_gid: str = Path(..., description="Globally unique identifier for the project membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Project Membership (DELETE request): A specific, existing project membership can be deleted.
    """
    membership = db.query(ProjectMembership).filter(ProjectMembership.gid == project_membership_gid).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project membership not found"
        )
    
    try:
        db.delete(membership)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project membership: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project membership: {str(e)}"
        )
    
    return EmptyResponse()

