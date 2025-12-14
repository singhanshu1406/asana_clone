from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from database import get_db
from utils import generate_gid
from models.section import Section
from models.project import Project
from schemas.section import (
    SectionResponse, SectionResponseWrapper, SectionListResponse,
    SectionCompact, SectionRequest, EmptyResponse
)

router = APIRouter()


@router.get("/projects/{project_gid}/sections", response_model=SectionListResponse)
def get_sections(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Results per page"),
    offset: Optional[str] = Query(None, description="Offset token"),
    db: Session = Depends(get_db)
):
    """
    Get Sections (GET request): Returns compact section records.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    sections = db.query(Section).filter(Section.project_id == project_id).limit(limit).all()
    
    section_compacts = []
    for section in sections:
        section_data = {
            "gid": section.gid,
            "resource_type": section.resource_type,
            "name": section.name
        }
        section_compacts.append(SectionCompact(**section_data))
    
    return SectionListResponse(data=section_compacts)


@router.get("/sections/{section_gid}", response_model=SectionResponseWrapper)
def get_section(
    section_gid: str = Path(..., description="Globally unique identifier for the section"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Section (GET request): Returns the complete section record.
    """
    try:
        section_id = int(section_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid section GID format"
        )
    
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    section_data = {
        "gid": section.gid,
        "resource_type": section.resource_type,
        "name": section.name,
        "created_at": section.created_at
    }
    
    return SectionResponseWrapper(data=SectionResponse(**section_data))


@router.post("/projects/{project_gid}/sections", response_model=SectionResponseWrapper, status_code=status.HTTP_201_CREATED)
def create_section(
    project_gid: str = Path(..., description="Globally unique identifier for the project"),
    section_data: SectionRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Create a Section (POST request): Creates a new section in a project.
    """
    try:
        project_id = int(project_gid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project GID format"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    section = Section(
        gid=generate_gid(),
        resource_type="section",
        name=section_data.name,
        project_id=project_id
    )
    
    db.add(section)
    db.commit()
    db.refresh(section)
    
    section_response = SectionResponse(
        gid=section.gid,
        resource_type=section.resource_type,
        name=section.name,
        created_at=section.created_at
    )
    
    return SectionResponseWrapper(data=section_response)


@router.delete("/sections/{section_gid}", response_model=EmptyResponse)
def delete_section(
    section_gid: str = Path(..., description="Globally unique identifier for the section"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """
    Delete a Section (DELETE request): A specific, existing section can be deleted.
    """
    section = db.query(Section).filter(Section.gid == section_gid).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    try:
        db.delete(section)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete section: it has dependent records (e.g., tasks). Please delete dependent records first."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting section: {str(e)}"
        )
    
    return EmptyResponse()

