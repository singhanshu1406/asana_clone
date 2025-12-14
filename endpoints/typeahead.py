from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from models.workspace import Workspace
from models.user import User
from models.project import Project
from models.task import Task
from schemas.base import AsanaResource
from pydantic import BaseModel

router = APIRouter()


class TypeaheadItem(AsanaResource):
    """Typeahead item"""
    name: Optional[str] = None

    class Config:
        from_attributes = True


class TypeaheadResponse(BaseModel):
    """Typeahead response"""
    data: List[TypeaheadItem]


@router.get("/typeahead", response_model=TypeaheadResponse)
def get_typeahead(
    workspace: str = Query(..., description="The workspace in which to get results."),
    type: str = Query(..., description="The type of values the typeahead should return. Note that unlike in most requests, the type parameter is required."),
    query: Optional[str] = Query(None, description="The string that will be used to search for relevant objects. If an empty string is passed in, the API will return results."),
    count: Optional[int] = Query(10, ge=1, le=100, description="The number of results to return. The default is 20 if this parameter is omitted, with a minimum of 1 and a maximum of 100. If there are fewer results found than requested, all results will be returned."),
    opt_pretty: Optional[bool] = Query(False, description="Pretty output format"),
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
    db: Session = Depends(get_db)
):
    """Get objects via typeahead"""
    workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
    if not workspace_obj:
        raise HTTPException(status_code=404, detail="Workspace not found")

    results = []
    
    if type == "user":
        query_obj = db.query(User)
        if query:
            query_obj = query_obj.filter(User.name.ilike(f"%{query}%"))
        users = query_obj.limit(count).all()
        results = [TypeaheadItem(gid=u.gid, resource_type="user", name=u.name) for u in users]
    elif type == "project":
        query_obj = db.query(Project).filter(Project.workspace_id == workspace_obj.id)
        if query:
            query_obj = query_obj.filter(Project.name.ilike(f"%{query}%"))
        projects = query_obj.limit(count).all()
        results = [TypeaheadItem(gid=p.gid, resource_type="project", name=p.name) for p in projects]
    elif type == "task":
        query_obj = db.query(Task)
        if query:
            query_obj = query_obj.filter(Task.name.ilike(f"%{query}%"))
        tasks = query_obj.limit(count).all()
        results = [TypeaheadItem(gid=t.gid, resource_type="task", name=t.name) for t in tasks]

    return TypeaheadResponse(data=results)

