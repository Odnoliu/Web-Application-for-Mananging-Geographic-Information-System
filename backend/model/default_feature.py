from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import VARCHAR
from geoalchemy2 import Geometry
from model.connect import Base

class DefaultFeature(Base):
    __tablename__ = "default_feature"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326))
    GID_1 = Column(VARCHAR)
    GID_0 = Column(VARCHAR)
    COUNTRY = Column(VARCHAR)
    NAME_1 = Column(VARCHAR)
    VARNAME_1 = Column(VARCHAR)
    NL_NAME_1 = Column(VARCHAR)
    TYPE_1 = Column(VARCHAR)
    ENGTYPE_1 = Column(VARCHAR)
    CC_1 = Column(VARCHAR)
    HASC_1 = Column(VARCHAR)
    ISO_1 = Column(VARCHAR)
    layer_id = Column(Integer, ForeignKey('default_vector_layer.default_layer_id', ondelete='CASCADE'))