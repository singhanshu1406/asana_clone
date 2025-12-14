from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class GoalRelationship(Base):
    __tablename__ = "goal_relationships"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="goal_relationship")
    resource_subtype = Column(String(50))
    supporting_goal_id = Column(Integer, ForeignKey("goals.id"))
    supported_goal_id = Column(Integer, ForeignKey("goals.id"))
    contribution_weight = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supporting_goal = relationship("Goal", foreign_keys=[supporting_goal_id])
    supported_goal = relationship("Goal", foreign_keys=[supported_goal_id])

