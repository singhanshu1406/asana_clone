from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.custom_type import CustomType
from models.custom_type_status_option import CustomTypeStatusOption
from models.project import Project
from schemas.custom_type import (
    CustomTypeResponse, CustomTypeListResponse, CustomTypeResponseWrapper
)

router = APIRouter()


@router.get("/custom_types", response_model=CustomTypeListResponse)
def get_custom_types(
    project: str = Query(..., description="Globally unique identifier for the project, which is used as a filter when retrieving all custom types."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get all custom types associated with an object"""
    project_obj = db.query(Project).filter(Project.gid == project).first()
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    # In a real implementation, you'd filter custom types by project
    custom_types = db.query(CustomType).limit(limit).all()

    return CustomTypeListResponse(
        data=[CustomTypeResponse.from_orm(ct) for ct in custom_types]
    )


@router.get("/custom_types/{custom_type_gid}", response_model=CustomTypeResponseWrapper)
def get_custom_type(
    custom_type_gid: str = Path(..., description="Globally unique identifier for the custom type."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a custom type"""
    custom_type = db.query(CustomType).filter(CustomType.gid == custom_type_gid).first()
    if not custom_type:
        raise HTTPException(status_code=404, detail="Custom type not found")

    return CustomTypeResponseWrapper(data=CustomTypeResponse.from_orm(custom_type))

