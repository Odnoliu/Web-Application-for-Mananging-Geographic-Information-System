from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from model.default_feature import DefaultFeature 
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
from geoalchemy2.functions import ST_Intersects, ST_GeomFromText
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_AsGeoJSON
router = APIRouter(prefix="/default-features", tags=["default-features"])

# Pydantic models for request and response
class DefaultFeatureResponse(BaseModel):
    id: int
    geom: dict
    GID_1: str | None
    GID_0: str | None
    COUNTRY: str | None
    NAME_1: str | None
    VARNAME_1: str | None
    NL_NAME_1: str | None
    TYPE_1: str | None
    ENGTYPE_1: str | None
    CC_1: str | None
    HASC_1: str | None
    ISO_1: str | None
    layer_id: int
    class Config:
        orm_mode = True

class DefaultFeatureCreate(BaseModel):
    geom: str  # WKT format for MULTIPOLYGON
    GID_1: str | None
    GID_0: str | None
    COUNTRY: str | None
    NAME_1: str | None
    VARNAME_1: str | None
    NL_NAME_1: str | None
    TYPE_1: str | None
    ENGTYPE_1: str | None
    CC_1: str | None
    HASC_1: str | None
    ISO_1: str | None
    layer_id: int
    geom: dict

class DefaultFeatureUpdate(BaseModel):
    geom: str | None  # WKT format for MULTIPOLYGON
    GID_1: str | None
    GID_0: str | None
    COUNTRY: str | None
    NAME_1: str | None
    VARNAME_1: str | None
    NL_NAME_1: str | None
    TYPE_1: str | None
    ENGTYPE_1: str | None
    CC_1: str | None
    HASC_1: str | None
    ISO_1: str | None
    layer_id: int | None
    geom: dict
class LayerFeatureResponse(BaseModel):
    layer_id: int
    feature_ids: List[int]
    
class SpatialQueryRequest(BaseModel):
    wkt: str  # WKT geometry for spatial query
    layer_id: int | None  # Optional layer_id filter

# CRUD Endpoints
@router.get("/", response_model=List[DefaultFeatureResponse])
async def get_all_features(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    features = db.query(DefaultFeature).all()
    return features

@router.get("/{feature_id}", response_model=DefaultFeatureResponse)
async def get_feature(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    feature = db.query(DefaultFeature).filter(DefaultFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    return feature

@router.post("/", response_model=DefaultFeatureResponse)
async def create_feature(
    feature_data: DefaultFeatureCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    feature = DefaultFeature(**feature_data.dict())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature

@router.put("/{feature_id}", response_model=DefaultFeatureResponse)
async def update_feature(
    feature_id: int,
    feature_data: DefaultFeatureUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    feature = db.query(DefaultFeature).filter(DefaultFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    
    for key, value in feature_data.dict(exclude_unset=True).items():
        setattr(feature, key, value)
    
    db.commit()
    db.refresh(feature)
    return feature

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    feature = db.query(DefaultFeature).filter(DefaultFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    
    db.delete(feature)
    db.commit()
    return None

# Additional Endpoints
@router.get("/{layer_id}", response_model=List[DefaultFeatureResponse])
async def get_features_by_layer(
    layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    features = db.query(DefaultFeature).filter(DefaultFeature.layer_id == layer_id).all()
    if not features:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No features found for this layer")
    return features

@router.post("/by-layer-ids", response_model=List[dict])
async def get_features_by_layer_ids(
    layer_ids: List[int],
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    features = db.query(
        DefaultFeature.id,
        DefaultFeature.GID_1,
        DefaultFeature.GID_0,
        DefaultFeature.COUNTRY,
        DefaultFeature.NAME_1,
        DefaultFeature.VARNAME_1,
        DefaultFeature.NL_NAME_1,
        DefaultFeature.TYPE_1,
        DefaultFeature.ENGTYPE_1,
        DefaultFeature.CC_1,
        DefaultFeature.HASC_1,
        DefaultFeature.ISO_1,
        DefaultFeature.layer_id,
        ST_AsGeoJSON(DefaultFeature.geom).label('geometry')
    ).filter(DefaultFeature.layer_id.in_(layer_ids)).all()
    
    if not features:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No features found for these layer IDs")
    
    # Chuyển Row objects thành dictionary
    return [feature._asdict() for feature in features]

@router.post("/feature_ids-by-layer-ids", response_model=List[LayerFeatureResponse])
async def get_feature_ids_by_layer_ids(
    layer_ids: List[int],
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    features = db.query(DefaultFeature.layer_id, DefaultFeature.id).filter(DefaultFeature.layer_id.in_(layer_ids)).all()
    
    if not features:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No feature IDs found for these layer IDs")
    
    feature_map = {}
    for layer_id, feature_id in features:
        if layer_id not in feature_map:
            feature_map[layer_id] = []
        feature_map[layer_id].append(feature_id)
        
    response = [
        {"layer_id": layer_id, "feature_ids": feature_ids}
        for layer_id, feature_ids in feature_map.items()
    ]
    
    for layer_id in layer_ids:
        if layer_id not in feature_map:
            response.append({"layer_id": layer_id, "feature_ids": []})
            
    response.sort(key=lambda x: x["layer_id"])
    
    return response

@router.post("/by-spatial", response_model=List[DefaultFeatureResponse])
async def get_features_by_spatial(
    query: SpatialQueryRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    try:
        # Tạo truy vấn cơ bản
        query_builder = db.query(DefaultFeature)
        
        # Thêm điều kiện không gian
        query_builder = query_builder.filter(
            ST_Intersects(DefaultFeature.geom, ST_GeomFromText(query.wkt, 4326))
        )
        
        # Thêm điều kiện layer_id nếu có
        if query.layer_id is not None:
            query_builder = query_builder.filter(DefaultFeature.layer_id == query.layer_id)
        
        features = query_builder.all()
        
        if not features:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No features found for this spatial query")
        
        return features
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid WKT format or spatial query error: {str(e)}")