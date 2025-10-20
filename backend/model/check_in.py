from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary, Float
from sqlalchemy.sql import func
from model.connect import Base
class CheckIn(Base):
    __tablename__ = "check_in"
    check_in_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    check_in_description = Column(String(500))
    check_in_image = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    longitude = Column(Float, nullable=True)        # map double precision
    latitude = Column(Float, nullable=True)         # map double precision
    place_id = Column(String(100), nullable=True)