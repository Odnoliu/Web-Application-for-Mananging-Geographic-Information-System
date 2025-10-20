from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.layers import Layer
from model.features import Feature
from model.projects import Project
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import json
from utils.file_processor import process_json, process_kmz, process_gpkg, process_zip
from shapely.geometry import shape, mapping
from shapely.wkt import dumps
from geoalchemy2.shape import from_shape, to_shape
from datetime import datetime

router = APIRouter(prefix="/layers", tags=["layers"])

class LayerCreate(BaseModel):
    project_id: int
    layer_name: str
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: Optional[int] = None
    z_index: Optional[int] = None
    layer_type: str

class LayerUpdate(BaseModel):
    layer_name: Optional[str]
    fill: Optional[str]
    stroke: Optional[str]
    stroke_width: Optional[int]

class LayerResponse(BaseModel):
    layer_id: Optional[int] = None
    project_id: Optional[int] = None
    layer_name: Optional[str] = None
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: Optional[int] = None
    z_index: Optional[int] = None
    layer_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] 
class RecycleLayerResponse(BaseModel):
    layer_id: Optional[int] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    layer_name: Optional[str] = None
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: Optional[int] = None
    z_index: Optional[int] = None
    layer_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
class UploadLayerForm(BaseModel):
    name: str
    fill_color: Optional[str] = None
    stroke_color: Optional[str] = None
    stroke_width: Optional[int] = None
    priority: int
    project_id: int
    layer_community_id: Optional[int] = None
    feature_community_id: Optional[int] = None

@router.get("/recycle", response_model=List[RecycleLayerResponse])
async def get_recycled_layers(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    results = (
        db.query(Layer, Project.project_name)
        .join(Project, Layer.project_id == Project.project_id)
        .filter(
            Project.user_id == user_id,
            Project.project_status == True,
            Layer.user_layer_status == False
        )
        .all()
    )
    
    if not results:
        return []
    
    # Format response
    return [{
        "layer_id": layer.layer_id,
        "project_id": layer.project_id,
        "project_name": project_name,   # ánh xạ thêm
        "layer_name": layer.layer_name,
        "fill": layer.fill,
        "stroke": layer.stroke,
        "stroke_width": layer.stroke_width,
        "z_index": layer.z_index,
        "layer_type": layer.layer_type,
        "created_at": layer.created_at,
        "updated_at": layer.updated_at
    } for layer, project_name in results]

@router.get("/{layer_id}", response_model=Optional[LayerResponse])
async def get_layer(layer_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    layer = db.query(Layer).filter(Layer.layer_id == layer_id, Layer.user_layer_status == True).first()
    if not layer:
        return None
    
    return {
        "layer_id": layer.layer_id,
        "project_id": layer.project_id,
        "layer_name": layer.layer_name,
        "fill": layer.fill,
        "stroke": layer.stroke,
        "stroke_width": layer.stroke_width,
        "z_index": layer.z_index,
        "layer_type": layer.layer_type,
        "created_at": layer.created_at,
        "updated_at": layer.updated_at
    }

@router.put("/{layer_id}", response_model=LayerResponse)
async def update_layer(layer_id: int, layer: LayerUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_layer = db.query(Layer).join(Project).filter(
        Layer.layer_id == layer_id,
        Project.user_id == user_id
    ).first()
    
    if not db_layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    for key, value in layer.dict(exclude_unset=True).items():
        setattr(db_layer, key, value)
    
    db.commit()
    db.refresh(db_layer)
    return db_layer

@router.delete("/{layer_id}")
async def delete_layer(layer_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_layer = db.query(Layer).join(Project).filter(Layer.layer_id == layer_id, Project.user_id == user_id).first()
    if not db_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    
    db.delete(db_layer)
    db.commit()
    return {"message": "Layer deleted successfully"}

@router.get("/projects/{project_id}", response_model=List[LayerResponse])
async def get_layers_by_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    print(project_id)
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    layers = db.query(Layer).filter(Layer.project_id == project_id, Layer.user_layer_status == True).all()
    return [{
        "layer_id": layer.layer_id,
        "project_id": layer.project_id,
        "layer_name": layer.layer_name,
        "fill": layer.fill,
        "stroke": layer.stroke,
        "stroke_width": layer.stroke_width,
        "z_index": layer.z_index,
        "layer_type": layer.layer_type,
        "created_at": layer.created_at,
        "updated_at": layer.updated_at
    } for layer in layers]

@router.post("/")
async def upload_layer(form: Optional[str] = Form(...), file: Optional[UploadFile] = File(None), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    try:
        form_data = json.loads(form)
        print(form_data)
        form_model = UploadLayerForm(**form_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid form data format")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    project = db.query(Project).filter(Project.project_id == form_model.project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    print(form_model)
    new_layer = Layer(
        project_id=form_model.project_id,
        layer_name=form_model.name,
        fill=form_model.fill_color,
        stroke=form_model.stroke_color,
        stroke_width=form_model.stroke_width,
        z_index=form_model.priority,
        layer_type='L001',
    )
    db.add(new_layer)
    db.commit()
    db.refresh(new_layer)
    layer_id = new_layer.layer_id
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
                db.delete(new_layer)
                db.commit()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")
        except Exception as e:
            db.delete(new_layer)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        for feature_data in features_data:
            geom = feature_data['geometry']
            shapely_geom = shape(geom) if isinstance(geom, dict) else geom
            geojson_geom = mapping(shapely_geom)
            properties = json.dumps(feature_data['properties'])
            new_feature = Feature(
                layer_id=layer_id,
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
                db.delete(new_layer)
                db.commit()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No features found for the given layer_community_id")
            
            for feature in features_to_copy:
                new_feature = Feature(
                    layer_id=layer_id,
                    feature_name=feature.feature_name,
                    properties=feature.properties,
                    geom=feature.geom
                )
                db.add(new_feature)
                db.commit()
                db.refresh(new_feature)
                feature_ids.append(new_feature)
        
        elif form_model.feature_community_id:
            print("dòng feature này chạy nè")
            feature_to_copy = db.query(Feature).filter(Feature.feature_id == form_model.feature_community_id).first()
            if not feature_to_copy:
                db.delete(new_layer)
                db.commit()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found for the given feature_community_id")
            
            new_feature = Feature(
                layer_id=layer_id,
                feature_name=feature_to_copy.feature_name,
                properties=feature_to_copy.properties,
                geom=feature_to_copy.geom
            )
            db.add(new_feature)
            db.commit()
            db.refresh(new_feature)
            feature_ids.append(new_feature)
        
        else:
            return {
                "message": "Layer created successfully",
                "layer": {
                    "id": new_layer.layer_id,
                    "name": new_layer.layer_name,
                    "fill": new_layer.fill,
                    "stroke": new_layer.stroke,
                    "stroke_width": new_layer.stroke_width,
                    "priority": new_layer.z_index,
                },
                "feature_count": 0,
                "features": []
            }
    return {
        "message": "Layer and features created successfully",
        "layer": {
            "id": new_layer.layer_id,
            "name": new_layer.layer_name,
            "fill": new_layer.fill,
            "stroke": new_layer.stroke,
            "stroke_width": new_layer.stroke_width,
            "priority": new_layer.z_index,
        },
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
  
@router.patch("/recycle/{layer_id}")
async def deactivate_layer(layer_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_layer = db.query(Layer).join(Project).filter(Layer.layer_id == layer_id, Project.user_id == user_id).first()
    if not db_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    
    db_layer.user_layer_status = True
    
    try:
        db.commit()
        db.refresh(db_layer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
@router.patch("/{layer_id}")
async def deactivate_layer(layer_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_layer = db.query(Layer).join(Project).filter(Layer.layer_id == layer_id, Project.user_id == user_id).first()
    if not db_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    
    db_layer.user_layer_status = False
    
    try:
        db.commit()
        db.refresh(db_layer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")