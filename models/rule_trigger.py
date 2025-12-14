from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class RuleTrigger(Base):
    __tablename__ = "rule_triggers"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="rule_trigger")
    resource_subtype = Column(String(50))
    trigger_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

