from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="allocation")
    resource_subtype = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    effort_type = Column(String(50))  # "hours" or "percent"
    effort_value = Column(Numeric(10, 2))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("projects.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    assignee = relationship("User", foreign_keys=[assignee_id])
    parent = relationship("Project")
    created_by = relationship("User", foreign_keys=[created_by_id])

