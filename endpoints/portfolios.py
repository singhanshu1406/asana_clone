from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.portfolio import Portfolio
from models.user import User
from models.workspace import Workspace
from schemas.portfolio import (
    PortfolioResponse, PortfolioResponseWrapper, PortfolioListResponse,
    PortfolioCompact, PortfolioRequest, PortfolioUpdateRequest,
    PortfolioAddItemRequest, PortfolioRemoveItemRequest, EmptyResponse
)

router = APIRouter()


@router.get("/portfolios", response_model=PortfolioListResponse)
def get_portfolios(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    owner: Optional[str] = Query(None, description="The user to filter portfolios on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Portfolios (GET request): Returns compact portfolio records.
    """
    query = db.query(Portfolio)
    
    if workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        query = query.filter(Portfolio.workspace_id == workspace_obj.id)
    
    if owner:
        owner_obj = db.query(User).filter(User.gid == owner).first()
        if not owner_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
        query = query.filter(Portfolio.owner_id == owner_obj.id)
    
    portfolios = query.limit(limit).all()
    
    portfolio_compacts = []
    for portfolio in portfolios:
        portfolio_data = {
            "gid": portfolio.gid,
            "resource_type": portfolio.resource_type,
            "name": portfolio.name
        }
        portfolio_compacts.append(PortfolioCompact(**portfolio_data))
    
    return PortfolioListResponse(data=portfolio_compacts)


@router.get("/portfolios/{portfolio_gid}", response_model=PortfolioResponseWrapper)
def get_portfolio(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Portfolio (GET request): Returns the complete portfolio record.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    portfolio_data = {
        "gid": portfolio.gid,
        "resource_type": portfolio.resource_type,
        "name": portfolio.name,
        "color": portfolio.color,
        "public": portfolio.public,
        "created_at": portfolio.created_at
    }
    
    return PortfolioResponseWrapper(data=PortfolioResponse(**portfolio_data))


@router.post("/portfolios", response_model=PortfolioResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_data: PortfolioRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Portfolio (POST request): Creates a new portfolio in the given workspace.
    """
    portfolio = Portfolio(
        gid=generate_gid(),
        resource_type="portfolio",
        name=portfolio_data.name or "New Portfolio"
    )
    
    if portfolio_data.workspace:
        workspace_obj = db.query(Workspace).filter(Workspace.gid == portfolio_data.workspace).first()
        if not workspace_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        portfolio.workspace_id = workspace_obj.id
    
    if portfolio_data.public is not None:
        portfolio.public = portfolio_data.public
    
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    
    portfolio_response = PortfolioResponse(
        gid=portfolio.gid,
        resource_type=portfolio.resource_type,
        name=portfolio.name,
        color=portfolio.color,
        public=portfolio.public,
        created_at=portfolio.created_at
    )
    
    return PortfolioResponseWrapper(data=portfolio_response)


@router.put("/portfolios/{portfolio_gid}", response_model=PortfolioResponseWrapper)
def update_portfolio(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio"),
    portfolio_data: PortfolioUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Portfolio (PUT request): An existing portfolio can be updated.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio_data.name is not None:
        portfolio.name = portfolio_data.name
    if portfolio_data.color is not None:
        portfolio.color = portfolio_data.color
    
    db.commit()
    db.refresh(portfolio)
    
    portfolio_response = PortfolioResponse(
        gid=portfolio.gid,
        resource_type=portfolio.resource_type,
        name=portfolio.name,
        color=portfolio.color,
        public=portfolio.public,
        created_at=portfolio.created_at
    )
    
    return PortfolioResponseWrapper(data=portfolio_response)


@router.delete("/portfolios/{portfolio_gid}", response_model=EmptyResponse)
def delete_portfolio(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Portfolio (DELETE request): A specific, existing portfolio can be deleted.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    try:
        db.delete(portfolio)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete portfolio: it has dependent records (e.g., portfolio memberships). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting portfolio: {str(e)}"
        )
    
    return EmptyResponse()

