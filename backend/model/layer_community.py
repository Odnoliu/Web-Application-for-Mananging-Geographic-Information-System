from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class LayerCommunity(Base):
    __tablename__ = "layer_community"
    layer_community_id = Column(Integer, primary_key=True, autoincrement=True)
    layer_id = Column(Integer, ForeignKey("layers.layer_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    layer_community_name = Column(String(255))
    layer_community_description = Column(String(500))
    status = Column(Boolean, default=True)
    access_rights = Column(String(50), nullable=False)
    layer_community_image = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())