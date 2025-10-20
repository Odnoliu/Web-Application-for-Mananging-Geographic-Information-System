from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from model.connect import Base

class DefaultVectorLayer(Base):
    __tablename__ = "default_vector_layer"

    default_layer_id = Column(Integer, primary_key=True, autoincrement=True)
    default_layer_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())