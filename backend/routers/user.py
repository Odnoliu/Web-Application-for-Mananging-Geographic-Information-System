from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from model.users import User
from utils.utils import get_current_user, oauth2_scheme
from model.connect import get_db
import base64

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/image")
async def get_user_image(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    response = {}
    if user.user_image:
        response["user_image"] = base64.b64encode(user.user_image).decode('utf-8')
    else:
        response["user_image"] = None
    response["avatar"] = user.avatar
    return response

@router.get("/profile")
async def get_user_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

@router.get("/check_role")
async def check_role(token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    if current_user['role'] == "Admin role":
        return {"role": current_user['role'], "message": "Admin"}
    else:
        if current_user["role"] == "User role":
            return {"role": current_user['role'], "message": "User role"}
        else:
            raise HTTPException(status_code=403, detail="User role is not valid")
        
@router.get("/all", response_model=list[dict])
async def get_all_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    users = db.query(User).all()
    if not users:
        return []
    
    return [{
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "user_image": base64.b64encode(user.user_image).decode('utf-8') if user.user_image else None,
        "avatar": user.avatar
    } for user in users]