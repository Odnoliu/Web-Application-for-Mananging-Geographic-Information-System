from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from model.connect import Base

class CommunityAccessControl(Base):
    __tablename__ = "community_access_control"
    access_control_id = Column(Integer, primary_key=True, autoincrement=True)
    layer_community_id = Column(Integer, ForeignKey("layer_community.layer_community_id", ondelete="CASCADE"), nullable=True)
    feature_community_id = Column(Integer, ForeignKey("feature_community.feature_community_id", ondelete="CASCADE"), nullable=True)
    user_informs = Column(String(255), nullable=False)