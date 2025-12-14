from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), default="rate")
    rate = Column(Numeric(15, 2))
    currency_code = Column(String(10))
    parent_id = Column(Integer, ForeignKey("projects.id"))
    resource_id = Column(Integer, ForeignKey("users.id"))  # Can be user or placeholder
    resource_type_field = Column(String(50))  # "user" or "placeholder"
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parent = relationship("Project")
    resource = relationship("User", foreign_keys=[resource_id])
    created_by = relationship("User", foreign_keys=[created_by_id])

