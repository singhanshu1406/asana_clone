from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.team import Team
from models.workspace import Workspace
from schemas.team import (
    TeamResponse, TeamResponseWrapper, TeamListResponse,
    TeamCompact, TeamRequest, TeamAddUserRequest, TeamRemoveUserRequest, EmptyResponse
)

router = APIRouter()


@router.get("/teams", response_model=TeamListResponse)
def get_teams(
    organization: Optional[str] = Query(None, description="The organization to filter results on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Teams (GET request): Returns compact team records.
    """
    query = db.query(Team)
    
    if organization:
        org_obj = db.query(Workspace).filter(Workspace.gid == organization).first()
        if not org_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        query = query.filter(Team.organization_id == org_obj.id)
    
    teams = query.limit(limit).all()
    
    team_compacts = []
    for team in teams:
        team_data = {
            "gid": team.gid,
            "resource_type": team.resource_type,
            "name": team.name
        }
        team_compacts.append(TeamCompact(**team_data))
    
    return TeamListResponse(data=team_compacts)


@router.get("/teams/{team_gid}", response_model=TeamResponseWrapper)
def get_team(
    team_gid: str = Path(..., description="Globally unique identifier for the team"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Team (GET request): Returns the complete team record.
    """
    team = db.query(Team).filter(Team.gid == team_gid).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    team_data = {
        "gid": team.gid,
        "resource_type": team.resource_type,
        "name": team.name,
        "description": team.description
    }
    
    return TeamResponseWrapper(data=TeamResponse(**team_data))


@router.post("/organizations/{organization_gid}/teams", response_model=TeamResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_team(
    organization_gid: str = Path(..., description="Globally unique identifier for the organization"),
    team_data: TeamRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Team (POST request): Creates a new team in an organization.
    """
    organization = db.query(Workspace).filter(Workspace.gid == organization_gid).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    team = Team(
        gid=generate_gid(),
        resource_type="team",
        name=team_data.name or "New Team",
        organization_id=organization.id,
        description=team_data.description
    )
    
    db.add(team)
    db.commit()
    db.refresh(team)
    
    team_response = TeamResponse(
        gid=team.gid,
        resource_type=team.resource_type,
        name=team.name,
        description=team.description
    )
    
    return TeamResponseWrapper(data=team_response)


@router.put("/teams/{team_gid}", response_model=TeamResponseWrapper)
def update_team(
    team_gid: str = Path(..., description="Globally unique identifier for the team"),
    team_data: TeamRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Team (PUT request): An existing team can be updated.
    """
    team = db.query(Team).filter(Team.gid == team_gid).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    
    db.commit()
    db.refresh(team)
    
    team_response = TeamResponse(
        gid=team.gid,
        resource_type=team.resource_type,
        name=team.name,
        description=team.description
    )
    
    return TeamResponseWrapper(data=team_response)


@router.delete("/teams/{team_gid}", response_model=EmptyResponse)
def delete_team(
    team_gid: str = Path(..., description="Globally unique identifier for the team"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Team (DELETE request): A specific, existing team can be deleted.
    """
    team = db.query(Team).filter(Team.gid == team_gid).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    try:
        db.delete(team)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete team: it has dependent records (e.g., team memberships, projects). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting team: {str(e)}"
        )
    
    return EmptyResponse()

