from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.goal_membership import GoalMembership
from models.goal import Goal
from models.user import User
from models.team import Team
from schemas.goal_membership import (
    GoalMembershipResponse, GoalMembershipResponseWrapper,
    GoalMembershipListResponse, GoalMembershipCompact
)

router = APIRouter()


@router.get("/goals/{goal_gid}/goal_memberships", response_model=GoalMembershipListResponse)
def get_goal_memberships(
    goal_gid: str = Path(..., description="Globally unique identifier for the goal"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Goal Memberships (GET request): Returns compact goal membership records.
    """
    try:
        goal_id = int(goal_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal GID format"
        )
    
    query = db.query(GoalMembership).filter(GoalMembership.goal_id == goal_id)
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(GoalMembership.user_id == user_obj.id)
        else:
            try:
                user_id = int(user)
                query = query.filter(GoalMembership.user_id == user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user GID format"
                )
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        goal_obj = db.query(Goal).filter(Goal.id == membership.goal_id).first()
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
        
        access_level = "viewer"
        if membership.is_editor:
            access_level = "editor"
        elif membership.is_commenter:
            access_level = "commenter"
        
        membership_data = {
            "gid": membership.gid,
            "resource_type": "membership",
            "resource_subtype": "goal_membership",
            "member": member_obj,
            "parent": {
                "gid": goal_obj.gid if goal_obj else "",
                "resource_type": "goal",
                "name": goal_obj.name if goal_obj else "",
                "owner": None
            } if goal_obj else None,
            "access_level": access_level,
            "role": "editor" if membership.is_editor else "commenter" if membership.is_commenter else None,
            "goal": {
                "gid": goal_obj.gid if goal_obj else "",
                "resource_type": "goal",
                "name": goal_obj.name if goal_obj else "",
                "owner": None
            } if goal_obj else None
        }
        membership_compacts.append(GoalMembershipCompact(**membership_data))
    
    return GoalMembershipListResponse(data=membership_compacts)


@router.get("/goal_memberships/{goal_membership_gid}", response_model=GoalMembershipResponseWrapper)
def get_goal_membership(
    goal_membership_gid: str = Path(..., description="Globally unique identifier for the goal membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Goal Membership (GET request): Returns the complete goal membership record.
    """
    try:
        membership_id = int(goal_membership_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal membership GID format"
        )
    
    membership = db.query(GoalMembership).filter(GoalMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal membership not found"
        )
    
    goal_obj = db.query(Goal).filter(Goal.id == membership.goal_id).first()
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
    
    access_level = "viewer"
    if membership.is_editor:
        access_level = "editor"
    elif membership.is_commenter:
        access_level = "commenter"
    
    membership_data = {
        "gid": membership.gid,
        "resource_type": "membership",
        "resource_subtype": "goal_membership",
        "member": member_obj,
        "parent": {
            "gid": goal_obj.gid if goal_obj else "",
            "resource_type": "goal",
            "name": goal_obj.name if goal_obj else "",
            "owner": None
        } if goal_obj else None,
        "access_level": access_level,
        "role": "editor" if membership.is_editor else "commenter" if membership.is_commenter else None,
        "goal": {
            "gid": goal_obj.gid if goal_obj else "",
            "resource_type": "goal",
            "name": goal_obj.name if goal_obj else "",
            "owner": None
        } if goal_obj else None
    }
    
    return GoalMembershipResponseWrapper(data=GoalMembershipResponse(**membership_data))

