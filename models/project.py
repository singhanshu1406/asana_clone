from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="project")
    name = Column(String(255), nullable=False)
    notes = Column(Text)
    archived = Column(Boolean, default=False)
    color = Column(String(50))
    default_view = Column(String(50))
    due_date = Column(Date)
    start_on = Column(Date)
    current_status_update_id = Column(Integer, ForeignKey("project_statuses.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("Workspace")
    team = relationship("Team")
    owner = relationship("User", foreign_keys=[owner_id])
    current_status_update = relationship("ProjectStatus", foreign_keys=[current_status_update_id])

