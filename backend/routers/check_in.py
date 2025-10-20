from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.check_in import CheckIn
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import base64
from datetime import datetime

router = APIRouter(prefix="/check_in", tags=["check_in"])

class CheckInCreate(BaseModel):
    check_in_description: Optional[str] = None
    check_in_image: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    place_id: Optional[str] = None

class CheckInUpdate(BaseModel):
    check_in_description: Optional[str] = None
    check_in_image: Optional[str] = None  # vẫn là data URL ở PUT (frontend đã gửi đúng)
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    place_id: Optional[str] = None

class CheckInResponse(BaseModel):
    check_in_id: int
    check_in_description: Optional[str] = None
    check_in_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    place_id: Optional[str] = None
    class Config:
        from_attributes = True
        
@router.post("/", response_model=CheckInResponse)
async def create_check_in(check_in: CheckInCreate,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    check_in_data = check_in.dict(exclude_unset=True)
    print(check_in_data)
    base64_string = check_in_data.pop("check_in_image")
    check_in_image = None
    if base64_string and base64_string.startswith("data:image"):
        try:
            # Remove data URI prefix (e.g., "data:image/jpeg;base64,")
            base64_string = base64_string.split(",")[1]
            # Decode base64 to verify it's valid
            check_in_image = base64.b64decode(base64_string)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid base64 string: {str(e)}"
            )
    db_check_in = CheckIn(user_id=user_id, check_in_image=check_in_image, **check_in_data)
    db.add(db_check_in)
    
    try:
        db.commit()
        db.refresh(db_check_in)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    if db_check_in.check_in_image:
        db_check_in.check_in_image = base64.b64encode(db_check_in.check_in_image).decode('utf-8')
    
    return db_check_in

@router.get("/by-user", response_model=List[CheckInResponse])
async def get_check_ins_by_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    response = []
    check_ins = db.query(CheckIn).filter(CheckIn.user_id == user_id).all()
    if not check_ins:
        return response
    
    for check_in in check_ins:
        check_in_data = {
            "check_in_id": check_in.check_in_id,
            "user_id": check_in.user_id,
            "check_in_description": check_in.check_in_description,
            "created_at": check_in.created_at,
            "updated_at": check_in.updated_at,
            "longitude": check_in.longitude,
            "latitude": check_in.latitude,
        }
        if check_in.check_in_image:
            check_in_data["check_in_image"] = base64.b64encode(check_in.check_in_image).decode('utf-8')
        response.append(check_in_data)
    
    return response

@router.get("/{check_in_id}", response_model=CheckInResponse)
async def get_check_in(check_in_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    check_in = db.query(CheckIn).filter(
        CheckIn.check_in_id == check_in_id,
        CheckIn.user_id == user_id
    ).first()
    if check_in is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    
    if check_in.check_in_image:
        check_in.check_in_image = base64.b64encode(check_in.check_in_image).decode('utf-8')
    
    return check_in

@router.put("/{check_in_id}", response_model=CheckInResponse)
async def update_check_in(check_in_id: int, check_in_update: CheckInUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_check_in = db.query(CheckIn).filter(
        CheckIn.check_in_id == check_in_id,
        CheckIn.user_id == user_id
    ).first()
    if db_check_in is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    
    update_data = check_in_update.dict(exclude_unset=True)
    if "check_in_image" in update_data:
        base64_string = update_data.pop("check_in_image")
        if base64_string and base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]
        try:
            db_check_in.check_in_image = base64.b64decode(base64_string) if base64_string else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")
    
    for key, value in update_data.items():
        setattr(db_check_in, key, value)
    
    db_check_in.updated_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(db_check_in)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    if db_check_in.check_in_image:
        db_check_in.check_in_image = base64.b64encode(db_check_in.check_in_image).decode('utf-8')
    
    return db_check_in

@router.delete("/{check_in_id}")
async def delete_check_in(check_in_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_check_in = db.query(CheckIn).filter(
        CheckIn.check_in_id == check_in_id,
        CheckIn.user_id == user_id
    ).first()
    if db_check_in is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    
    db.delete(db_check_in)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    return {"message": "Check-in deleted successfully"}