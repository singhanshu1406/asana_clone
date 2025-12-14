from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.goal import Goal
from models.user import User
from models.team import Team
from models.workspace import Workspace
from models.time_period import TimePeriod
from models.status_update import StatusUpdate
from schemas.goal import (
    GoalResponse, GoalResponseWrapper, GoalListResponse, GoalCompact,
    GoalRequest, GoalUpdateRequest, GoalAddSubgoalRequest, GoalRemoveSubgoalRequest,
    GoalAddSupportingWorkRequest, GoalAddSupportingRelationshipRequest,
    GoalRemoveSupportingRelationshipRequest, EmptyResponse
)

router = APIRouter()


@router.get("/goals", response_model=GoalListResponse)
def get_goals(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    team: Optional[str] = Query(None, description="The team to filter goals on"),
    time_periods: Optional[str] = Query(None, description="Comma-separated list of time period GIDs"),
    is_workspace_level: Optional[bool] = Query(None, description="Filter to workspace-level goals"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Goals (GET request): Returns compact goal records.
    """
    query = db.query(Goal)
    
    if workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if workspace_obj:
            query = query.filter(Goal.workspace_id == workspace_obj.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
    
    if team:
        team_obj = db.query(Team).filter(Team.gid == team).first()
        if team_obj:
            query = query.filter(Goal.team_id == team_obj.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
    
    if is_workspace_level is not None:
        query = query.filter(Goal.is_workspace_level == is_workspace_level)
    
    goals = query.limit(limit).all()
    
    goal_compacts = []
    for goal in goals:
        owner_obj = None
        if goal.owner_id:
            owner = db.query(User).filter(User.id == goal.owner_id).first()
            if owner:
                owner_obj = {
                    "gid": owner.gid,
                    "resource_type": "user",
                    "name": owner.name or "",
                    "email": owner.email
                }
        
        goal_data = {
            "gid": goal.gid,
            "resource_type": goal.resource_type,
            "name": goal.name,
            "owner": owner_obj
        }
        goal_compacts.append(GoalCompact(**goal_data))
    
    return GoalListResponse(data=goal_compacts)


@router.get("/goals/{goal_gid}", response_model=GoalResponseWrapper)
def get_goal(
    goal_gid: str = Path(..., description="Globally unique identifier for the goal"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Goal (GET request): Returns the complete goal record for a single goal.
    """
    goal = db.query(Goal).filter(Goal.gid == goal_gid).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Build response
    goal_data = {
        "gid": goal.gid,
        "resource_type": goal.resource_type,
        "name": goal.name,
        "html_notes": goal.html_notes,
        "notes": goal.notes,
        "due_on": goal.due_on,
        "start_on": goal.start_on,
        "is_workspace_level": goal.is_workspace_level,
        "liked": goal.liked,
        "status": goal.status,
        "num_likes": goal.num_likes
    }
    
    return GoalResponseWrapper(data=GoalResponse(**goal_data))


@router.post("/goals", response_model=GoalResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Goal (POST request): Creates a new goal in a workspace or team.
    """
    # Create goal
    goal = Goal(
        gid=generate_gid(),
        resource_type="goal",
        name=goal_data.name or "New Goal"
    )
    
    if goal_data.workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == goal_data.workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        goal.workspace_id = workspace_obj.id
    
    if goal_data.team:
        team_obj = db.query(Team).filter(Team.gid == goal_data.team).first()
        if not team_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        goal.team_id = team_obj.id
    
    if goal_data.owner:
        owner_obj = db.query(User).filter(User.gid == goal_data.owner).first()
        if not owner_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
        goal.owner_id = owner_obj.id
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    goal_response = GoalResponse(
        gid=goal.gid,
        resource_type=goal.resource_type,
        name=goal.name,
        html_notes=goal.html_notes,
        notes=goal.notes,
        due_on=goal.due_on,
        start_on=goal.start_on,
        is_workspace_level=goal.is_workspace_level,
        liked=goal.liked,
        status=goal.status
    )
    
    return GoalResponseWrapper(data=goal_response)


@router.put("/goals/{goal_gid}", response_model=GoalResponseWrapper)
def update_goal(
    goal_gid: str = Path(..., description="Globally unique identifier for the goal"),
    goal_data: GoalUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Goal (PUT request): An existing goal can be updated by making a PUT request.
    """
    goal = db.query(Goal).filter(Goal.gid == goal_gid).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Update fields
    if goal_data.name is not None:
        goal.name = goal_data.name
    if goal_data.notes is not None:
        goal.notes = goal_data.notes
    if goal_data.html_notes is not None:
        goal.html_notes = goal_data.html_notes
    if goal_data.due_on is not None:
        goal.due_on = goal_data.due_on
    if goal_data.start_on is not None:
        goal.start_on = goal_data.start_on
    if goal_data.status is not None:
        goal.status = goal_data.status
    
    db.commit()
    db.refresh(goal)
    
    goal_response = GoalResponse(
        gid=goal.gid,
        resource_type=goal.resource_type,
        name=goal.name,
        html_notes=goal.html_notes,
        notes=goal.notes,
        due_on=goal.due_on,
        start_on=goal.start_on,
        is_workspace_level=goal.is_workspace_level,
        liked=goal.liked,
        status=goal.status
    )
    
    return GoalResponseWrapper(data=goal_response)


@router.delete("/goals/{goal_gid}", response_model=EmptyResponse)
def delete_goal(
    goal_gid: str = Path(..., description="Globally unique identifier for the goal"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Goal (DELETE request): A specific, existing goal can be deleted.
    """
    goal = db.query(Goal).filter(Goal.gid == goal_gid).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    try:
        db.delete(goal)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete goal: it has dependent records (e.g., goal memberships, goal relationships). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}"
        )
    
    return EmptyResponse()

