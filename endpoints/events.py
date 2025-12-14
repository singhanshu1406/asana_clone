from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.event import Event
from models.user import User
from schemas.event import EventResponse, EventListResponse

router = APIRouter()


@router.get("/events", response_model=EventListResponse)
def get_events(
    resource: Optional[str] = Query(None, description="Globally unique identifier for the resource"),
    sync: Optional[str] = Query(None, description="A sync token received from the last request"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get Events (GET request): Returns the full record for all events that have occurred 
    since the sync token was created.
    """
    query = db.query(Event)
    
    if resource:
        try:
            resource_id = int(resource)
            query = query.filter(Event.resource_id == resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource GID format"
            )
    
    # Order by created_at descending
    events = query.order_by(Event.created_at.desc()).limit(100).all()
    
    # Convert to response format
    event_responses = []
    for event in events:
        user_obj = None
        if event.user_id:
            user = db.query(User).filter(User.id == event.user_id).first()
            if user:
                user_obj = {
                    "gid": user.gid,
                    "resource_type": "user",
                    "name": user.name or "",
                    "email": user.email
                }
        
        event_data = {
            "gid": event.gid,
            "resource_type": event.resource_type,
            "action": event.action or "changed",
            "created_at": event.created_at,
            "user": user_obj,
            "resource": {
                "gid": event.gid,
                "resource_type": event.resource_type,
                "name": ""
            },
            "parent": None,
            "change": event.change if event.change else None
        }
        event_responses.append(EventResponse(**event_data))
    
    return EventListResponse(data=event_responses)

