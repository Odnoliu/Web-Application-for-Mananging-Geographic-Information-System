from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.feature_community import FeatureCommunity
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import base64
from datetime import datetime

router = APIRouter(prefix="/feature_community", tags=["feature_community"])

class FeatureCommunityCreate(BaseModel):
    feature_id: int
    feature_community_name: str
    feature_community_description: Optional[str] = None
    access_rights: str
    feature_community_image: str

class FeatureCommunityUpdate(BaseModel):
    feature_community_name: Optional[str] = None
    feature_community_description: Optional[str] = None
    access_rights: Optional[str] = None
    feature_community_image: Optional[str] = None

class FeatureCommunityResponse(BaseModel):
    feature_community_id: int
    feature_id: int
    user_id: int
    feature_community_name: str
    feature_community_description: Optional[str] = None
    status: bool
    access_rights: str
    created_at: datetime
    updated_at: datetime
    feature_community_image: Optional[str] = None

    class Config:
        orm_mode = True

class FeatureCommunityIdsRequest(BaseModel):
    feature_community_ids: List[int]

@router.post("/", response_model=FeatureCommunityResponse)
async def create_feature_community(feature_community: FeatureCommunityCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    if feature_community.access_rights not in ["Public", "Restricted"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="access_rights must be 'Public' or 'Restricted'")

    feature_community_data = feature_community.dict(exclude_unset=True)
    base64_string = feature_community_data.pop("feature_community_image")
    
    # Loại bỏ tiền tố base64 nếu có (ví dụ: data:image/jpeg;base64,)
    if base64_string and base64_string.startswith("data:image"):
        base64_string = base64_string.split(",")[1]
    
    try:
        feature_community_image = base64.b64decode(base64_string)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")

    db_feature_community = FeatureCommunity(user_id=user_id, feature_community_image=feature_community_image, **feature_community_data)
    db.add(db_feature_community)
    db.commit()
    db.refresh(db_feature_community)
    if db_feature_community.feature_community_image:
        db_feature_community.feature_community_image = base64.b64encode(db_feature_community.feature_community_image).decode('utf-8')
    return db_feature_community

@router.get("/", response_model=List[FeatureCommunityResponse])
async def get_all_feature_communities(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    feature_communities = db.query(FeatureCommunity).filter(
        FeatureCommunity.status == True,
        FeatureCommunity.access_rights == "Public"
    ).all()
    response = []
    if not feature_communities:
        return response
    
    
    for feature_community in feature_communities:
        feature_community_data = {
            "feature_community_id": feature_community.feature_community_id,
            "feature_id": feature_community.feature_id,
            "user_id": feature_community.user_id,
            "feature_community_name": feature_community.feature_community_name,
            "feature_community_description": feature_community.feature_community_description,
            "status": feature_community.status,
            "access_rights": feature_community.access_rights,
            "created_at": feature_community.created_at,
            "updated_at": feature_community.updated_at
        }
        if feature_community.feature_community_image:
            feature_community_data["feature_community_image"] = base64.b64encode(feature_community.feature_community_image).decode('utf-8')
        response.append(feature_community_data)
    return response

@router.get("/by-user", response_model=List[FeatureCommunityResponse])
async def get_feature_communities_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    feature_communities = db.query(FeatureCommunity).filter(
        FeatureCommunity.user_id == user_id,
        FeatureCommunity.status == True,
    ).all()
    response = []
    if not feature_communities:
        return response
    
    for feature_community in feature_communities:
        feature_community_data = {
            "feature_community_id": feature_community.feature_community_id,
            "feature_id": feature_community.feature_id,
            "user_id": feature_community.user_id,
            "feature_community_name": feature_community.feature_community_name,
            "feature_community_description": feature_community.feature_community_description,
            "status": feature_community.status,
            "access_rights": feature_community.access_rights,
            "created_at": feature_community.created_at,
            "updated_at": feature_community.updated_at
        }
        if feature_community.feature_community_image:
            feature_community_data["feature_community_image"] = base64.b64encode(feature_community.feature_community_image).decode('utf-8')
        response.append(feature_community_data)
    return response

@router.get("/by-user-delete", response_model=List[FeatureCommunityResponse])
async def get_feature_communities_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    feature_communities = db.query(FeatureCommunity).filter(
        FeatureCommunity.user_id == user_id,
        FeatureCommunity.status == False,
    ).all()
    if not feature_communities:
        return []
    
    response = []
    for feature_community in feature_communities:
        feature_community_data = {
            "feature_community_id": feature_community.feature_community_id,
            "feature_id": feature_community.feature_id,
            "user_id": feature_community.user_id,
            "feature_community_name": feature_community.feature_community_name,
            "feature_community_description": feature_community.feature_community_description,
            "status": feature_community.status,
            "access_rights": feature_community.access_rights,
            "created_at": feature_community.created_at,
            "updated_at": feature_community.updated_at
        }
        if feature_community.feature_community_image:
            feature_community_data["feature_community_image"] = base64.b64encode(feature_community.feature_community_image).decode('utf-8')
        response.append(feature_community_data)
    return response

@router.get("/{feature_community_id}", response_model=int)
async def get_layer_id_by_community_id(feature_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    feature_community = db.query(FeatureCommunity).filter(
        FeatureCommunity.feature_community_id == feature_community_id,
        FeatureCommunity.status == True,
    ).first()
    
    if not feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Layer community with id {feature_community_id} not found or not accessible")
    
    return feature_community.feature_id
@router.post("/by-ids", response_model=List[FeatureCommunityResponse])
async def get_feature_communities_by_ids(request: FeatureCommunityIdsRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not request.feature_community_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="feature_community_ids cannot be empty")

    feature_communities = db.query(FeatureCommunity).filter(
        FeatureCommunity.feature_community_id.in_(request.feature_community_ids),
        FeatureCommunity.status == True,
        FeatureCommunity.access_rights == "Public"
    ).all()
    if not feature_communities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No public feature communities found for the provided IDs")
    
    response = []
    for feature_community in feature_communities:
        feature_community_data = {
            "feature_community_id": feature_community.feature_community_id,
            "feature_id": feature_community.feature_id,
            "user_id": feature_community.user_id,
            "feature_community_name": feature_community.feature_community_name,
            "feature_community_description": feature_community.feature_community_description,
            "status": feature_community.status,
            "access_rights": feature_community.access_rights,
            "created_at": feature_community.created_at,
            "updated_at": feature_community.updated_at
        }
        if feature_community.feature_community_image:
            feature_community_data["feature_community_image"] = base64.b64encode(feature_community.feature_community_image).decode('utf-8')
        response.append(feature_community_data)
    return response

@router.put("/{feature_community_id}", response_model=FeatureCommunityResponse)
async def update_feature_community(feature_community_id: int, feature_community: FeatureCommunityUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    db_feature_community = db.query(FeatureCommunity).filter(FeatureCommunity.feature_community_id == feature_community_id, FeatureCommunity.user_id == user_id).first()
    if not db_feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature community not found")

    feature_community_data = feature_community.dict(exclude_unset=True)
    if "access_rights" in feature_community_data and feature_community_data["access_rights"] not in ["Public", "Restricted"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="access_rights must be 'Public' or 'Restricted'")
    if "feature_community_image" in feature_community_data:
        base64_string = feature_community_data.pop("feature_community_image")
        if base64_string and base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]
        try:
            db_feature_community.feature_community_image = base64.b64decode(base64_string) if base64_string else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")
    
    for key, value in feature_community_data.items():
        setattr(db_feature_community, key, value)

    try:
        db.commit()
        db.refresh(db_feature_community)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    if db_feature_community.feature_community_image:
        db_feature_community.feature_community_image = base64.b64encode(db_feature_community.feature_community_image).decode('utf-8')
    return db_feature_community

@router.patch("/{feature_community_id}")
async def deactivate_feature_community(feature_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    db_feature_community = db.query(FeatureCommunity).filter(FeatureCommunity.feature_community_id == feature_community_id, FeatureCommunity.user_id == user_id).first()
    if not db_feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature community not found")

    db_feature_community.status = False
    try:
        db.commit()
        db.refresh(db_feature_community)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return {"message": "Feature community deactivated successfully"}

@router.delete("/{feature_community_id}")
async def delete_feature_community(feature_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    db_feature_community = db.query(FeatureCommunity).filter(FeatureCommunity.feature_community_id == feature_community_id, FeatureCommunity.user_id == user_id).first()
    if not db_feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature community not found")

    db.delete(db_feature_community)
    db.commit()
    return {"message": "Feature community deleted successfully"}