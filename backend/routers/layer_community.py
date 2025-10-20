from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.layer_community import LayerCommunity
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import base64
from datetime import datetime

router = APIRouter(prefix="/layer_community", tags=["layer_community"])

class LayerCommunityCreate(BaseModel):
    layer_id: int
    layer_community_name: str
    layer_community_description: Optional[str] = None
    access_rights: str
    layer_community_image: str

class LayerCommunityUpdate(BaseModel):
    layer_community_name: Optional[str] = None
    layer_community_description: Optional[str] = None
    access_rights: Optional[str] = None
    layer_community_image: Optional[str] = None

class LayerCommunityResponse(BaseModel):
    layer_community_id: int
    layer_id: int
    user_id: int
    layer_community_name: str
    layer_community_description: Optional[str] = None
    status: bool
    access_rights: str
    created_at: datetime
    updated_at: datetime
    layer_community_image: Optional[str] = None

    class Config:
        orm_mode = True

class LayerCommunityIdsRequest(BaseModel):
    layer_community_ids: List[int]

@router.post("/", response_model=LayerCommunityResponse)
async def create_layer_community(layer_community: LayerCommunityCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    if layer_community.access_rights not in ["Public", "Restricted"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="access_rights must be 'Public' or 'Restricted'")

    layer_community_data = layer_community.dict(exclude_unset=True)
    base64_string = layer_community_data.pop("layer_community_image")
    
    # Loại bỏ tiền tố base64 nếu có (ví dụ: data:image/jpeg;base64,)
    if base64_string and base64_string.startswith("data:image"):
        base64_string = base64_string.split(",")[1]
    
    try:
        layer_community_image = base64.b64decode(base64_string)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")

    db_layer_community = LayerCommunity(user_id=user_id, layer_community_image=layer_community_image, **layer_community_data)
    db.add(db_layer_community)
    db.commit()
    db.refresh(db_layer_community)
    if db_layer_community.layer_community_image:
        db_layer_community.layer_community_image = base64.b64encode(db_layer_community.layer_community_image).decode('utf-8')
    return db_layer_community

@router.get("/", response_model=List[LayerCommunityResponse])
async def get_all_layer_communities(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    layer_communities = db.query(LayerCommunity).filter(
        LayerCommunity.status == True,
        LayerCommunity.access_rights == "Public"
    ).all()
    response = []
    if not layer_communities:
        return response
    
    for layer_community in layer_communities:
        layer_community_data = {
            "layer_community_id": layer_community.layer_community_id,
            "layer_id": layer_community.layer_id,
            "user_id": layer_community.user_id,
            "layer_community_name": layer_community.layer_community_name,
            "layer_community_description": layer_community.layer_community_description,
            "status": layer_community.status,
            "access_rights": layer_community.access_rights,
            "created_at": layer_community.created_at,
            "updated_at": layer_community.updated_at
        }
        if layer_community.layer_community_image:
            layer_community_data["layer_community_image"] = base64.b64encode(layer_community.layer_community_image).decode('utf-8')
        response.append(layer_community_data)
    return response
@router.get("/by-user", response_model=List[LayerCommunityResponse])
async def get_layer_communities_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    print(type(user_id))
    layer_communities = db.query(LayerCommunity).filter(
        LayerCommunity.user_id == user_id,
        LayerCommunity.status == True,
    ).all()
    response = []
    if not layer_communities:
        return response
    
    for layer_community in layer_communities:
        layer_community_data = {
            "layer_community_id": layer_community.layer_community_id,
            "layer_id": layer_community.layer_id,
            "user_id": layer_community.user_id,
            "layer_community_name": layer_community.layer_community_name,
            "layer_community_description": layer_community.layer_community_description,
            "status": layer_community.status,
            "access_rights": layer_community.access_rights,
            "created_at": layer_community.created_at,
            "updated_at": layer_community.updated_at
        }
        if layer_community.layer_community_image:
            layer_community_data["layer_community_image"] = base64.b64encode(layer_community.layer_community_image).decode('utf-8')
        response.append(layer_community_data)
    return response
@router.get("/by-user-delete", response_model=List[LayerCommunityResponse])
async def get_layer_communities_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    layer_communities = db.query(LayerCommunity).filter(
        LayerCommunity.user_id == user_id,
        LayerCommunity.status == False,
    ).all()
    if not layer_communities:
        return []
    
    response = []
    for layer_community in layer_communities:
        layer_community_data = {
            "layer_community_id": layer_community.layer_community_id,
            "layer_id": layer_community.layer_id,
            "user_id": layer_community.user_id,
            "layer_community_name": layer_community.layer_community_name,
            "layer_community_description": layer_community.layer_community_description,
            "status": layer_community.status,
            "access_rights": layer_community.access_rights,
            "created_at": layer_community.created_at,
            "updated_at": layer_community.updated_at
        }
        if layer_community.layer_community_image:
            layer_community_data["layer_community_image"] = base64.b64encode(layer_community.layer_community_image).decode('utf-8')
        response.append(layer_community_data)
    return response

@router.get("/{layer_community_id}", response_model=int)
async def get_layer_id_by_community_id(layer_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    layer_community = db.query(LayerCommunity).filter(
        LayerCommunity.layer_community_id == layer_community_id,
        LayerCommunity.status == True,
    ).first()
    
    if not layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Layer community with id {layer_community_id} not found or not accessible")
    
    return layer_community.layer_id

@router.post("/by-ids", response_model=List[LayerCommunityResponse])
async def get_layer_communities_by_ids(request: LayerCommunityIdsRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not request.layer_community_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="layer_community_ids cannot be empty")

    layer_communities = db.query(LayerCommunity).filter(
        LayerCommunity.layer_community_id.in_(request.layer_community_ids),
        LayerCommunity.status == True,
        LayerCommunity.access_rights == "Public"
    ).all()
    if not layer_communities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No public layer communities found for the provided IDs")
    
    response = []
    for layer_community in layer_communities:
        layer_community_data = {
            "layer_community_id": layer_community.layer_community_id,
            "layer_id": layer_community.layer_id,
            "user_id": layer_community.user_id,
            "layer_community_name": layer_community.layer_community_name,
            "layer_community_description": layer_community.layer_community_description,
            "status": layer_community.status,
            "access_rights": layer_community.access_rights,
            "created_at": layer_community.created_at,
            "updated_at": layer_community.updated_at
        }
        if layer_community.layer_community_image:
            layer_community_data["layer_community_image"] = base64.b64encode(layer_community.layer_community_image).decode('utf-8')
        response.append(layer_community_data)
    return response

@router.put("/{layer_community_id}", response_model=LayerCommunityResponse)
async def update_layer_community(layer_community_id: int, layer_community: LayerCommunityUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    db_layer_community = db.query(LayerCommunity).filter(LayerCommunity.layer_community_id == layer_community_id, LayerCommunity.user_id == user_id).first()
    if not db_layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found")

    layer_community_data = layer_community.dict(exclude_unset=True)
    if "access_rights" in layer_community_data and layer_community_data["access_rights"] not in ["Public", "Restricted"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="access_rights must be 'Public' or 'Restricted'")
    if "layer_community_image" in layer_community_data:
        base64_string = layer_community_data.pop("layer_community_image")
        if base64_string and base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]
        try:
            db_layer_community.layer_community_image = base64.b64decode(base64_string) if base64_string else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")
    
    for key, value in layer_community_data.items():
        setattr(db_layer_community, key, value)

    try:
        db.commit()
        db.refresh(db_layer_community)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    if db_layer_community.layer_community_image:
        db_layer_community.layer_community_image = base64.b64encode(db_layer_community.layer_community_image).decode('utf-8')
    return db_layer_community

@router.patch("/{layer_community_id}")
async def deactivate_layer_community(layer_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    db_layer_community = db.query(LayerCommunity).filter(LayerCommunity.layer_community_id == layer_community_id, LayerCommunity.user_id == user_id).first()
    if not db_layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found")

    db_layer_community.status = False
    try:
        db.commit()
        db.refresh(db_layer_community)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return {"message": "Layer community deactivated successfully"}

@router.delete("/{layer_community_id}")
async def delete_layer_community(layer_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    db_layer_community = db.query(LayerCommunity).filter(LayerCommunity.layer_community_id == layer_community_id, LayerCommunity.user_id == user_id).first()
    if not db_layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found")

    db.delete(db_layer_community)
    db.commit()
    return {"message": "Layer community deleted successfully"}