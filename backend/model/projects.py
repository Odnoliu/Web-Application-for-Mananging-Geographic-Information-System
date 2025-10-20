from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    project_name = Column(String(255), nullable=False)
    project_img = Column(LargeBinary)
    project_type = Column(String(10), ForeignKey("project_types.project_type_id", ondelete="CASCADE"))
    project_status = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())