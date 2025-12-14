from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.access_request import AccessRequest
from models.user import User
from models.project import Project
from models.portfolio import Portfolio
from schemas.access_request import (
    AccessRequestResponse, AccessRequestResponseWrapper, AccessRequestListResponse,
    AccessRequestCreateRequest, EmptyResponse
)
from schemas.base import UserCompact, ProjectCompact, PortfolioCompact

router = APIRouter()


@router.get("/access_requests", response_model=AccessRequestListResponse)
def get_access_requests(
    target: str = Query(..., description="Globally unique identifier for the target object"),
    user: Optional[str] = Query(None, description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get access requests (GET request): Returns the pending access requests for a target object or a target object filtered by user.
    """
    try:
        target_id = int(target)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target GID format"
        )
    
    query = db.query(AccessRequest).filter(AccessRequest.target_id == target_id)
    
    if user:
        if user == "me":
            # In a real implementation, get current user from auth token
            pass
        else:
            try:
                user_id = int(user)
                query = query.filter(AccessRequest.requester_id == user_id)
            except ValueError:
                # Try to find by email
                user_obj = db.query(User).filter(User.email == user).first()
                if user_obj:
                    query = query.filter(AccessRequest.requester_id == user_obj.id)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid user identifier"
                    )
    
    access_requests = query.all()
    
    request_responses = []
    for req in access_requests:
        requester_obj = None
        if req.requester:
            requester_obj = UserCompact(
                gid=req.requester.gid,
                resource_type=req.requester.resource_type,
                name=req.requester.name,
                email=req.requester.email,
                photo=req.requester.photo
            )
        
        target_obj = None
        if req.target_type == "project":
            project = db.query(Project).filter(Project.id == req.target_id).first()
            if project:
                target_obj = {
                    "gid": project.gid,
                    "resource_type": project.resource_type,
                    "name": project.name
                }
        elif req.target_type == "portfolio":
            portfolio = db.query(Portfolio).filter(Portfolio.id == req.target_id).first()
            if portfolio:
                target_obj = {
                    "gid": portfolio.gid,
                    "resource_type": portfolio.resource_type,
                    "name": portfolio.name
                }
        
        request_data = {
            "gid": req.gid,
            "resource_type": req.resource_type,
            "approval_status": req.approval_status,
            "message": req.message,
            "requester": requester_obj,
            "target": target_obj
        }
        request_responses.append(AccessRequestResponse(**request_data))
    
    return AccessRequestListResponse(data=request_responses)


@router.post("/access_requests", response_model=AccessRequestResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_access_request(
    request_data: AccessRequestCreateRequest = Body(..., alias="data"),
    db: Session = Depends(get_db)
):
    """
    Create an access request (POST request): Submits a new access request for a private object.
    """
    try:
        target_id = int(request_data.target)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target GID format"
        )
    
    # Determine target type by checking if it exists in projects or portfolios
    project = db.query(Project).filter(Project.id == target_id).first()
    portfolio = db.query(Portfolio).filter(Portfolio.id == target_id).first()
    
    if not project and not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target object not found"
        )
    
    target_type = "project" if project else "portfolio"
    
    # In a real implementation, get current user from auth token
    # For now, use a default user
    requester = db.query(User).first()
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found in system"
        )
    
    new_request = AccessRequest(
        gid=generate_gid(),
        resource_type="access_request",
        message=request_data.message,
        approval_status="pending",
        requester_id=requester.id,
        target_id=target_id,
        target_type=target_type
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    requester_obj = UserCompact(
        gid=requester.gid,
        resource_type=requester.resource_type,
        name=requester.name,
        email=requester.email,
        photo=requester.photo
    )
    
    target_obj = None
    if target_type == "project" and project:
        target_obj = {
            "gid": project.gid,
            "resource_type": project.resource_type,
            "name": project.name
        }
    elif target_type == "portfolio" and portfolio:
        target_obj = {
            "gid": portfolio.gid,
            "resource_type": portfolio.resource_type,
            "name": portfolio.name
        }
    
    request_response = AccessRequestResponse(
        gid=new_request.gid,
        resource_type=new_request.resource_type,
        approval_status=new_request.approval_status,
        message=new_request.message,
        requester=requester_obj,
        target=target_obj
    )
    
    return AccessRequestResponseWrapper(data=request_response)


@router.post("/access_requests/{access_request_gid}/approve", response_model=EmptyResponse)
def approve_access_request(
    access_request_gid: str = Path(..., description="Globally unique identifier for the access request"),
    db: Session = Depends(get_db)
):
    """
    Approve an access request (POST request): Approves an access request for a target object.
    """
    try:
        request_id = int(access_request_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid access request GID format"
        )
    
    access_request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )
    
    access_request.approval_status = "approved"
    db.commit()
    
    return EmptyResponse(data={})


@router.post("/access_requests/{access_request_gid}/reject", response_model=EmptyResponse)
def reject_access_request(
    access_request_gid: str = Path(..., description="Globally unique identifier for the access request"),
    db: Session = Depends(get_db)
):
    """
    Reject an access request (POST request): Rejects an access request for a target object.
    """
    try:
        request_id = int(access_request_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid access request GID format"
        )
    
    access_request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )
    
    access_request.approval_status = "denied"
    db.commit()
    
    return EmptyResponse(data={})

