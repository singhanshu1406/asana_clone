from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="goal")
    name = Column(String(255), nullable=False)
    html_notes = Column(Text)
    notes = Column(Text)
    due_on = Column(Date)
    start_on = Column(Date)
    status = Column(String(50))
    is_workspace_level = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    num_likes = Column(Integer, default=0)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    time_period_id = Column(Integer, ForeignKey("time_periods.id"))
    metric_id = Column(Integer)
    parent_goal_id = Column(Integer, ForeignKey("goals.id"))
    current_status_update_id = Column(Integer, ForeignKey("status_updates.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("Workspace")
    team = relationship("Team")
    owner = relationship("User", foreign_keys=[owner_id])
    time_period = relationship("TimePeriod")
    parent_goal = relationship("Goal", remote_side=[id])
    current_status_update = relationship("StatusUpdate", foreign_keys=[current_status_update_id])

