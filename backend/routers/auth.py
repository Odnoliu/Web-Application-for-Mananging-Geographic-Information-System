from fastapi import Depends, HTTPException, status, APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from model.users import User
from model.auth_providers import AuthProvider
from model.roles import Role
from model.user_role import UserRole
from schemas.Users import UserResponse, LoginRequest
from utils.utils import oauth, verify_password, create_access_token, get_user_role, hash_password
from model.connect import get_db
import requests


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/admin/login", response_model=dict)
async def admin_login_with_email(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role = get_user_role(db, user.user_id)
    if role != "Admin role":
        raise HTTPException(status_code=403, detail="Admin access required")
    access_token = create_access_token(data={"user_id": user.user_id, "email": None, "username": user.username, "role": role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/user/login", response_model=dict)
async def user_login_with_username(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role = get_user_role(db, user.user_id)
    if role != "User role":
        raise HTTPException(status_code=403, detail="User access required")
    access_token = create_access_token(data={"user_id": user.user_id, "email": None, "username": user.username, "role": role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/user/register", response_model=UserResponse)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    user_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(password)
    user_image_data = None
    if user_image:
        try:
            user_image_data = await user_image.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read image file: {str(e)}")

    new_user = User(
        username=username,
        user_image=user_image_data,
        password_hash=hashed_password,
        full_name=full_name,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    default_role = db.query(Role).filter(Role.name == "User role").first()
    if default_role:
        db.add(UserRole(user_id=new_user.user_id, role_id=default_role.role_id))
        db.commit()

    access_token = create_access_token(data={"user_id": new_user.user_id, "email": None, "username": new_user.username, "role": "User role"})
    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        access_token=access_token
    )

@router.get("/user/google")
async def user_login_google(request: Request):
    redirect_uri = "http://localhost:8000/auth/user/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/user/google/callback")
async def user_google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        id_token = token.get("id_token")
        if not id_token:
            raise HTTPException(status_code=400, detail="No id_token in token response")

        user_info = token.get("userinfo")
        print("User Info: ", user_info)
        access_gg_token = token.get("access_token")
        email = user_info.get("email")
        full_name = user_info.get("name")
        avatar = user_info.get("picture")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, full_name=full_name, avatar=avatar, is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            default_role = db.query(Role).filter(Role.name == "User role").first()
            if default_role:
                db.add(UserRole(user_id=user.user_id, role_id=default_role.role_id))
                db.commit()
            db.add(AuthProvider(user_id=user.user_id, provider_name="google", provider_user_id=user_info.get("sub"), access_token=access_gg_token))
            db.commit()
        else:
            auth_provider = db.query(AuthProvider).filter(AuthProvider.user_id == user.user_id, AuthProvider.provider_name == "google").first()
            if not auth_provider:
                db.add(AuthProvider(user_id=user.user_id, provider_name="google", provider_user_id=user_info.get("sub"), access_token=access_gg_token))
                db.commit()

        role = get_user_role(db, user.user_id)
        access_token = create_access_token(data={"user_id": user.user_id, "email": email, "username": None, "role": role})
        request.session["access_token"] = access_token
        return RedirectResponse(url=f"http://localhost:5173/home?access_token={access_token}")
    except Exception as e:
        return RedirectResponse(url=f"http://localhost:5173/home?error=Google OAuth failed: {str(e)}")

@router.get("/user/facebook")
async def user_login_facebook(request: Request):
    redirect_uri = "http://localhost:8000/auth/user/facebook/callback"
    return await oauth.facebook.authorize_redirect(request, redirect_uri)

@router.get("/user/facebook/callback")
async def user_facebook_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.facebook.authorize_access_token(request)
        access_fb_token = token.get("access_token")
        user_response = requests.get(
            f"https://graph.facebook.com/v12.0/me?fields=id,name,email,picture.type(large)&access_token={access_fb_token}"
        )
        user_info = user_response.json()
        print("User Info: ", user_info)
        email = user_info.get("email")
        full_name = user_info.get("name")
        avatar = user_info["picture"]["data"]["url"]
        print(avatar)
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, full_name=full_name, avatar=avatar, is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            default_role = db.query(Role).filter(Role.name == "User role").first()
            if default_role:
                db.add(UserRole(user_id=user.user_id, role_id=default_role.role_id))
                db.commit()
            db.add(AuthProvider(user_id=user.user_id, provider_name="facebook", provider_user_id=user_info.get("id"), access_token=access_fb_token))
            db.commit()
        else:
            auth_provider = db.query(AuthProvider).filter(AuthProvider.user_id == user.user_id, AuthProvider.provider_name == "facebook").first()
            if not auth_provider:
                db.add(AuthProvider(user_id=user.user_id, provider_name="facebook", provider_user_id=user_info.get("id"), access_token=access_fb_token))
                db.commit()

        role = get_user_role(db, user.user_id)
        access_token = create_access_token(data={"user_id": user.user_id, "email": email, "username": None, "role": role})
        request.session["access_token"] = access_token
        return RedirectResponse(url=f"http://localhost:5173/home?access_token={access_token}")
    except Exception as e:
        return RedirectResponse(url=f"http://localhost:5173/home?error=Facebook OAuth failed: {str(e)}")
    