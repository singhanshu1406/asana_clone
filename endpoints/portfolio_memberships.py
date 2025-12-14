from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.portfolio_membership import PortfolioMembership
from models.portfolio import Portfolio
from models.user import User
from models.team import Team
from schemas.portfolio_membership import (
    PortfolioMembershipResponse, PortfolioMembershipResponseWrapper,
    PortfolioMembershipListResponse, PortfolioMembershipCompact,
    PortfolioMembershipRequest, EmptyResponse
)

router = APIRouter()


@router.get("/portfolios/{portfolio_gid}/portfolio_memberships", response_model=PortfolioMembershipListResponse)
def get_portfolio_memberships(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio"),
    user: Optional[str] = Query(None, description="A string identifying a user"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Portfolio Memberships (GET request): Returns compact portfolio membership records.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    query = db.query(PortfolioMembership).filter(
        PortfolioMembership.portfolio_id == portfolio.id
    )
    
    if user:
        if user.lower() == "me":
            # Would need current user context
            pass
        elif "@" in user:
            user_obj = db.query(User).filter(User.email == user).first()
            if user_obj:
                query = query.filter(PortfolioMembership.user_id == user_obj.id)
        else:
            user_obj = db.query(User).filter(User.gid == user).first()
            if user_obj:
                query = query.filter(PortfolioMembership.user_id == user_obj.id)
    
    memberships = query.limit(limit).all()
    
    membership_compacts = []
    for membership in memberships:
        portfolio_obj = db.query(Portfolio).filter(Portfolio.id == membership.portfolio_id).first()
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
            "parent": {
                "gid": portfolio_obj.gid if portfolio_obj else "",
                "resource_type": "portfolio",
                "name": portfolio_obj.name if portfolio_obj else ""
            } if portfolio_obj else None,
            "member": member_obj,
            "access_level": membership.write_access or "viewer"
        }
        membership_compacts.append(PortfolioMembershipCompact(**membership_data))
    
    return PortfolioMembershipListResponse(data=membership_compacts)


@router.get("/portfolio_memberships/{portfolio_membership_gid}", response_model=PortfolioMembershipResponseWrapper)
def get_portfolio_membership(
    portfolio_membership_gid: str = Path(..., description="Globally unique identifier for the portfolio membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Portfolio Membership (GET request): Returns the complete portfolio membership record.
    """
    membership = db.query(PortfolioMembership).filter(PortfolioMembership.gid == portfolio_membership_gid).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio membership not found"
        )
    
    portfolio_obj = db.query(Portfolio).filter(Portfolio.id == membership.portfolio_id).first()
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
        "parent": {
            "gid": portfolio_obj.gid if portfolio_obj else "",
            "resource_type": "portfolio",
            "name": portfolio_obj.name if portfolio_obj else ""
        } if portfolio_obj else None,
        "member": member_obj,
        "access_level": membership.write_access or "viewer"
    }
    
    return PortfolioMembershipResponseWrapper(data=PortfolioMembershipResponse(**membership_data))


@router.post("/portfolios/{portfolio_gid}/portfolio_memberships", response_model=PortfolioMembershipResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_portfolio_membership(
    portfolio_gid: str = Path(..., description="Globally unique identifier for the portfolio"),
    membership_data: PortfolioMembershipRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Portfolio Membership (POST request): Creates a new portfolio membership.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.gid == portfolio_gid).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    membership = PortfolioMembership(
        gid=generate_gid(),
        resource_type="portfolio_membership",
        portfolio_id=portfolio_id
    )
    
    if membership_data.user:
        user_obj = db.query(User).filter(User.gid == membership_data.user).first()
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        membership.user_id = user_obj.id
    
    if membership_data.team:
        team_obj = db.query(Team).filter(Team.gid == membership_data.team).first()
        if not team_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        membership.team_id = team_obj.id
    
    if membership_data.access_level:
        membership.write_access = membership_data.access_level
    
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    # Build response
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
    
    membership_response_data = {
        "gid": membership.gid,
        "resource_type": membership.resource_type,
        "parent": {
            "gid": portfolio.gid,
            "resource_type": "portfolio",
            "name": portfolio.name
        },
        "member": member_obj,
        "access_level": membership.write_access or "viewer"
    }
    
    return PortfolioMembershipResponseWrapper(data=PortfolioMembershipResponse(**membership_response_data))


@router.delete("/portfolio_memberships/{portfolio_membership_gid}", response_model=EmptyResponse)
def delete_portfolio_membership(
    portfolio_membership_gid: str = Path(..., description="Globally unique identifier for the portfolio membership"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Portfolio Membership (DELETE request): A specific, existing portfolio membership can be deleted.
    """
    membership = db.query(PortfolioMembership).filter(PortfolioMembership.gid == portfolio_membership_gid).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio membership not found"
        )
    
    try:
        db.delete(membership)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete portfolio membership: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting portfolio membership: {str(e)}"
        )
    
    return EmptyResponse()

