from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from model.connect import Base

class DefaultFeatureSettings(Base):
    __tablename__ = "default_feature_settings"
    default_settings_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))
    default_layer_id = Column(Integer, ForeignKey("default_vector_layer.default_layer_id", ondelete="CASCADE"))
    default_feature_id = Column(Integer, ForeignKey("default_feature.id", ondelete="CASCADE"))
    default_feature_status = Column(Boolean, default=True)