from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.time_period import TimePeriod
from schemas.time_period import (
    TimePeriodResponse, TimePeriodResponseWrapper, TimePeriodListResponse,
    TimePeriodCompact
)

router = APIRouter()


@router.get("/time_periods", response_model=TimePeriodListResponse)
def get_time_periods(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Time Periods (GET request): Returns compact time period records.
    """
    time_periods = db.query(TimePeriod).limit(limit).all()
    
    period_compacts = []
    for period in time_periods:
        period_data = {
            "gid": period.gid,
            "resource_type": period.resource_type,
            "display_name": period.display_name,
            "end_on": str(period.end_on) if period.end_on else None,
            "start_on": str(period.start_on) if period.start_on else None,
            "period": period.period
        }
        period_compacts.append(TimePeriodCompact(**period_data))
    
    return TimePeriodListResponse(data=period_compacts)


@router.get("/time_periods/{time_period_gid}", response_model=TimePeriodResponseWrapper)
def get_time_period(
    time_period_gid: str = Path(..., description="Globally unique identifier for the time period"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Time Period (GET request): Returns the complete time period record.
    """
    try:
        period_id = int(time_period_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time period GID format"
        )
    
    time_period = db.query(TimePeriod).filter(TimePeriod.id == period_id).first()
    if not time_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time period not found"
        )
    
    period_data = {
        "gid": time_period.gid,
        "resource_type": time_period.resource_type,
        "display_name": time_period.display_name,
        "end_on": str(time_period.end_on) if time_period.end_on else None,
        "start_on": str(time_period.start_on) if time_period.start_on else None,
        "period": time_period.period,
        "parent": None
    }
    
    return TimePeriodResponseWrapper(data=TimePeriodResponse(**period_data))

