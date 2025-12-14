from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserTaskList(Base):
    __tablename__ = "user_task_lists"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="user_task_list")
    name = Column(String(255))
    owner_id = Column(Integer, ForeignKey("users.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
    workspace = relationship("Workspace")

