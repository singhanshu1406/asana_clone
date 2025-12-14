from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.job import Job
from schemas.job import JobResponse, JobResponseWrapper

router = APIRouter()


@router.get("/jobs/{job_gid}", response_model=JobResponseWrapper)
def get_job(
    job_gid: str = Path(..., description="Globally unique identifier for the job"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """
    Get a Job (GET request): Returns the complete job record for a single job.
    """
    job = db.query(Job).filter(Job.gid == job_gid).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_data = {
        "gid": job.gid,
        "resource_type": job.resource_type,
        "resource_subtype": job.resource_subtype,
        "status": job.status,
        "new_project": None,
        "new_task": None,
        "new_project_template": None,
        "new_graph_export": None,
        "new_resource_export": None
    }
    
    return JobResponseWrapper(data=JobResponse(**job_data))

