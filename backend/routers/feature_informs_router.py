from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from model.feature_informs import FeatureInforms
from model.connect import get_db
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/feature_informs", tags=["feature_informs"])

# Pydantic model for request validation
class FeatureInformCreate(BaseModel):
    feature_id: int
    title: str
    content: str

class FeatureInformUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# Create a new feature inform
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_feature_inform(
    inform: FeatureInformCreate,
    db: Session = Depends(get_db)
):
    new_inform = FeatureInforms(
        feature_id=inform.feature_id,
        title=inform.title,
        content=inform.content
    )
    db.add(new_inform)
    db.commit()
    db.refresh(new_inform)
    return {
        "informs_id": new_inform.inform_id,
        "feature_id": new_inform.feature_id,
        "title": new_inform.title,
        "content": new_inform.content
    }

# Get all feature informs by feature_id
@router.get("/{feature_id}")
async def get_feature_informs(
    feature_id: int,
    db: Session = Depends(get_db)
):
    informs = db.query(FeatureInforms).filter(FeatureInforms.feature_id == feature_id).all()
    if not informs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feature informs found for this feature_id"
        )
    
    return [{
        "informs_id": inform.inform_id,
        "feature_id": inform.feature_id,
        "title": inform.title,
        "content": inform.content
    } for inform in informs]
@router.post("/by_feature_ids")
async def get_feature_informs_by_ids(
    feature_ids: List[int],
    db: Session = Depends(get_db)
):
    if not feature_ids:
        return []
    
    informs = db.query(FeatureInforms).filter(FeatureInforms.feature_id.in_(feature_ids)).all()
    if not informs:
        return []
    
    return [{
        "informs_id": inform.inform_id,
        "feature_id": inform.feature_id,
        "title": inform.title,
        "content": inform.content
    } for inform in informs]
# Update a feature inform by informs_id
@router.put("/{informs_id}")
async def update_feature_inform(
    informs_id: int,
    inform_update: FeatureInformUpdate,
    db: Session = Depends(get_db)
):
    inform = db.query(FeatureInforms).filter(FeatureInforms.inform_id== informs_id).first()
    if not inform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature inform not found"
        )
    
    update_data = inform_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inform, key, value)
    
    db.commit()
    db.refresh(inform)
    return {
        "informs_id": inform.inform_id,
        "feature_id": inform.feature_id,
        "title": inform.title,
        "content": inform.content
    }

# Delete a feature inform by informs_id
@router.delete("/{informs_id}")
async def delete_feature_inform(
    informs_id: int,
    db: Session = Depends(get_db)
):
    inform = db.query(FeatureInforms).filter(FeatureInforms.inform_id == informs_id).first()
    if not inform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature inform not found"
        )
    
    db.delete(inform)
    db.commit()
    return {"message": f"Feature inform with id {informs_id} deleted successfully"}