from fastapi import Depends, HTTPException, status, APIRouter, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.favourite_place import FavouritePlace
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
from datetime import datetime

router = APIRouter(prefix="/favourite-places", tags=["favourite_places"])

class FavouritePlaceCreate(BaseModel):
    place_id: str

class FavouritePlaceUpdate(BaseModel):
    user_id: int
    favourite_id: int
    place_id: str

class FavouritePlaceResponse(BaseModel):
    favourite_id: int
    place_id: str
    created_at: datetime

    class Config:
        from_attributes = True
        
@router.post("/", response_model=FavouritePlaceResponse)
async def create_favourite_place(favourite: str = Body(...), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    print(favourite)
    favourite_data = favourite
    db_favourite = FavouritePlace(user_id=user_id, place_id=favourite_data)
    db.add(db_favourite)
    try:
        db.commit()
        db.refresh(db_favourite)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return db_favourite

@router.get("/by-user", response_model=List[FavouritePlaceResponse])
async def get_favourite_places_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    favourites = db.query(FavouritePlace).filter(FavouritePlace.user_id == user_id).all()
    if not favourites:
        return []
    
    return favourites

@router.get("/{favourite_id}", response_model=FavouritePlaceResponse)
async def get_favourite_place(favourite_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    favourite = db.query(FavouritePlace).filter(
        FavouritePlace.favourite_id == favourite_id,
        FavouritePlace.user_id == user_id
    ).first()
    if favourite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favourite place not found")
    
    return favourite

@router.put("/{favourite_id}", response_model=FavouritePlaceResponse)
async def update_favourite_place(favourite_id: int, favourite_update: FavouritePlaceUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_favourite = db.query(FavouritePlace).filter(
        FavouritePlace.favourite_id == favourite_id,
        FavouritePlace.user_id == user_id
    ).first()
    if db_favourite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favourite place not found")
    
    for key, value in favourite_update.dict(exclude_unset=True).items():
        setattr(db_favourite, key, value)
    
    try:
        db.commit()
        db.refresh(db_favourite)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return db_favourite

@router.delete("/")
async def delete_favourite_place(place_id: str = Query(...), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_favourite = db.query(FavouritePlace).filter(
        FavouritePlace.place_id == place_id,
        FavouritePlace.user_id == user_id
    ).first()
    if db_favourite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favourite place not found")
    
    db.delete(db_favourite)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return {"message": "Favourite place deleted successfully"}