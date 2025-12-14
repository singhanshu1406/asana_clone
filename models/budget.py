from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="budget")
    budget_type = Column(String(50))  # "cost" or "time"
    
    # Estimate fields
    estimate_enabled = Column(Boolean, default=True)
    estimate_source = Column(String(50))  # "none", "tasks", "capacity_plans"
    estimate_billable_status_filter = Column(String(50))  # "billable", "non_billable", "any"
    estimate_value = Column(Numeric(15, 2), nullable=True)
    estimate_units = Column(String(10), nullable=True)  # "minutes" or currency code
    
    # Actual fields
    actual_billable_status_filter = Column(String(50))  # "billable", "non_billable", "any"
    actual_value = Column(Numeric(15, 2), nullable=True)
    actual_units = Column(String(10), nullable=True)  # "minutes" or currency code
    
    # Total fields
    total_enabled = Column(Boolean, default=True)
    total_value = Column(Numeric(15, 2), nullable=True)
    total_units = Column(String(10), nullable=True)  # "minutes" or currency code
    
    parent_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parent = relationship("Project")

