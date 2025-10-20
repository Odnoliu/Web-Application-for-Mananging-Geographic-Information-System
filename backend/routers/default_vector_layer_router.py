from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.default_vector_layer import DefaultVectorLayer
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme

router = APIRouter(prefix="/default-vector-layers", tags=["default-vector-layers"])

class DefaultVectorLayerCreate(BaseModel):
    default_layer_name: str

class DefaultVectorLayerUpdate(BaseModel):
    default_layer_name: Optional[str] = None

class DefaultVectorLayerResponse(BaseModel):
    default_layer_id: int
    default_layer_name: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

@router.post("/", response_model=DefaultVectorLayerResponse)
async def create_default_vector_layer(
    layer: DefaultVectorLayerCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    # Kiểm tra quyền user (giả định chỉ user có quyền tạo)
    if current_user.get("role") != "User role":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User access required")
    
    db_layer = DefaultVectorLayer(**layer.dict())
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer

@router.get("/{default_layer_id}", response_model=DefaultVectorLayerResponse)
async def get_default_vector_layer(
    default_layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    layer = db.query(DefaultVectorLayer).filter(DefaultVectorLayer.default_layer_id == default_layer_id).first()
    if not layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer not found")
    
    return layer

@router.get("/", response_model=List[DefaultVectorLayerResponse])
async def get_all_default_vector_layers(db: Session = Depends(get_db)):
    layers = db.query(DefaultVectorLayer).all()
    # Chuyển đổi dữ liệu
    response = [
        {
            "default_layer_id": layer.default_layer_id,
            "default_layer_name": layer.default_layer_name,
            "created_at": layer.created_at.isoformat() if layer.created_at else None,
            "updated_at": layer.updated_at.isoformat() if layer.updated_at else None
        }
        for layer in layers
    ]
    return response

@router.put("/{default_layer_id}", response_model=DefaultVectorLayerResponse)
async def update_default_vector_layer(
    default_layer_id: int,
    layer: DefaultVectorLayerUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    db_layer = db.query(DefaultVectorLayer).filter(DefaultVectorLayer.default_layer_id == default_layer_id).first()
    if not db_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer not found")
    
    for key, value in layer.dict(exclude_unset=True).items():
        setattr(db_layer, key, value)
    
    db.commit()
    db.refresh(db_layer)
    return db_layer

@router.delete("/{default_layer_id}")
async def delete_default_vector_layer(
    default_layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    db_layer = db.query(DefaultVectorLayer).filter(DefaultVectorLayer.default_layer_id == default_layer_id).first()
    if not db_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer not found")
    
    db.delete(db_layer)
    db.commit()
    return {"message": "Default vector layer deleted successfully"}