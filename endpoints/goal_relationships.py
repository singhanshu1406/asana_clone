from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.goal_relationship import GoalRelationship
from models.goal import Goal
from schemas.goal_relationship import (
    GoalRelationshipResponse, GoalRelationshipResponseWrapper,
    GoalRelationshipListResponse, GoalRelationshipCompact
)

router = APIRouter()


@router.get("/goals/{goal_gid}/goal_relationships", response_model=GoalRelationshipListResponse)
def get_goal_relationships(
    goal_gid: str = Path(..., description="Globally unique identifier for the goal"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get Goal Relationships (GET request): Returns compact goal relationship records.
    """
    try:
        goal_id = int(goal_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal GID format"
        )
    
    # Get relationships where this goal is the supported goal
    relationships = db.query(GoalRelationship).filter(
        GoalRelationship.supported_goal_id == goal_id
    ).all()
    
    relationship_compacts = []
    for rel in relationships:
        rel_data = {
            "gid": rel.gid,
            "resource_type": rel.resource_type,
            "resource_subtype": rel.resource_subtype,
            "contribution_weight": float(rel.contribution_weight) if rel.contribution_weight else None,
            "supporting_resource": None
        }
        relationship_compacts.append(GoalRelationshipCompact(**rel_data))
    
    return GoalRelationshipListResponse(data=relationship_compacts)


@router.get("/goal_relationships/{goal_relationship_gid}", response_model=GoalRelationshipResponseWrapper)
def get_goal_relationship(
    goal_relationship_gid: str = Path(..., description="Globally unique identifier for the goal relationship"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Goal Relationship (GET request): Returns the complete goal relationship record.
    """
    try:
        rel_id = int(goal_relationship_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal relationship GID format"
        )
    
    relationship = db.query(GoalRelationship).filter(GoalRelationship.id == rel_id).first()
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal relationship not found"
        )
    
    rel_data = {
        "gid": relationship.gid,
        "resource_type": relationship.resource_type,
        "resource_subtype": relationship.resource_subtype,
        "contribution_weight": float(relationship.contribution_weight) if relationship.contribution_weight else None,
        "supported_goal": None,
        "supporting_resource": None
    }
    
    return GoalRelationshipResponseWrapper(data=GoalRelationshipResponse(**rel_data))

