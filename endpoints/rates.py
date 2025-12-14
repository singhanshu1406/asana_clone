from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from models.rate import Rate
from models.project import Project
from models.user import User
from schemas.rate import (
    RateResponse, RateListResponse, RateResponseWrapper, RateRequest
)
from schemas.project_membership import EmptyResponse
from utils import generate_gid

router = APIRouter()


@router.get("/rates", response_model=RateListResponse)
def get_rates(
    parent: str = Query(..., description="Globally unique identifier for the rate's parent object. This currently can only be a `project`."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get all rates"""
    project = db.query(Project).filter(Project.gid == parent).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rates = db.query(Rate).filter(Rate.parent_id == project.id).limit(limit).all()

    return RateListResponse(
        data=[RateResponse.from_orm(r) for r in rates]
    )


@router.post("/rates", response_model=RateResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_rate(
    rate_data: RateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create a rate"""
    project = db.query(Project).filter(Project.gid == rate_data.parent).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    resource_id = None
    if rate_data.resource:
        user = db.query(User).filter(User.gid == rate_data.resource).first()
        if user:
            resource_id = user.id

    rate = Rate(
        gid=generate_gid(),
        rate=rate_data.rate,
        currency_code=rate_data.currency_code,
        parent_id=project.id,
        resource_id=resource_id,
        resource_type_field="user" if resource_id else None
    )

    db.add(rate)
    db.commit()
    db.refresh(rate)

    return RateResponseWrapper(data=RateResponse.from_orm(rate))


@router.get("/rates/{rate_gid}", response_model=RateResponseWrapper)
def get_rate(
    rate_gid: str = Path(..., description="Globally unique identifier for the rate."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a rate"""
    rate = db.query(Rate).filter(Rate.gid == rate_gid).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    return RateResponseWrapper(data=RateResponse.from_orm(rate))


@router.put("/rates/{rate_gid}", response_model=RateResponseWrapper)
def update_rate(
    rate_gid: str = Path(..., description="Globally unique identifier for the rate."),
    rate_data: RateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Update a rate"""
    rate = db.query(Rate).filter(Rate.gid == rate_gid).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    if rate_data.rate is not None:
        rate.rate = rate_data.rate
    if rate_data.currency_code is not None:
        rate.currency_code = rate_data.currency_code

    db.commit()
    db.refresh(rate)

    return RateResponseWrapper(data=RateResponse.from_orm(rate))


@router.delete("/rates/{rate_gid}", response_model=EmptyResponse)
def delete_rate(
    rate_gid: str = Path(..., description="Globally unique identifier for the rate."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Delete a rate"""
    rate = db.query(Rate).filter(Rate.gid == rate_gid).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    try:
        db.delete(rate)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete rate: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rate: {str(e)}"
        )

    return EmptyResponse()

