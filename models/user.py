from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="user")
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    photo = Column(String(500))
    workspaces = Column(ARRAY(String))
    is_workspace_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

