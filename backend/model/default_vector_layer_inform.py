from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from model.connect import Base

class DefaultVectorLayerInform(Base):
    __tablename__ = "default_vector_layer_inform"

    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    default_layer_id = Column(Integer, ForeignKey("default_vector_layer.default_layer_id", ondelete="CASCADE"), primary_key=True)
    fill = Column(String(10))
    stroke = Column(String(10))
    stroke_width = Column(Integer)
    z_index = Column(Integer)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    base = Column(String(10))
    layer_name = Column(String(255))
    status = Column(Boolean, default=True)