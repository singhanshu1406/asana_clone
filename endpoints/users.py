from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.user import User
from schemas.user import (
    UserResponse, UserResponseWrapper, UserListResponse,
    UserCompact, UserRequest, UserUpdateRequest
)

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
def get_users(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    team: Optional[str] = Query(None, description="The team to filter users on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Users (GET request): Returns compact user records.
    """
    query = db.query(User)
    
    users = query.limit(limit).all()
    
    user_compacts = []
    for user in users:
        user_data = {
            "gid": user.gid,
            "resource_type": user.resource_type,
            "name": user.name or "",
            "email": user.email
        }
        user_compacts.append(UserCompact(**user_data))
    
    return UserListResponse(data=user_compacts)


@router.get("/users/{user_gid}", response_model=UserResponseWrapper)
def get_user(
    user_gid: str = Path(..., description="Globally unique identifier for the user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a User (GET request): Returns the complete user record.
    """
    # Handle "me" special case
    if user_gid.lower() == "me":
        # Would need current user context - for now use default
        user = db.query(User).first()
    else:
        # Try GID lookup first
        user = db.query(User).filter(User.gid == user_gid).first()
        if not user:
            # Try email lookup as fallback
            user = db.query(User).filter(User.email == user_gid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = {
        "gid": user.gid,
        "resource_type": user.resource_type,
        "name": user.name or "",
        "email": user.email,
        "photo": None
    }
    
    return UserResponseWrapper(data=UserResponse(**user_data))


@router.get("/users/me", response_model=UserResponseWrapper)
def get_current_user(
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get Current User (GET request): Returns the full user record for the authenticated user.
    """
    # Would need current user context - for now use first user
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = {
        "gid": user.gid,
        "resource_type": user.resource_type,
        "name": user.name or "",
        "email": user.email,
        "photo": None
    }
    
    return UserResponseWrapper(data=UserResponse(**user_data))

