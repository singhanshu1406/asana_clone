from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="attachment")
    name = Column(String(255))
    resource_subtype = Column(String(50))
    download_url = Column(String(500))
    view_url = Column(String(500))
    host = Column(String(255))
    parent_id = Column(Integer)
    parent_type = Column(String(50))
    permanent_url = Column(String(500))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", foreign_keys=[created_by_id])

