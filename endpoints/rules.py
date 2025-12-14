from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas.rule import RuleTriggerRequest, RuleTriggerResponseWrapper, RuleTriggerResponse

router = APIRouter()


@router.post("/rules/{rule_trigger_gid}/trigger", response_model=RuleTriggerResponseWrapper)
def trigger_rule(
    rule_trigger_gid: str = Path(..., description="The ID of the incoming web request trigger. This value is a path parameter that is automatically generated for the API endpoint."),
    trigger_data: RuleTriggerRequest = Body(..., alias="data"),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    db: Session = Depends(get_db)
):
    """Trigger a rule"""
    # In a real implementation, you'd execute the rule logic
    # For now, we'll return a success response
    response = RuleTriggerResponse(
        success=True,
        message="Rule triggered successfully"
    )

    return RuleTriggerResponseWrapper(data=response)

