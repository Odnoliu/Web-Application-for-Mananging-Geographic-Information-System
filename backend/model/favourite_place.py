from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from model.connect import Base

class FavouritePlace(Base):
    __tablename__ = "favourite_place"
    favourite_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    place_id = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())