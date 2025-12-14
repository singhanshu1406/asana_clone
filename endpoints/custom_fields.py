from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from models.custom_field import CustomField
from models.enum_option import EnumOption
from models.workspace import Workspace
from models.user import User
from schemas.custom_field import (
    CustomFieldResponse, CustomFieldListResponse, CustomFieldResponseWrapper,
    CustomFieldRequest, CustomFieldUpdateRequest,
    EnumOptionResponse, EnumOptionListResponse, EnumOptionResponseWrapper,
    EnumOptionRequest
)
from schemas.project_membership import EmptyResponse
from utils import generate_gid

router = APIRouter()


@router.get("/workspaces/{workspace_gid}/custom_fields", response_model=CustomFieldListResponse)
def get_custom_fields_for_workspace(
    workspace_gid: str = Path(..., description="Globally unique identifier for the workspace or organization."),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a workspace's custom fields"""
    workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    query = db.query(CustomField).filter(CustomField.workspace_id == workspace.id)
    custom_fields = query.limit(limit).all()

    return CustomFieldListResponse(
        data=[CustomFieldResponse.from_orm(cf) for cf in custom_fields]
    )


@router.post("/workspaces/{workspace_gid}/custom_fields", response_model=CustomFieldResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_custom_field(
    workspace_gid: str = Path(..., description="Globally unique identifier for the workspace or organization."),
    custom_field_data: CustomFieldRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create a custom field"""
    workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get or create user (assuming "me" or first user)
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    custom_field = CustomField(
        gid=generate_gid(),
        name=custom_field_data.name,
        type=custom_field_data.type,
        description=custom_field_data.description,
        enabled=custom_field_data.enabled,
        workspace_id=workspace.id,
        created_by_id=user.id,
        precision=custom_field_data.precision,
        format=custom_field_data.format,
        currency_code=custom_field_data.currency_code,
        custom_label=custom_field_data.custom_label,
        custom_label_position=custom_field_data.custom_label_position,
        is_global_to_workspace=custom_field_data.is_global_to_workspace,
        has_notifications_enabled=custom_field_data.has_notifications_enabled,
        is_value_read_only=custom_field_data.is_value_read_only,
        default_access_level=custom_field_data.default_access_level,
        privacy_setting=custom_field_data.privacy_setting
    )

    db.add(custom_field)
    db.commit()
    db.refresh(custom_field)

    return CustomFieldResponseWrapper(data=CustomFieldResponse.from_orm(custom_field))


@router.get("/custom_fields/{custom_field_gid}", response_model=CustomFieldResponseWrapper)
def get_custom_field(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get a custom field"""
    custom_field = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
    if not custom_field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    return CustomFieldResponseWrapper(data=CustomFieldResponse.from_orm(custom_field))


@router.put("/custom_fields/{custom_field_gid}", response_model=CustomFieldResponseWrapper)
def update_custom_field(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field."),
    custom_field_data: CustomFieldUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Update a custom field"""
    custom_field = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
    if not custom_field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    if custom_field_data.name is not None:
        custom_field.name = custom_field_data.name
    if custom_field_data.description is not None:
        custom_field.description = custom_field_data.description
    if custom_field_data.enabled is not None:
        custom_field.enabled = custom_field_data.enabled
    if custom_field_data.precision is not None:
        custom_field.precision = custom_field_data.precision
    if custom_field_data.format is not None:
        custom_field.format = custom_field_data.format
    if custom_field_data.currency_code is not None:
        custom_field.currency_code = custom_field_data.currency_code
    if custom_field_data.custom_label is not None:
        custom_field.custom_label = custom_field_data.custom_label
    if custom_field_data.custom_label_position is not None:
        custom_field.custom_label_position = custom_field_data.custom_label_position
    if custom_field_data.is_global_to_workspace is not None:
        custom_field.is_global_to_workspace = custom_field_data.is_global_to_workspace
    if custom_field_data.has_notifications_enabled is not None:
        custom_field.has_notifications_enabled = custom_field_data.has_notifications_enabled
    if custom_field_data.is_value_read_only is not None:
        custom_field.is_value_read_only = custom_field_data.is_value_read_only
    if custom_field_data.default_access_level is not None:
        custom_field.default_access_level = custom_field_data.default_access_level
    if custom_field_data.privacy_setting is not None:
        custom_field.privacy_setting = custom_field_data.privacy_setting

    db.commit()
    db.refresh(custom_field)

    return CustomFieldResponseWrapper(data=CustomFieldResponse.from_orm(custom_field))


@router.delete("/custom_fields/{custom_field_gid}", response_model=EmptyResponse)
def delete_custom_field(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Delete a custom field"""
    custom_field = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
    if not custom_field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    try:
        db.delete(custom_field)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete custom field: it has dependent records (e.g., enum options, custom field settings). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting custom field: {str(e)}"
        )

    return EmptyResponse()


@router.post("/custom_fields/{custom_field_gid}/enum_options", response_model=EnumOptionResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_enum_option_for_custom_field(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field."),
    enum_option_data: EnumOptionRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Create an enum option"""
    custom_field = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
    if not custom_field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    enum_option = EnumOption(
        gid=generate_gid(),
        name=enum_option_data.name,
        color=enum_option_data.color,
        enabled=enum_option_data.enabled if enum_option_data.enabled is not None else True,
        custom_field_id=custom_field.id
    )

    db.add(enum_option)
    db.commit()
    db.refresh(enum_option)

    return EnumOptionResponseWrapper(data=EnumOptionResponse.from_orm(enum_option))


@router.post("/custom_fields/{custom_field_gid}/enum_options/insert", response_model=EnumOptionListResponse)
def insert_enum_option_for_custom_field(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field."),
    enum_option_data: dict = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Reorder a custom field's enum"""
    custom_field = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
    if not custom_field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    # This is a simplified implementation - in reality, you'd reorder enum options
    enum_options = db.query(EnumOption).filter(EnumOption.custom_field_id == custom_field.id).all()

    return EnumOptionListResponse(
        data=[EnumOptionResponse.from_orm(eo) for eo in enum_options]
    )


@router.put("/enum_options/{enum_option_gid}", response_model=EnumOptionResponseWrapper)
def update_enum_option(
    enum_option_gid: str = Path(..., description="Globally unique identifier for the enum option."),
    enum_option_data: EnumOptionRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Update an enum option"""
    enum_option = db.query(EnumOption).filter(EnumOption.gid == enum_option_gid).first()
    if not enum_option:
        raise HTTPException(status_code=404, detail="Enum option not found")

    if enum_option_data.name is not None:
        enum_option.name = enum_option_data.name
    if enum_option_data.color is not None:
        enum_option.color = enum_option_data.color
    if enum_option_data.enabled is not None:
        enum_option.enabled = enum_option_data.enabled

    db.commit()
    db.refresh(enum_option)

    return EnumOptionResponseWrapper(data=EnumOptionResponse.from_orm(enum_option))


@router.delete("/enum_options/{enum_option_gid}", response_model=EmptyResponse)
def delete_enum_option(
    enum_option_gid: str = Path(..., description="Globally unique identifier for the enum option."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Delete an enum option"""
    enum_option = db.query(EnumOption).filter(EnumOption.gid == enum_option_gid).first()
    if not enum_option:
        raise HTTPException(status_code=404, detail="Enum option not found")

    try:
        db.delete(enum_option)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete enum option: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting enum option: {str(e)}"
        )

    return EmptyResponse()

