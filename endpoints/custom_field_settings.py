from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.custom_field_setting import CustomFieldSetting
from models.project import Project
from models.portfolio import Portfolio
from schemas.custom_field_setting import (
    CustomFieldSettingResponse, CustomFieldSettingListResponse,
    CustomFieldSettingResponseWrapper
)

router = APIRouter()


@router.get("/projects/{project_gid}/custom_field_settings", response_model=CustomFieldSettingListResponse)
def get_custom_field_settings_for_project(
    project_gid: str = Path(..., description="Globally unique identifier for the project."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a project's custom field settings"""
    project = db.query(Project).filter(Project.gid == project_gid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    settings = db.query(CustomFieldSetting).filter(CustomFieldSetting.project_id == project.id).limit(limit).all()

    return CustomFieldSettingListResponse(
        data=[CustomFieldSettingResponse.from_orm(s) for s in settings]
    )


@router.get("/portfolios/{portfolio_gid}/custom_field_settings", response_model=CustomFieldSettingListResponse)
def get_custom_field_settings_for_portfolio(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a portfolio's custom field settings"""
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    settings = db.query(CustomFieldSetting).filter(CustomFieldSetting.portfolio_id == portfolio.id).limit(limit).all()

    return CustomFieldSettingListResponse(
        data=[CustomFieldSettingResponse.from_orm(s) for s in settings]
    )


@router.get("/custom_field_settings/{custom_field_setting_gid}", response_model=CustomFieldSettingResponseWrapper)
def get_custom_field_setting(
    custom_field_setting_gid: str = Path(..., description="Globally unique identifier for the custom field setting."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a custom field setting"""
    setting = db.query(CustomFieldSetting).filter(CustomFieldSetting.gid == custom_field_setting_gid).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Custom field setting not found")

    return CustomFieldSettingResponseWrapper(data=CustomFieldSettingResponse.from_orm(setting))

