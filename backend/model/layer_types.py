from sqlalchemy import Column, String
from model.connect import Base


class LayerType(Base):
    __tablename__ = "layer_types"
    layer_type_id = Column(String(10), primary_key=True)
    layer_type = Column(String(50), nullable=False, unique=True)