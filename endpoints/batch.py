from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas.batch import BatchRequestWrapper, BatchResponseWrapper, BatchResponse

router = APIRouter()


@router.post("/batch", response_model=BatchResponseWrapper)
def create_batch_request(
    batch_data: BatchRequestWrapper = Body(...),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Submit parallel requests"""
    # This is a simplified implementation
    # In a real implementation, you'd execute the batch requests in parallel
    # and return the responses
    
    responses = []
    for request_item in batch_data.data:
        # Simplified: just return a mock response
        # In reality, you'd make the actual HTTP requests based on request_item.method and request_item.relative_path
        response = BatchResponse(
            status_code=200,
            headers={},
            body={"data": {"gid": "12345", "resource_type": "task"}}
        )
        responses.append(response)

    return BatchResponseWrapper(data=responses)

