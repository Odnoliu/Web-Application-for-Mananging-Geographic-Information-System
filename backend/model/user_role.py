from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(10), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True)
