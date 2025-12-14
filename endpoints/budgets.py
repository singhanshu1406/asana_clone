from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.budget import Budget
from models.project import Project
from schemas.budget import (
    BudgetResponse, BudgetResponseWrapper, BudgetListResponse,
    BudgetRequest, BudgetEstimate, BudgetActual, BudgetTotal, EmptyResponse
)
from schemas.base import ProjectCompact

router = APIRouter()


@router.get("/budgets", response_model=BudgetListResponse)
def get_budgets(
    parent: str = Query(..., description="Globally unique identifier for the budget's parent object. This currently can only be a project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get all budgets (GET request): Gets all budgets for a given parent.
    """
    try:
        parent_id = int(parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent GID format"
        )
    
    project = db.query(Project).filter(Project.id == parent_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent project not found"
        )
    
    budgets = db.query(Budget).filter(Budget.parent_id == parent_id).all()
    
    budget_responses = []
    for budget in budgets:
        parent_obj = ProjectCompact(
            gid=project.gid,
            resource_type=project.resource_type,
            name=project.name,
            resource_subtype=None
        )
        
        estimate_obj = None
        if budget.estimate_enabled is not None or budget.estimate_source or budget.estimate_value:
            estimate_obj = BudgetEstimate(
                enabled=budget.estimate_enabled,
                source=budget.estimate_source,
                billable_status_filter=budget.estimate_billable_status_filter,
                value=float(budget.estimate_value) if budget.estimate_value else None,
                units=budget.estimate_units
            )
        
        actual_obj = None
        if budget.actual_value or budget.actual_billable_status_filter:
            actual_obj = BudgetActual(
                billable_status_filter=budget.actual_billable_status_filter,
                value=float(budget.actual_value) if budget.actual_value else None,
                units=budget.actual_units
            )
        
        total_obj = None
        if budget.total_enabled is not None or budget.total_value:
            total_obj = BudgetTotal(
                enabled=budget.total_enabled,
                value=float(budget.total_value) if budget.total_value else None,
                units=budget.total_units
            )
        
        budget_data = {
            "gid": budget.gid,
            "resource_type": budget.resource_type,
            "budget_type": budget.budget_type,
            "estimate": estimate_obj,
            "actual": actual_obj,
            "total": total_obj,
            "parent": parent_obj
        }
        budget_responses.append(BudgetResponse(**budget_data))
    
    return BudgetListResponse(data=budget_responses)


@router.post("/budgets", response_model=BudgetResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a budget (POST request): Creates a new budget.
    """
    if not budget_data.parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="parent is required"
        )
    
    try:
        parent_id = int(budget_data.parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent GID format"
        )
    
    project = db.query(Project).filter(Project.id == parent_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent project not found"
        )
    
    new_budget = Budget(
        gid=generate_gid(),
        resource_type="budget",
        budget_type=budget_data.budget_type,
        estimate_enabled=budget_data.estimate_enabled,
        estimate_source=budget_data.estimate_source,
        estimate_billable_status_filter=budget_data.estimate_billable_status_filter,
        estimate_value=budget_data.estimate_value,
        estimate_units=budget_data.estimate_units,
        actual_billable_status_filter=budget_data.actual_billable_status_filter,
        actual_value=budget_data.actual_value,
        actual_units=budget_data.actual_units,
        total_enabled=budget_data.total_enabled,
        total_value=budget_data.total_value,
        total_units=budget_data.total_units,
        parent_id=parent_id
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    parent_obj = ProjectCompact(
        gid=project.gid,
        resource_type=project.resource_type,
        name=project.name,
        resource_subtype=None
    )
    
    estimate_obj = None
    if new_budget.estimate_enabled is not None or new_budget.estimate_source or new_budget.estimate_value:
        estimate_obj = BudgetEstimate(
            enabled=new_budget.estimate_enabled,
            source=new_budget.estimate_source,
            billable_status_filter=new_budget.estimate_billable_status_filter,
            value=float(new_budget.estimate_value) if new_budget.estimate_value else None,
            units=new_budget.estimate_units
        )
    
    actual_obj = None
    if new_budget.actual_value or new_budget.actual_billable_status_filter:
        actual_obj = BudgetActual(
            billable_status_filter=new_budget.actual_billable_status_filter,
            value=float(new_budget.actual_value) if new_budget.actual_value else None,
            units=new_budget.actual_units
        )
    
    total_obj = None
    if new_budget.total_enabled is not None or new_budget.total_value:
        total_obj = BudgetTotal(
            enabled=new_budget.total_enabled,
            value=float(new_budget.total_value) if new_budget.total_value else None,
            units=new_budget.total_units
        )
    
    budget_response = BudgetResponse(
        gid=new_budget.gid,
        resource_type=new_budget.resource_type,
        budget_type=new_budget.budget_type,
        estimate=estimate_obj,
        actual=actual_obj,
        total=total_obj,
        parent=parent_obj
    )
    
    return BudgetResponseWrapper(data=budget_response)


@router.get("/budgets/{budget_gid}", response_model=BudgetResponseWrapper)
def get_budget(
    budget_gid: str = Path(..., description="Globally unique identifier for the budget"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a budget (GET request): Returns the complete budget record for a single budget.
    """
    try:
        budget_id = int(budget_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid budget GID format"
        )
    
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    project = db.query(Project).filter(Project.id == budget.parent_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent project not found"
        )
    
    parent_obj = ProjectCompact(
        gid=project.gid,
        resource_type=project.resource_type,
        name=project.name,
        resource_subtype=None
    )
    
    estimate_obj = None
    if budget.estimate_enabled is not None or budget.estimate_source or budget.estimate_value:
        estimate_obj = BudgetEstimate(
            enabled=budget.estimate_enabled,
            source=budget.estimate_source,
            billable_status_filter=budget.estimate_billable_status_filter,
            value=float(budget.estimate_value) if budget.estimate_value else None,
            units=budget.estimate_units
        )
    
    actual_obj = None
    if budget.actual_value or budget.actual_billable_status_filter:
        actual_obj = BudgetActual(
            billable_status_filter=budget.actual_billable_status_filter,
            value=float(budget.actual_value) if budget.actual_value else None,
            units=budget.actual_units
        )
    
    total_obj = None
    if budget.total_enabled is not None or budget.total_value:
        total_obj = BudgetTotal(
            enabled=budget.total_enabled,
            value=float(budget.total_value) if budget.total_value else None,
            units=budget.total_units
        )
    
    budget_data = {
        "gid": budget.gid,
        "resource_type": budget.resource_type,
        "budget_type": budget.budget_type,
        "estimate": estimate_obj,
        "actual": actual_obj,
        "total": total_obj,
        "parent": parent_obj
    }
    
    return BudgetResponseWrapper(data=BudgetResponse(**budget_data))


@router.put("/budgets/{budget_gid}", response_model=BudgetResponseWrapper)
def update_budget(
    budget_gid: str = Path(..., description="Globally unique identifier for the budget"),
    budget_data: BudgetRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a budget (PUT request): Updates an existing budget.
    """
    try:
        budget_id = int(budget_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid budget GID format"
        )
    
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    update_data = budget_data.dict(exclude_unset=True)
    
    if "budget_type" in update_data:
        budget.budget_type = update_data["budget_type"]
    if "estimate_enabled" in update_data:
        budget.estimate_enabled = update_data["estimate_enabled"]
    if "estimate_source" in update_data:
        budget.estimate_source = update_data["estimate_source"]
    if "estimate_billable_status_filter" in update_data:
        budget.estimate_billable_status_filter = update_data["estimate_billable_status_filter"]
    if "estimate_value" in update_data:
        budget.estimate_value = update_data["estimate_value"]
    if "estimate_units" in update_data:
        budget.estimate_units = update_data["estimate_units"]
    if "actual_billable_status_filter" in update_data:
        budget.actual_billable_status_filter = update_data["actual_billable_status_filter"]
    if "actual_value" in update_data:
        budget.actual_value = update_data["actual_value"]
    if "actual_units" in update_data:
        budget.actual_units = update_data["actual_units"]
    if "total_enabled" in update_data:
        budget.total_enabled = update_data["total_enabled"]
    if "total_value" in update_data:
        budget.total_value = update_data["total_value"]
    if "total_units" in update_data:
        budget.total_units = update_data["total_units"]
    
    db.commit()
    db.refresh(budget)
    
    project = db.query(Project).filter(Project.id == budget.parent_id).first()
    parent_obj = ProjectCompact(
        gid=project.gid,
        resource_type=project.resource_type,
        name=project.name,
        resource_subtype=None
    )
    
    estimate_obj = None
    if budget.estimate_enabled is not None or budget.estimate_source or budget.estimate_value:
        estimate_obj = BudgetEstimate(
            enabled=budget.estimate_enabled,
            source=budget.estimate_source,
            billable_status_filter=budget.estimate_billable_status_filter,
            value=float(budget.estimate_value) if budget.estimate_value else None,
            units=budget.estimate_units
        )
    
    actual_obj = None
    if budget.actual_value or budget.actual_billable_status_filter:
        actual_obj = BudgetActual(
            billable_status_filter=budget.actual_billable_status_filter,
            value=float(budget.actual_value) if budget.actual_value else None,
            units=budget.actual_units
        )
    
    total_obj = None
    if budget.total_enabled is not None or budget.total_value:
        total_obj = BudgetTotal(
            enabled=budget.total_enabled,
            value=float(budget.total_value) if budget.total_value else None,
            units=budget.total_units
        )
    
    budget_response = BudgetResponse(
        gid=budget.gid,
        resource_type=budget.resource_type,
        budget_type=budget.budget_type,
        estimate=estimate_obj,
        actual=actual_obj,
        total=total_obj,
        parent=parent_obj
    )
    
    return BudgetResponseWrapper(data=budget_response)


@router.delete("/budgets/{budget_gid}", response_model=EmptyResponse)
def delete_budget(
    budget_gid: str = Path(..., description="Globally unique identifier for the budget"),
    db: Session = Depends(get_db)
):
    """
    Delete a budget (DELETE request): Deletes a specific, existing budget.
    """
    budget = db.query(Budget).filter(Budget.gid == budget_gid).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    try:
        db.delete(budget)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete budget: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting budget: {str(e)}"
        )
    
    return EmptyResponse(data={})

