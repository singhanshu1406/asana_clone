from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CustomField(Base):
    __tablename__ = "custom_fields"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="custom_field")
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    resource_subtype = Column(String(50))
    enabled = Column(Boolean, default=True)
    custom_id = Column(String(255))
    id_prefix = Column(String(50))
    is_formula_field = Column(Boolean, default=False)
    input_restrictions = Column(ARRAY(String))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("Workspace")
    created_by = relationship("User", foreign_keys=[created_by_id])

