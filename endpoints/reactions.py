from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.reaction import Reaction
from schemas.reaction import ReactionResponse, ReactionListResponse

router = APIRouter()


@router.get("/status_updates/{status_update_gid}/reactions", response_model=ReactionListResponse)
def get_reactions_for_status_update(
    status_update_gid: str = Path(..., description="Globally unique identifier for the status update."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get reactions for a status update"""
    # In a real implementation, you'd filter by status_update_gid
    reactions = db.query(Reaction).filter(Reaction.target_type == "status_update").limit(limit).all()

    return ReactionListResponse(
        data=[ReactionResponse.from_orm(r) for r in reactions]
    )

