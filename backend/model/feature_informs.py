from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from model.connect import Base

class FeatureInforms(Base):
    __tablename__ = "feature_informs"
    inform_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("features.feature_id", ondelete="CASCADE"))
    title = Column(String(255))
    content = Column(String(255))
    
    