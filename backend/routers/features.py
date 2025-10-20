from fastapi import Depends, HTTPException, status, APIRouter, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from model.features import Feature
from model.layers import Layer
from model.projects import Project
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
from geoalchemy2.shape import from_shape, to_shape
from utils.file_processor import process_json, process_kmz, process_gpkg, process_zip
from shapely.geometry import shape, mapping
import json

router = APIRouter(prefix="/features", tags=["features"])

class FeatureCreate(BaseModel):
    layer_id: int
    feature_name: Optional[str] = None
    properties: Optional[Dict] = None
    feature_fill: Optional[str] = None
    feature_stroke: Optional[str] = None
    geom: str 

class FeatureUpdate(BaseModel):
    feature_name: Optional[str] = None
    properties: Optional[Dict] = None
    feature_fill: Optional[str] = None
    feature_stroke: Optional[str] = None
    geom: Optional[str] = None
    
class DrawFeatureItem(BaseModel):
    layer_id: int
    feature: dict 
    
class UploadFeatureForm(BaseModel):
    layer_id: int
    layer_community_id: Optional[int] = None
    feature_community_id: Optional[int] = None

@router.post("/")
async def create_feature(feature: FeatureCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    # Verify layer exists and belongs to user's project
    layer = db.query(Layer).join(Project).filter(Layer.layer_id == feature.layer_id, Project.user_id == user_id).first()
    if not layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    
    db_feature = Feature(**feature.dict())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.get("/{feature_id}")
async def get_feature(feature_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    feature = db.query(Feature).filter(Feature.feature_id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    
    return {
        "feature_id": feature.feature_id,
        "layer_id": feature.layer_id,
        "feature_name": feature.feature_name,
        "properties": json.loads(feature.properties) if feature.properties else {},
        "geom": mapping(to_shape(feature.geom)), # Chuyển WKBElement thành GeoJSON
        "feature_fill": feature.feature_fill,
        "feature_stroke": feature.feature_stroke,
        "created_at": feature.created_at,
        "updated_at": feature.updated_at
    }

@router.put("/{feature_id}")
async def update_feature(feature_id: int, feature: FeatureUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_feature = db.query(Feature).join(Layer).join(Project).filter(Feature.feature_id == feature_id, Project.user_id == user_id).first()
    if not db_feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    
    for key, value in feature.dict(exclude_unset=True).items():
        setattr(db_feature, key, value)
    
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.delete("/{feature_id}")
async def delete_feature(feature_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_feature = db.query(Feature).filter(Feature.feature_id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")
    
    db.delete(db_feature)
    db.commit()
    return {"message": "Feature deleted successfully"}

@router.post("/by-ids")
async def get_features_by_layer_ids(
    layer_ids: List[int],  # Nhận mảng layer_ids từ query parameter
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Lấy user hiện tại
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Kiểm tra các layer tồn tại và thuộc về user
    layers = db.query(Layer).filter(
        Layer.layer_id.in_(layer_ids),
    ).all()
    if not layers or len(layers) != len(layer_ids):
        return []

    # Lấy tất cả feature theo mảng layer_ids
    features = db.query(Feature).filter(Feature.layer_id.in_(layer_ids)).all()

    # Chuyển đổi dữ liệu feature thành định dạng phù hợp cho frontend
    features_data = [
        {
            "feature_id": feature.feature_id,
            "layer_id": feature.layer_id,
            "name": feature.feature_name or "Unnamed",
            "properties": json.loads(feature.properties) if feature.properties else {},
            "geom": mapping(to_shape(feature.geom))  # Chuyển WKBElement thành GeoJSON
        }
        for feature in features
    ]

    # Nhóm features theo layer_id để trả về cấu trúc phù hợp
    grouped_features = {}
    for layer in layers:
        grouped_features[layer.layer_id] = {
            "layer": {
                "id": layer.layer_id,
                "name": layer.layer_name,
                "fill": layer.fill,
                "stroke": layer.stroke,
                "stroke_width": layer.stroke_width,
                "priority": layer.z_index
            },
            "features": [f for f in features_data if f["layer_id"] == layer.layer_id]
        }

    # Trả về response
    return list(grouped_features.values())

@router.post("/feature-to-layers")
async def upload_layer(form: Optional[str] = Form(...), file: Optional[UploadFile] = File(None), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    try:
        form_data = json.loads(form)
        print(form_data)
        form_model = UploadFeatureForm(**form_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid form data format")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    layer = db.query(Layer).filter(Layer.layer_id == form_model.layer_id).first()
    if not layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    print(form_model)
    feature_ids = []
    # Nếu không có file, trả về ngay với layer_id
    if file:
        print("dòng file này chạy nè")
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        try:
            if extension in ['json', 'geojson']:
                features_data = process_json(file.file)
            elif extension == 'kmz':
                features_data = process_kmz(file.file)
            elif extension == 'gpkg':
                features_data = process_gpkg(file.file)
            elif extension == 'zip':
                features_data = process_zip(file.file)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        for feature_data in features_data:
            geom = feature_data['geometry']
            shapely_geom = shape(geom) if isinstance(geom, dict) else geom
            geojson_geom = mapping(shapely_geom)
            properties = json.dumps(feature_data['properties'])
            new_feature = Feature(
                layer_id=form_model.layer_id,
                feature_name=feature_data['properties'].get('name', 'COUNTRY') if extension == 'kmz' else feature_data['properties'].get('VARNAME_1', 'COUNTRY'),
                properties=properties,
                geom=from_shape(shapely_geom, srid=4326),
            )
            db.add(new_feature)
            db.commit()
            db.refresh(new_feature)
            feature_ids.append(new_feature)
    
    else:
        if form_model.layer_community_id:
            print("dòng layercommunity này chạy nè")
            features_to_copy = db.query(Feature).filter(Feature.layer_id == form_model.layer_community_id).all()
            if not features_to_copy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No features found for the given layer_community_id")
            
            for feature in features_to_copy:
                new_feature = Feature(
                    layer_id=form_model.layer_id,
                    feature_name=feature.feature_name,
                    properties=feature.properties,
                    geom=feature.geom
                )
                db.add(new_feature)
                db.commit()
                db.refresh(new_feature)
                feature_ids.append(new_feature)
        
        else:
            print("dòng feature này chạy nè")
            feature_to_copy = db.query(Feature).filter(Feature.feature_id == form_model.feature_community_id).first()
            if not feature_to_copy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found for the given feature_community_id")
            
            new_feature = Feature(
                layer_id=form_model.layer_id,
                feature_name=feature_to_copy.feature_name,
                properties=feature_to_copy.properties,
                geom=feature_to_copy.geom
            )
            db.add(new_feature)
            db.commit()
            db.refresh(new_feature)
            feature_ids.append(new_feature)
        
    return {
        "message": "Add features to user kayer successfully",
        "layer_id": form_model.layer_id,
        "feature_count": len(feature_ids),
        "features": [
            {
                "feature_id": feature.feature_id,
                "layer_id": feature.layer_id,
                "name": feature.feature_name,
                "properties": feature.properties,
                "geom": mapping(to_shape(feature.geom))
            }
            for feature in feature_ids
        ]
    }
  
@router.post("/draw-features")
async def save_draw_features(
    features: List[DrawFeatureItem],
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)

    saved_features = []

    for item in features:
        layer = db.query(Layer).filter(Layer.layer_id == item.layer_id).first()
        if not layer:
            raise HTTPException(status_code=404, detail=f"Layer {item.layer_id} not found")

        feature_geojson = item.feature
        geometry = feature_geojson.get("geometry")
        properties = None
        if not geometry:
            raise HTTPException(status_code=400, detail="Feature geometry is missing")

        try:
            shapely_geom = shape(geometry)
            geom_db = from_shape(shapely_geom, srid=4326)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid geometry: {e}")

        new_feature = Feature(
            layer_id=item.layer_id,
            feature_name='No named',
            properties=json.dumps(properties),
            geom=geom_db,
        )

        db.add(new_feature)
        db.commit()
        db.refresh(new_feature)

        saved_features.append({
            "feature_id": new_feature.feature_id,
            "layer_id": new_feature.layer_id
        })

    return saved_features