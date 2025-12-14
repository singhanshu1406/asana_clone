from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="task")
    name = Column(String(255), nullable=False)
    notes = Column(Text)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    due_on = Column(Date)
    due_at = Column(DateTime(timezone=True))
    start_on = Column(Date)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    assignee_status = Column(String(50))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    parent_id = Column(Integer, ForeignKey("tasks.id"))
    num_subtasks = Column(Integer, default=0)
    num_likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    assignee = relationship("User", foreign_keys=[assignee_id])
    workspace = relationship("Workspace")
    parent = relationship("Task", remote_side=[id])

