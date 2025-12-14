from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from database import get_db
from utils import generate_gid
from models.attachment import Attachment
from models.user import User
from models.project import Project
from models.task import Task
from models.project_brief import ProjectBrief
from schemas.attachment import (
    AttachmentResponse, AttachmentResponseWrapper, AttachmentListResponse,
    AttachmentCompact, AttachmentRequest, EmptyResponse
)
from schemas.base import UserCompact, ProjectCompact, TaskCompact

router = APIRouter()


@router.get("/attachments", response_model=AttachmentListResponse)
def get_attachments_for_object(
    parent: str = Query(..., description="Globally unique identifier for object to fetch attachments from. Must be a GID for a project, project_brief, or task"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get attachments from an object (GET request): Returns the compact records for all attachments on the object.
    """
    try:
        parent_id = int(parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent GID format"
        )
    
    # Determine parent type by checking which table has this ID
    project = db.query(Project).filter(Project.id == parent_id).first()
    task = db.query(Task).filter(Task.id == parent_id).first()
    project_brief = db.query(ProjectBrief).filter(ProjectBrief.id == parent_id).first()
    
    if not project and not task and not project_brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent object not found"
        )
    
    # Query attachments
    query = db.query(Attachment).filter(Attachment.parent_id == parent_id)
    attachments = query.limit(limit).all()
    
    attachment_compacts = []
    for attachment in attachments:
        attachment_data = {
            "gid": attachment.gid,
            "resource_type": attachment.resource_type,
            "name": attachment.name,
            "resource_subtype": attachment.resource_subtype
        }
        attachment_compacts.append(AttachmentCompact(**attachment_data))
    
    return AttachmentListResponse(data=attachment_compacts)


@router.get("/attachments/{attachment_gid}", response_model=AttachmentResponseWrapper)
def get_attachment(
    attachment_gid: str = Path(..., description="Globally unique identifier for the attachment"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get an attachment (GET request): Get the full record for a single attachment.
    """
    try:
        attachment_id = int(attachment_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attachment GID format"
        )
    
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    created_by_obj = None
    if attachment.created_by:
        created_by_obj = UserCompact(
            gid=attachment.created_by.gid,
            resource_type=attachment.created_by.resource_type,
            name=attachment.created_by.name,
            email=attachment.created_by.email,
            photo=attachment.created_by.photo
        )
    
    parent_obj = None
    if attachment.parent_type == "project":
        project = db.query(Project).filter(Project.id == attachment.parent_id).first()
        if project:
            parent_obj = {
                "gid": project.gid,
                "resource_type": project.resource_type,
                "name": project.name,
                "resource_subtype": None
            }
    elif attachment.parent_type == "task":
        task = db.query(Task).filter(Task.id == attachment.parent_id).first()
        if task:
            parent_obj = {
                "gid": task.gid,
                "resource_type": task.resource_type,
                "name": task.name,
                "resource_subtype": task.resource_subtype
            }
    elif attachment.parent_type == "project_brief":
        project_brief = db.query(ProjectBrief).filter(ProjectBrief.id == attachment.parent_id).first()
        if project_brief:
            parent_obj = {
                "gid": project_brief.gid,
                "resource_type": project_brief.resource_type
            }
    
    attachment_data = {
        "gid": attachment.gid,
        "resource_type": attachment.resource_type,
        "name": attachment.name,
        "resource_subtype": attachment.resource_subtype,
        "connected_to_app": False,  # Default value
        "created_at": attachment.created_at,
        "download_url": attachment.download_url,
        "host": attachment.host,
        "permanent_url": attachment.permanent_url,
        "size": None,  # Not stored in model
        "view_url": attachment.view_url,
        "parent": parent_obj,
        "created_by": created_by_obj
    }
    
    return AttachmentResponseWrapper(data=AttachmentResponse(**attachment_data))


@router.post("/attachments", response_model=AttachmentResponseWrapper)
def create_attachment_for_object(
    parent: str = Form(..., description="Globally unique identifier for the parent object"),
    file: Optional[UploadFile] = File(None, description="File to upload"),
    url: Optional[str] = Form(None, description="URL of the external resource"),
    name: Optional[str] = Form(None, description="Name of the attachment"),
    connect_to_app: Optional[bool] = Form(None, description="Connect to app"),
    resource_subtype: Optional[str] = Form(None, description="Resource subtype"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Upload an attachment (POST request): Upload an attachment on an object.
    """
    try:
        parent_id = int(parent)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent GID format"
        )
    
    # Determine parent type
    project = db.query(Project).filter(Project.id == parent_id).first()
    task = db.query(Task).filter(Task.id == parent_id).first()
    project_brief = db.query(ProjectBrief).filter(ProjectBrief.id == parent_id).first()
    
    if not project and not task and not project_brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent object not found"
        )
    
    parent_type = "project" if project else ("task" if task else "project_brief")
    
    # Get current user (in real implementation, from auth token)
    created_by = db.query(User).first()
    if not created_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found in system"
        )
    
    # In a real implementation, handle file upload
    # For now, create attachment record
    attachment_name = name or (file.filename if file else "Attachment")
    download_url = url or f"/attachments/{uuid.uuid4()}/download"
    view_url = f"/attachments/{uuid.uuid4()}/view"
    
    new_attachment = Attachment(
        gid=generate_gid(),
        resource_type="attachment",
        name=attachment_name,
        resource_subtype=resource_subtype or "external",
        download_url=download_url,
        view_url=view_url,
        host=None,
        parent_id=parent_id,
        parent_type=parent_type,
        permanent_url=download_url,
        created_by_id=created_by.id
    )
    
    db.add(new_attachment)
    db.commit()
    db.refresh(new_attachment)
    
    created_by_obj = UserCompact(
        gid=created_by.gid,
        resource_type=created_by.resource_type,
        name=created_by.name,
        email=created_by.email,
        photo=created_by.photo
    )
    
    parent_obj = None
    if parent_type == "project" and project:
        parent_obj = {
            "gid": project.gid,
            "resource_type": project.resource_type,
            "name": project.name,
            "resource_subtype": None
        }
    elif parent_type == "task" and task:
        parent_obj = {
            "gid": task.gid,
            "resource_type": task.resource_type,
            "name": task.name,
            "resource_subtype": task.resource_subtype
        }
    elif parent_type == "project_brief" and project_brief:
        parent_obj = {
            "gid": project_brief.gid,
            "resource_type": project_brief.resource_type
        }
    
    attachment_data = {
        "gid": new_attachment.gid,
        "resource_type": new_attachment.resource_type,
        "name": new_attachment.name,
        "resource_subtype": new_attachment.resource_subtype,
        "connected_to_app": connect_to_app or False,
        "created_at": new_attachment.created_at,
        "download_url": new_attachment.download_url,
        "host": new_attachment.host,
        "permanent_url": new_attachment.permanent_url,
        "size": None,
        "view_url": new_attachment.view_url,
        "parent": parent_obj,
        "created_by": created_by_obj
    }
    
    return AttachmentResponseWrapper(data=AttachmentResponse(**attachment_data))


@router.delete("/attachments/{attachment_gid}", response_model=EmptyResponse)
def delete_attachment(
    attachment_gid: str = Path(..., description="Globally unique identifier for the attachment"),
    db: Session = Depends(get_db)
):
    """
    Delete an attachment (DELETE request): Deletes a specific, existing attachment.
    """
    attachment = db.query(Attachment).filter(Attachment.gid == attachment_gid).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    try:
        db.delete(attachment)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete attachment: it has dependent records."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting attachment: {str(e)}"
        )
    
    return EmptyResponse(data={})

