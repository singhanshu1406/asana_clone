from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class EnumOption(Base):
    __tablename__ = "enum_options"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="enum_option")
    name = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    color = Column(String(50))
    custom_field_id = Column(Integer, ForeignKey("custom_fields.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    custom_field = relationship("CustomField")

