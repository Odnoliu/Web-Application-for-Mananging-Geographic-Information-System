from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class AuthProvider(Base):
    __tablename__ = "auth_providers"
    provider_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    provider_name = Column(String(50), nullable=False)
    provider_user_id = Column(String(255))
    access_token = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())