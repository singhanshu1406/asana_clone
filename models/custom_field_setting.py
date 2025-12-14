from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CustomFieldSetting(Base):
    __tablename__ = "custom_field_settings"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="custom_field_setting")
    is_important = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    custom_field_id = Column(Integer, ForeignKey("custom_fields.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
    portfolio = relationship("Portfolio")
    custom_field = relationship("CustomField")

