from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class StatusUpdate(Base):
    __tablename__ = "status_updates"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="status_update")
    text = Column(Text)
    html_text = Column(Text)
    status_type = Column(String(50))
    title = Column(String(255))
    author_id = Column(Integer, ForeignKey("users.id"))
    resource_subtype = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", foreign_keys=[author_id])

