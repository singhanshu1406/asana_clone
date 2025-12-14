from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class TimeTrackingEntry(Base):
    __tablename__ = "time_tracking_entries"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="time_tracking_entry")
    duration_minutes = Column(Integer)
    entered_on = Column(Date)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    attributable_to_id = Column(Integer, ForeignKey("projects.id"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    task = relationship("Task")
    attributable_to = relationship("Project", foreign_keys=[attributable_to_id])
    portfolio = relationship("Portfolio")
    user = relationship("User", foreign_keys=[user_id])
    workspace = relationship("Workspace")
    created_by = relationship("User", foreign_keys=[created_by_id])

