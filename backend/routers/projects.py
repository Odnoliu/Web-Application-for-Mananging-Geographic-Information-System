from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model import Project, ProjectType, DefaultVectorLayerInform, Layer
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import base64
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    project_name: str
    project_type: str
    project_img: Optional[str] = None

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    project_img: Optional[str] = None
    
# Model cho một item cập nhật priority
class PriorityUpdateItem(BaseModel):
    isDefault: bool
    layer_id: int
    priority: int

# Model cho toàn bộ request body
class PriorityUpdateRequest(BaseModel):
    updates: List[PriorityUpdateItem]
    
class PriorityUpdateResponseItem(BaseModel):
    isDefault: bool
    layer_id: int
    z_index: int 
    
class ProjectResponse(BaseModel):
    project_id: int
    project_name: str
    project_type: str
    created_at: datetime
    updated_at: datetime
    project_img: Optional[str] = None

    class Config:
        orm_mode = True
    
@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    project_data = project.dict(exclude_unset=True)
    project_img = base64.b64decode(project_data.pop("project_img")) if project_data.get("project_img") else None
    
    db_project = Project(user_id=user_id, project_img=project_img, **project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    if db_project.project_img:
        db_project.project_img = base64.b64encode(db_project.project_img).decode('utf-8')
    return db_project

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    response = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "project_type": project.project_type,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
    if project.project_img:
        response["project_img"] = base64.b64encode(project.project_img).decode('utf-8')
    return response

@router.get("/by-type/{project_type_id}", response_model=List[ProjectResponse])
async def get_projects_by_type(project_type_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    projects = db.query(Project).filter(
        Project.project_type == project_type_id,
        Project.user_id == user_id,
        Project.project_status == True
    ).all()
    
    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for this type")
    response = []
    for project in projects:
        project_data = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_type": project.project_type,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        if project.project_img:
            project_data["project_img"] = base64.b64encode(project.project_img).decode('utf-8')
        response.append(project_data)
    
    return response

@router.get("/recycle/{project_type_id}", response_model=List[ProjectResponse])
async def get_projects_by_type(project_type_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    projects = db.query(Project).filter(
        Project.project_type == project_type_id,
        Project.user_id == user_id,
        Project.project_status == False
    ).all()
    response = []
    if not projects:
        return response
    for project in projects:
        project_data = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_type": project.project_type,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        if project.project_img:
            project_data["project_img"] = base64.b64encode(project.project_img).decode('utf-8')
        response.append(project_data)
    
    return response

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    project_data = project.dict(exclude_unset=True)
    # Giải mã base64 thành byte nếu có project_img
    
    if "project_img" in project_data:
        base64_string = project_data.pop("project_img")
        # Loại bỏ prefix "data:image/png;base64," nếu có
        if base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]
        try:
            db_project.project_img = base64.b64decode(base64_string)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid base64 string: {str(e)}")
    else:
        db_project.project_img = None
    
    # Cập nhật các trường khác
    for key, value in project_data.items():
        setattr(db_project, key, value)
    
    # Lưu vào database
    try:
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
    # Chuyển project_img (byte) thành base64 string cho response
    if db_project.project_img:
        try:
            db_project.project_img = base64.b64encode(project.project_img).decode('utf-8')
        except Exception as e:
            db_project.project_img = None
    
    return db_project

@router.delete("/{project_id}")
async def delete_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.patch("/{project_id}")
async def deactivate_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db_project.project_status = False
    
    try:
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
@router.patch("/recycle/{project_id}")
async def deactivate_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == user_id).first()
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db_project.project_status = True
    
    try:
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
@router.patch(
    "/{project_id}/update-layer-priorities",
    response_model=List[PriorityUpdateResponseItem] # <-- 1. THAY ĐỔI RESPONSE MODEL
)
async def update_layer_priorities(
    project_id: int,
    request: PriorityUpdateRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Phần xác thực owner không thay đổi
    project_owner = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == user_id
    ).first()
    if not project_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found for this user."
        )
    
    response_data = [] # <-- 2. Chuẩn bị một mảng để chứa dữ liệu trả về

    try:
        for item in request.updates:
            # Phần logic cập nhật database không thay đổi
            if item.isDefault:
                db.query(DefaultVectorLayerInform).filter(
                    DefaultVectorLayerInform.project_id == project_id,
                    DefaultVectorLayerInform.default_layer_id == item.layer_id
                ).update({"z_index": item.priority})
            else:
                db.query(Layer).filter(
                    Layer.project_id == project_id,
                    Layer.layer_id == item.layer_id
                ).update({"z_index": item.priority})
            
            # 3. Thêm item đã xử lý vào mảng response
            response_data.append({
                "isDefault": item.isDefault,
                "layer_id": item.layer_id,
                "z_index": item.priority # z_index mới chính là priority được gửi lên
            })

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating priorities: {str(e)}"
        )

    return response_data # <-- 4. Trả về mảng dữ liệu thay vì message
    
    