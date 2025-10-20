from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from model.default_vector_layer_inform import DefaultVectorLayerInform
from model.projects import Project
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
from datetime import datetime

router = APIRouter(prefix="/default-vector-layer-informs", tags=["default-vector-layer-informs"])

class DefaultVectorLayerInformCreate(BaseModel):
    project_id: int
    default_layer_id: int
    base: Optional[str] = None
    layer_name: Optional[str] = None

class DefaultVectorLayerInformCreateList(BaseModel):
    informs: List[DefaultVectorLayerInformCreate]

class DefaultVectorLayerInformUpdate(BaseModel):
    layer_name: Optional[str]
    fill: Optional[str] 
    stroke: Optional[str]
    stroke_width: Optional[int]

class DefaultVectorLayerInformResponse(BaseModel):
    project_id: int
    default_layer_id: int
    fill: Optional[str]
    stroke: Optional[str]
    stroke_width: Optional[int]
    z_index: Optional[int]
    created_at: datetime
    updated_at: datetime
    base: Optional[str]
    layer_name: Optional[str]

    class Config:
        orm_mode = True
class DefaultVectorLayerInformUpdateBase(BaseModel):
    project_id: int
    base: str
@router.post("/", response_model=List[DefaultVectorLayerInformResponse])
async def create_default_vector_layer_inform(
    data: DefaultVectorLayerInformCreateList,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    created_informs = []
    
    try:
        for inform in data.informs:
            # Verify project exists and belongs to user
            project = db.query(Project).filter(
                Project.project_id == inform.project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {inform.project_id} not found"
                )
            
            # Create new DefaultVectorLayerInform with default values
            db_inform = DefaultVectorLayerInform(
                project_id=inform.project_id,
                default_layer_id=inform.default_layer_id,
                base=inform.base,
                layer_name=inform.layer_name,
                fill="#1717CD",
                stroke="#000000",
                stroke_width=1,
                z_index=1
            )
            
            db.add(db_inform)
            db.commit()
            db.refresh(db_inform)
            created_informs.append(db_inform)
            
        return created_informs
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create default vector layer informs: {str(e)}"
        )

@router.get("/{project_id}/{default_layer_id}", response_model=DefaultVectorLayerInformResponse)
async def get_default_vector_layer_inform(
    project_id: int,
    default_layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    inform = db.query(DefaultVectorLayerInform).join(Project).filter(
        DefaultVectorLayerInform.project_id == project_id,
        DefaultVectorLayerInform.default_layer_id == default_layer_id,
        DefaultVectorLayerInform.status == True,
        Project.user_id == user_id
    ).first()
    if not inform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer inform not found")
    
    return inform
@router.get("/recycle", response_model=List[DefaultVectorLayerInformResponse])
async def get_recycled_default_vector_layer_informs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    # Lấy tất cả project_id của user có project_status = True
    project_ids = db.query(Project.project_id).filter(
        Project.user_id == user_id,
        Project.project_status == True
    ).all()
    project_ids = [pid[0] for pid in project_ids]
    
    if not project_ids:
        return []
    
    # Lấy tất cả DefaultVectorLayerInform từ các project có status = False
    layer_informs = db.query(DefaultVectorLayerInform).filter(
        DefaultVectorLayerInform.project_id.in_(project_ids),
        DefaultVectorLayerInform.status == False
    ).all()
    
    if not layer_informs:
        return []
    
    return layer_informs

@router.get("/{project_id}", response_model=list[DefaultVectorLayerInformResponse])
async def get_default_vector_layer_informs_by_project(
    project_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    layer_inform = db.query(DefaultVectorLayerInform).filter(DefaultVectorLayerInform.project_id == project_id, DefaultVectorLayerInform.status == True).all()
    if not layer_inform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer inform not found")
    
    return layer_inform

@router.put("/informs/{project_id}/{default_layer_id}", response_model=DefaultVectorLayerInformResponse)
async def update_default_vector_layer_inform(
    project_id: int,
    default_layer_id: int,
    inform: DefaultVectorLayerInformUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_inform = db.query(DefaultVectorLayerInform).join(Project).filter(
        DefaultVectorLayerInform.project_id == project_id,
        DefaultVectorLayerInform.default_layer_id == default_layer_id,
        Project.user_id == user_id
    ).first()

    if not db_inform:
        raise HTTPException(status_code=404, detail="Default vector layer inform not found")

    for key, value in inform.dict(exclude_unset=True).items():
        setattr(db_inform, key, value)
    
    db.commit()
    db.refresh(db_inform)
    return db_inform

@router.delete("/{project_id}/{default_layer_id}")
async def delete_default_vector_layer_inform(
    project_id: int,
    default_layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_inform = db.query(DefaultVectorLayerInform).join(Project).filter(
        DefaultVectorLayerInform.project_id == project_id,
        DefaultVectorLayerInform.default_layer_id == default_layer_id,
        Project.user_id == user_id
    ).first()
    if not db_inform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer inform not found")
    
    db.delete(db_inform)
    db.commit()
    return {"message": "Default vector layer inform deleted successfully"}

@router.put("/", response_model=List[DefaultVectorLayerInformResponse])
async def update_default_vector_layer_inform(
    data: DefaultVectorLayerInformUpdateBase,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    try:
        # Verify project exists and belongs to user
        project = db.query(Project).filter(
            Project.project_id == data.project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {data.project_id} not found"
            )

        # Find all DefaultVectorLayerInform records with matching project_id
        db_informs = db.query(DefaultVectorLayerInform).filter(
            DefaultVectorLayerInform.project_id == data.project_id
        ).all()

        if not db_informs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No DefaultVectorLayerInform records found for project ID {data.project_id}"
            )

        # Update base for all matching records
        for db_inform in db_informs:
            db_inform.base = data.base

        db.commit()

        # Refresh updated records
        updated_informs = []
        for db_inform in db_informs:
            db.refresh(db_inform)
            updated_informs.append(db_inform)

        return updated_informs

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update default vector layer informs: {str(e)}"
        )
        
@router.patch("/{project_id}/{default_layer_id}")
async def deactivate_default_vector_layer_inform(
    project_id: int,
    default_layer_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    
    db_inform = db.query(DefaultVectorLayerInform).join(Project).filter(
        DefaultVectorLayerInform.project_id == project_id,
        DefaultVectorLayerInform.default_layer_id == default_layer_id,
        Project.user_id == user_id
    ).first()
    if not db_inform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default vector layer inform not found")
    
    db_inform.status = False
    
    try:
        db.commit()
        db.refresh(db_inform)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    