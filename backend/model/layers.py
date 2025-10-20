from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class Layer(Base):
    __tablename__ = "layers"
    layer_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))
    layer_name = Column(String(255), nullable=False)
    fill = Column(String(10))
    stroke = Column(String(10))
    stroke_width = Column(Integer)
    z_index = Column(Integer)
    layer_type = Column(String(10), ForeignKey("layer_types.layer_type_id", ondelete="CASCADE"))
    user_layer_status = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())