from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.custom_field_membership import CustomFieldMembership
from models.custom_field import CustomField
from models.user import User
from models.team import Team
from schemas.custom_field_membership import (
    CustomFieldMembershipResponse, CustomFieldMembershipResponseWrapper,
    CustomFieldMembershipListResponse, CustomFieldMembershipCompact
)

router = APIRouter()


@router.get("/custom_fields/{custom_field_gid}/custom_field_memberships", response_model=CustomFieldMembershipListResponse)
def get_custom_field_memberships(
    custom_field_gid: str = Path(..., description="Globally unique identifier for the custom field"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Custom Field Memberships (GET request): Returns compact custom field membership records.
    """
    try:
        custom_field_id = int(custom_field_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid custom field GID format"
        )
    
    query = db.query(CustomFieldMembership).filter(CustomFieldMembership.custom_field_id == custom_field_id)
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(CustomFieldMembership.user_id == user_obj.id)
        else:
            try:
                user_id = int(user)
                query = query.filter(CustomFieldMembership.user_id == user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user GID format"
                )
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        custom_field_obj = db.query(CustomField).filter(CustomField.id == membership.custom_field_id).first()
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
        
        membership_data = {
            "gid": membership.gid,
            "resource_type": membership.resource_type,
            "resource_subtype": "custom_field_membership",
            "parent": {
                "gid": custom_field_obj.gid if custom_field_obj else "",
                "resource_type": "custom_field",
                "name": custom_field_obj.name if custom_field_obj else "",
                "type": None
            } if custom_field_obj else None,
            "member": member_obj,
            "access_level": "user"  # Default
        }
        membership_compacts.append(CustomFieldMembershipCompact(**membership_data))
    
    return CustomFieldMembershipListResponse(data=membership_compacts)


@router.get("/custom_field_memberships/{custom_field_membership_gid}", response_model=CustomFieldMembershipResponseWrapper)
def get_custom_field_membership(
    custom_field_membership_gid: str = Path(..., description="Globally unique identifier for the custom field membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Custom Field Membership (GET request): Returns the complete custom field membership record.
    """
    try:
        membership_id = int(custom_field_membership_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid custom field membership GID format"
        )
    
    membership = db.query(CustomFieldMembership).filter(CustomFieldMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field membership not found"
        )
    
    custom_field_obj = db.query(CustomField).filter(CustomField.id == membership.custom_field_id).first()
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
    
    membership_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "resource_subtype": "custom_field_membership",
        "parent": {
            "gid": custom_field_obj.gid if custom_field_obj else "",
            "resource_type": "custom_field",
            "name": custom_field_obj.name if custom_field_obj else "",
            "type": None
        } if custom_field_obj else None,
        "member": member_obj,
        "access_level": "user"  # Default
    }
    
    return CustomFieldMembershipResponseWrapper(data=CustomFieldMembershipResponse(**membership_data))

