from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base


class Role(Base):
    __tablename__ = "roles"
    role_id = Column(String(10), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)