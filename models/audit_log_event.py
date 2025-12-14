from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class AuditLogEvent(Base):
    __tablename__ = "audit_log_events"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="audit_log_event")
    event_type = Column(String(100))
    actor_type = Column(String(50))
    actor_gid = Column(String(255))
    resource_type_name = Column(String(100))
    resource_gid = Column(String(255))
    context = Column(JSON)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

