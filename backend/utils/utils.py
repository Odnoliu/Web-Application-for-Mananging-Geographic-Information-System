import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
import requests

config = Config(".env")
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth = OAuth(config)

# Đăng ký Google OAuth
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "consent",
        "issuer": "https://accounts.google.com",
    },
)

  # Đăng ký Facebook OAuth
oauth.register(
    name="facebook",
    client_id=config("FACEBOOK_CLIENT_ID"),
    client_secret=config("FACEBOOK_CLIENT_SECRET"),
    authorize_url="https://www.facebook.com/v12.0/dialog/oauth",
    access_token_url="https://graph.facebook.com/v12.0/oauth/access_token",
    userinfo_endpoint="https://graph.facebook.com/me?fields=id,name,email,picture",
    client_kwargs={"scope": "email"},
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="not-used", tokenUrl="not-used", auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": data.get("role", "User role")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username", '')
        email: str = payload.get("email", '')
        role: str = payload.get("role")
        if (username is '' and email is '') or role is None:
            raise credentials_exception
        return { 'user_id': user_id ,"email": email, "username": username, "role": role}
    except JWTError:
        raise credentials_exception

def get_user_role(db, user_id: int) -> str:
    from model.user_role import UserRole
    from model.roles import Role
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if user_role:
        role = db.query(Role).filter(Role.role_id == user_role.role_id).first()
        return role.name if role else "User role"
    return "User role"