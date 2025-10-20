from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from model.connect import Base

class Feature(Base):
    __tablename__ = "features"
    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(String(255))
    layer_id = Column(Integer, ForeignKey("layers.layer_id", ondelete="CASCADE"))
    properties = Column(JSONB)
    feature_fill = Column(String(10))
    feature_stroke = Column(String(10))
    geom = Column(Geometry(geometry_type='GEOMETRY', srid=4326))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())