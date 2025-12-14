from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.allocation import Allocation
from models.user import User
from models.project import Project
from schemas.allocation import (
    AllocationResponse, AllocationResponseWrapper, AllocationListResponse,
    AllocationRequest, Effort, EmptyResponse
)
from schemas.base import UserCompact, ProjectCompact

router = APIRouter()


@router.get("/allocations", response_model=AllocationListResponse)
def get_allocations(
    parent: Optional[str] = Query(None, description="Globally unique identifier for the project to filter allocations by"),
    assignee: Optional[str] = Query(None, description="Globally unique identifier for the user or placeholder the allocation is assigned to"),
    workspace: Optional[str] = Query(None, description="Globally unique identifier for the workspace"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get multiple allocations (GET request): Returns a list of allocations filtered to a specific project, user or placeholder.
    """
    query = db.query(Allocation)
    
    if parent:
        try:
            parent_id = int(parent)
            query = query.filter(Allocation.parent_id == parent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent GID format"
            )
    
    if assignee:
        try:
            assignee_id = int(assignee)
            query = query.filter(Allocation.assignee_id == assignee_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee GID format"
            )
    
    allocations = query.limit(limit).all()
    
    allocation_responses = []
    for alloc in allocations:
        assignee_obj = None
        if alloc.assignee:
            assignee_obj = UserCompact(
                gid=alloc.assignee.gid,
                resource_type=alloc.assignee.resource_type,
                name=alloc.assignee.name,
                email=alloc.assignee.email,
                photo=alloc.assignee.photo
            )
        
        parent_obj = None
        if alloc.parent:
            parent_obj = ProjectCompact(
                gid=alloc.parent.gid,
                resource_type=alloc.parent.resource_type,
                name=alloc.parent.name,
                resource_subtype=None
            )
        
        created_by_obj = None
        if alloc.created_by:
            created_by_obj = UserCompact(
                gid=alloc.created_by.gid,
                resource_type=alloc.created_by.resource_type,
                name=alloc.created_by.name,
                email=alloc.created_by.email,
                photo=alloc.created_by.photo
            )
        
        effort_obj = None
        if alloc.effort_type or alloc.effort_value:
            effort_obj = Effort(
                type=alloc.effort_type,
                value=float(alloc.effort_value) if alloc.effort_value else None
            )
        
        allocation_data = {
            "gid": alloc.gid,
            "resource_type": alloc.resource_type,
            "resource_subtype": alloc.resource_subtype,
            "start_date": alloc.start_date,
            "end_date": alloc.end_date,
            "assignee": assignee_obj,
            "parent": parent_obj,
            "created_by": created_by_obj,
            "effort": effort_obj
        }
        allocation_responses.append(AllocationResponse(**allocation_data))
    
    return AllocationListResponse(data=allocation_responses)


@router.get("/allocations/{allocation_gid}", response_model=AllocationResponseWrapper)
def get_allocation(
    allocation_gid: str = Path(..., description="Globally unique identifier for the allocation"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get an allocation (GET request): Returns the complete allocation record for a single allocation.
    """
    try:
        allocation_id = int(allocation_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid allocation GID format"
        )
    
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found"
        )
    
    assignee_obj = None
    if allocation.assignee:
        assignee_obj = UserCompact(
            gid=allocation.assignee.gid,
            resource_type=allocation.assignee.resource_type,
            name=allocation.assignee.name,
            email=allocation.assignee.email,
            photo=allocation.assignee.photo
        )
    
    parent_obj = None
    if allocation.parent:
        parent_obj = ProjectCompact(
            gid=allocation.parent.gid,
            resource_type=allocation.parent.resource_type,
            name=allocation.parent.name,
            resource_subtype=None
        )
    
    created_by_obj = None
    if allocation.created_by:
        created_by_obj = UserCompact(
            gid=allocation.created_by.gid,
            resource_type=allocation.created_by.resource_type,
            name=allocation.created_by.name,
            email=allocation.created_by.email,
            photo=allocation.created_by.photo
        )
    
    effort_obj = None
    if allocation.effort_type or allocation.effort_value:
        effort_obj = Effort(
            type=allocation.effort_type,
            value=float(allocation.effort_value) if allocation.effort_value else None
        )
    
    allocation_data = {
        "gid": allocation.gid,
        "resource_type": allocation.resource_type,
        "resource_subtype": allocation.resource_subtype,
        "start_date": allocation.start_date,
        "end_date": allocation.end_date,
        "assignee": assignee_obj,
        "parent": parent_obj,
        "created_by": created_by_obj,
        "effort": effort_obj
    }
    
    return AllocationResponseWrapper(data=AllocationResponse(**allocation_data))


@router.post("/allocations", response_model=AllocationResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_allocation(
    allocation_data: AllocationRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create an allocation (POST request): Creates a new allocation.
    """
    if not allocation_data.assignee or not allocation_data.parent or not allocation_data.start_date or not allocation_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assignee, parent, start_date, and end_date are required"
        )
    
    try:
        assignee_id = int(allocation_data.assignee)
        parent_id = int(allocation_data.parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assignee or parent GID format"
        )
    
    # Verify assignee and parent exist
    assignee = db.query(User).filter(User.id == assignee_id).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found"
        )
    
    parent = db.query(Project).filter(Project.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent project not found"
        )
    
    # Get current user (in real implementation, from auth token)
    created_by = db.query(User).first()
    if not created_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found in system"
        )
    
    new_allocation = Allocation(
        gid=generate_gid(),
        resource_type="allocation",
        resource_subtype=allocation_data.resource_subtype,
        start_date=allocation_data.start_date,
        end_date=allocation_data.end_date,
        effort_type=allocation_data.effort_type,
        effort_value=allocation_data.effort_value,
        assignee_id=assignee_id,
        parent_id=parent_id,
        created_by_id=created_by.id
    )
    
    db.add(new_allocation)
    db.commit()
    db.refresh(new_allocation)
    
    assignee_obj = UserCompact(
        gid=assignee.gid,
        resource_type=assignee.resource_type,
        name=assignee.name,
        email=assignee.email,
        photo=assignee.photo
    )
    
    parent_obj = ProjectCompact(
        gid=parent.gid,
        resource_type=parent.resource_type,
        name=parent.name,
        resource_subtype=None
    )
    
    created_by_obj = UserCompact(
        gid=created_by.gid,
        resource_type=created_by.resource_type,
        name=created_by.name,
        email=created_by.email,
        photo=created_by.photo
    )
    
    effort_obj = None
    if new_allocation.effort_type or new_allocation.effort_value:
        effort_obj = Effort(
            type=new_allocation.effort_type,
            value=float(new_allocation.effort_value) if new_allocation.effort_value else None
        )
    
    allocation_response = AllocationResponse(
        gid=new_allocation.gid,
        resource_type=new_allocation.resource_type,
        resource_subtype=new_allocation.resource_subtype,
        start_date=new_allocation.start_date,
        end_date=new_allocation.end_date,
        assignee=assignee_obj,
        parent=parent_obj,
        created_by=created_by_obj,
        effort=effort_obj
    )
    
    return AllocationResponseWrapper(data=allocation_response)


@router.put("/allocations/{allocation_gid}", response_model=AllocationResponseWrapper)
def update_allocation(
    allocation_gid: str = Path(..., description="Globally unique identifier for the allocation"),
    allocation_data: AllocationRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update an allocation (PUT request): Updates an existing allocation.
    """
    try:
        allocation_id = int(allocation_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid allocation GID format"
        )
    
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found"
        )
    
    update_data = allocation_data.dict(exclude_unset=True)
    
    if "assignee" in update_data and update_data["assignee"]:
        try:
            assignee_id = int(update_data["assignee"])
            assignee = db.query(User).filter(User.id == assignee_id).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found"
                )
            allocation.assignee_id = assignee_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee GID format"
            )
    
    if "parent" in update_data and update_data["parent"]:
        try:
            parent_id = int(update_data["parent"])
            parent = db.query(Project).filter(Project.id == parent_id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent project not found"
                )
            allocation.parent_id = parent_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent GID format"
            )
    
    if "start_date" in update_data:
        allocation.start_date = update_data["start_date"]
    if "end_date" in update_data:
        allocation.end_date = update_data["end_date"]
    if "effort_type" in update_data:
        allocation.effort_type = update_data["effort_type"]
    if "effort_value" in update_data:
        allocation.effort_value = update_data["effort_value"]
    if "resource_subtype" in update_data:
        allocation.resource_subtype = update_data["resource_subtype"]
    
    db.commit()
    db.refresh(allocation)
    
    # Build response
    assignee_obj = None
    if allocation.assignee:
        assignee_obj = UserCompact(
            gid=allocation.assignee.gid,
            resource_type=allocation.assignee.resource_type,
            name=allocation.assignee.name,
            email=allocation.assignee.email,
            photo=allocation.assignee.photo
        )
    
    parent_obj = None
    if allocation.parent:
        parent_obj = ProjectCompact(
            gid=allocation.parent.gid,
            resource_type=allocation.parent.resource_type,
            name=allocation.parent.name,
            resource_subtype=None
        )
    
    created_by_obj = None
    if allocation.created_by:
        created_by_obj = UserCompact(
            gid=allocation.created_by.gid,
            resource_type=allocation.created_by.resource_type,
            name=allocation.created_by.name,
            email=allocation.created_by.email,
            photo=allocation.created_by.photo
        )
    
    effort_obj = None
    if allocation.effort_type or allocation.effort_value:
        effort_obj = Effort(
            type=allocation.effort_type,
            value=float(allocation.effort_value) if allocation.effort_value else None
        )
    
    allocation_response = AllocationResponse(
        gid=allocation.gid,
        resource_type=allocation.resource_type,
        resource_subtype=allocation.resource_subtype,
        start_date=allocation.start_date,
        end_date=allocation.end_date,
        assignee=assignee_obj,
        parent=parent_obj,
        created_by=created_by_obj,
        effort=effort_obj
    )
    
    return AllocationResponseWrapper(data=allocation_response)


@router.delete("/allocations/{allocation_gid}", response_model=EmptyResponse)
def delete_allocation(
    allocation_gid: str = Path(..., description="Globally unique identifier for the allocation"),
    db: Session = Depends(get_db)
):
    """
    Delete an allocation (DELETE request): Deletes a specific, existing allocation.
    """
    allocation = db.query(Allocation).filter(Allocation.gid == allocation_gid).first()
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found"
        )
    
    try:
        db.delete(allocation)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete allocation: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting allocation: {str(e)}"
        )
    
    return EmptyResponse(data={})

