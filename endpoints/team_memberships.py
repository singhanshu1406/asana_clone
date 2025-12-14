from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.team_membership import TeamMembership
from models.team import Team
from models.user import User
from schemas.team_membership import (
    TeamMembershipResponse, TeamMembershipResponseWrapper,
    TeamMembershipListResponse, TeamMembershipCompact
)

router = APIRouter()


@router.get("/teams/{team_gid}/team_memberships", response_model=TeamMembershipListResponse)
def get_team_memberships(
    team_gid: str = Path(..., description="Globally unique identifier for the team"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Team Memberships (GET request): Returns compact team membership records.
    """
    try:
        team_id = int(team_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team GID format"
        )
    
    query = db.query(TeamMembership).filter(TeamMembership.team_id == team_id)
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(TeamMembership.user_id == user_obj.id)
        else:
            try:
                user_id = int(user)
                query = query.filter(TeamMembership.user_id == user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user GID format"
                )
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        team_obj = db.query(Team).filter(Team.id == membership.team_id).first()
        user_obj = db.query(User).filter(User.id == membership.user_id).first() if membership.user_id else None
        
        membership_data = {
            "gid": membership.gid,
            "resource_type": membership.resource_type,
            "user": {
                "gid": user_obj.gid,
                "resource_type": "user",
                "name": user_obj.name or "",
                "email": user_obj.email
            } if user_obj else None,
            "team": {
                "gid": team_obj.gid if team_obj else "",
                "resource_type": "team",
                "name": team_obj.name if team_obj else ""
            } if team_obj else None,
            "is_guest": membership.is_guest,
            "is_limited_access": False,
            "is_admin": membership.is_admin
        }
        membership_compacts.append(TeamMembershipCompact(**membership_data))
    
    return TeamMembershipListResponse(data=membership_compacts)


@router.get("/team_memberships/{team_membership_gid}", response_model=TeamMembershipResponseWrapper)
def get_team_membership(
    team_membership_gid: str = Path(..., description="Globally unique identifier for the team membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Team Membership (GET request): Returns the complete team membership record.
    """
    try:
        membership_id = int(team_membership_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team membership GID format"
        )
    
    membership = db.query(TeamMembership).filter(TeamMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team membership not found"
        )
    
    team_obj = db.query(Team).filter(Team.id == membership.team_id).first()
    user_obj = db.query(User).filter(User.id == membership.user_id).first() if membership.user_id else None
    
    membership_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "user": {
            "gid": user_obj.gid,
            "resource_type": "user",
            "name": user_obj.name or "",
            "email": user_obj.email
        } if user_obj else None,
        "team": {
            "gid": team_obj.gid if team_obj else "",
            "resource_type": "team",
            "name": team_obj.name if team_obj else ""
        } if team_obj else None,
        "is_guest": membership.is_guest,
        "is_limited_access": False,
        "is_admin": membership.is_admin
    }
    
    return TeamMembershipResponseWrapper(data=TeamMembershipResponse(**membership_data))

