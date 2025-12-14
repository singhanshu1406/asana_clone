from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.webhook import Webhook
from schemas.webhook import (
    WebhookResponse, WebhookResponseWrapper, WebhookListResponse,
    WebhookCompact, WebhookRequest, WebhookUpdateRequest, EmptyResponse
)

router = APIRouter()


@router.get("/webhooks", response_model=WebhookListResponse)
def get_webhooks(
    workspace: Optional[str] = Query(None, description="The workspace to filter results on"),
    resource: Optional[str] = Query(None, description="The resource to filter webhooks on"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Webhooks (GET request): Returns compact webhook records.
    """
    query = db.query(Webhook)
    
    if resource:
        try:
            resource_id = int(resource)
            query = query.filter(Webhook.resource_id == resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource GID format"
            )
    
    webhooks = query.limit(limit).all()
    
    webhook_compacts = []
    for webhook in webhooks:
        webhook_data = {
            "gid": webhook.gid,
            "resource_type": webhook.resource_type,
            "active": webhook.active,
            "target": webhook.target,
            "resource": None
        }
        webhook_compacts.append(WebhookCompact(**webhook_data))
    
    return WebhookListResponse(data=webhook_compacts)


@router.get("/webhooks/{webhook_gid}", response_model=WebhookResponseWrapper)
def get_webhook(
    webhook_gid: str = Path(..., description="Globally unique identifier for the webhook"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Webhook (GET request): Returns the complete webhook record.
    """
    try:
        webhook_id = int(webhook_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook GID format"
        )
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    webhook_data = {
        "gid": webhook.gid,
        "resource_type": webhook.resource_type,
        "active": webhook.active,
        "target": webhook.target,
        "resource": None,
        "created_at": webhook.created_at,
        "filters": webhook.filters if webhook.filters else []
    }
    
    return WebhookResponseWrapper(data=WebhookResponse(**webhook_data))


@router.post("/webhooks", response_model=WebhookResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_data: WebhookRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Webhook (POST request): Creates a new webhook.
    """
    try:
        resource_id = int(webhook_data.resource)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource GID format"
        )
    
    webhook = Webhook(
        gid=generate_gid(),
        resource_type="webhook",
        resource_id=resource_id,
        target=webhook_data.target,
        active=True,
        filters=[f.dict() for f in webhook_data.filters] if webhook_data.filters else []
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    webhook_response = WebhookResponse(
        gid=webhook.gid,
        resource_type=webhook.resource_type,
        active=webhook.active,
        target=webhook.target,
        resource=None,
        created_at=webhook.created_at,
        filters=webhook.filters if webhook.filters else []
    )
    
    return WebhookResponseWrapper(data=webhook_response)


@router.put("/webhooks/{webhook_gid}", response_model=WebhookResponseWrapper)
def update_webhook(
    webhook_gid: str = Path(..., description="Globally unique identifier for the webhook"),
    webhook_data: WebhookUpdateRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Update a Webhook (PUT request): An existing webhook can be updated.
    """
    try:
        webhook_id = int(webhook_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook GID format"
        )
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    if webhook_data.filters is not None:
        webhook.filters = [f.dict() for f in webhook_data.filters]
    
    db.commit()
    db.refresh(webhook)
    
    webhook_response = WebhookResponse(
        gid=webhook.gid,
        resource_type=webhook.resource_type,
        active=webhook.active,
        target=webhook.target,
        resource=None,
        created_at=webhook.created_at,
        filters=webhook.filters if webhook.filters else []
    )
    
    return WebhookResponseWrapper(data=webhook_response)


@router.delete("/webhooks/{webhook_gid}", response_model=EmptyResponse)
def delete_webhook(
    webhook_gid: str = Path(..., description="Globally unique identifier for the webhook"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Webhook (DELETE request): A specific, existing webhook can be deleted.
    """
    webhook = db.query(Webhook).filter(Webhook.gid == webhook_gid).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    try:
        db.delete(webhook)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete webhook: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting webhook: {str(e)}"
        )
    
    return EmptyResponse()

