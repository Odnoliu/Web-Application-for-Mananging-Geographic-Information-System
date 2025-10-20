from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from model.connect import get_db
from model.default_feature_settings import DefaultFeatureSettings

# Pydantic models for request/response
class LayerFeatureInput(BaseModel):
    layer_id: int
    feature_ids: List[int]
    
class DefaultFeatureSettingCreateWithFeature(BaseModel):
    project_id: int
    default_layer_id: int
    feature_id: int
    default_feature_status: bool = True
    
class DefaultFeatureSettingCreateBulk(BaseModel):
    project_id: int
    layers: List[LayerFeatureInput]

class DefaultFeatureSettingUpdate(BaseModel):
    default_feature_status: bool

class DefaultFeatureSettingResponse(BaseModel):
    default_feature_id: int

# Router
router = APIRouter(prefix="/default-feature-settings", tags=["Default Feature Settings"])

@router.post("/")
async def create_default_feature_setting(setting: DefaultFeatureSettingCreateBulk, db: Session = Depends(get_db)):
    try:
        # Duyệt qua từng layer và feature_ids
        for layer in setting.layers:
            for feature_id in layer.feature_ids:
                # Tạo bản ghi DefaultFeatureSettings
                db_setting = DefaultFeatureSettings(
                    project_id=setting.project_id,
                    default_layer_id=layer.layer_id,
                    default_feature_id=feature_id,
                    default_feature_status=True  # Giá trị mặc định
                )
                db.add(db_setting)
                
        # Lưu tất cả bản ghi vào database
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    

@router.get("/", response_model=List[DefaultFeatureSettingResponse])
async def get_all_default_layer_ids(db: Session = Depends(get_db)):
    settings = db.query(DefaultFeatureSettings).all()
    return [{"default_layer_id": setting.default_layer_id} for setting in settings]

@router.get("/{project_id}", response_model=List[DefaultFeatureSettingResponse])
async def get_by_project_and_status(project_id: int, db: Session = Depends(get_db)):
    settings = db.query(DefaultFeatureSettings).filter(
        DefaultFeatureSettings.project_id == project_id,
        DefaultFeatureSettings.default_feature_status == True
    ).all()
    
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No settings found for this project with status True")
    
    return settings

@router.put("/{default_setting_id}", response_model=DefaultFeatureSettingResponse)
async def update_status(default_setting_id: int, update_data: DefaultFeatureSettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(DefaultFeatureSettings).filter(DefaultFeatureSettings.default_setting_id == default_setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.default_feature_status = update_data.default_feature_status
    db.commit()
    db.refresh(setting)
    return {"default_layer_id": setting.default_layer_id}

@router.delete("/{default_setting_id}", response_model=DefaultFeatureSettingResponse)
async def delete_setting(default_setting_id: int, db: Session = Depends(get_db)):
    setting = db.query(DefaultFeatureSettings).filter(DefaultFeatureSettings.default_setting_id == default_setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"default_layer_id": setting.default_layer_id}