from sqlalchemy import Column, String
from model.connect import Base


class ProjectType(Base):
    __tablename__ = "project_types"
    project_type_id = Column(String(10), primary_key=True)
    project_type = Column(String(50), nullable=False, unique=True)