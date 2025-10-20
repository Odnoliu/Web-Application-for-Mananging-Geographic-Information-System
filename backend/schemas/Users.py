from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    # user_image is handled separately via UploadFile, not included here

class UserResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    is_active: bool
    access_token: str

    class Config:
        orm_mode = True