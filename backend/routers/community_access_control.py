from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import aiosmtplib
from email.message import EmailMessage
import re
from model.community_access_control import CommunityAccessControl
from model.layer_community import LayerCommunity
from model.feature_community import FeatureCommunity
from model.connect import get_db
from utils.utils import get_current_user, oauth2_scheme
import base64

router = APIRouter(prefix="/community_access_control", tags=["community_access_control"])
# Cấu hình SMTP
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "systemgid2612@gmail.com"  # Thay bằng email của bạn
SMTP_PASSWORD = "xdcz wxcz axpk octi"  # Thay bằng mật khẩu ứng dụng Gmail
class AccessControlCreate(BaseModel):
    user_informs: List[str]
    layer_community_id: int = None
    feature_community_id: int = None
    
class AccessControlResponse(BaseModel):
    list_layer_id: List[dict]
    list_feature_id: List[dict]
    
def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
async def send_share_notification(to_email: str, user_name: str, data_type: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = "You have been shared new data on FID"
    message.set_content(
        f"Your friend {user_name} has just shared a new {data_type} with you.\n"
        "Please check and use it on the system. Have a great day!",
        subtype="plain"
    )
    message.add_alternative(
        f"""\
        <html>
            <body>
                <p>Your friend <strong>{user_name}</strong> has just shared a new {data_type} with you.</p>
                <p>Please check and use it on the system. Have a great day!</p>
            </body>
        </html>
        """,
        subtype="html"
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")  # Log lỗi, không làm gián đoạn endpoint
        
@router.post("/add-layer-access", response_model=List[dict])
async def add_layer_access_control(access_data: AccessControlCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    username = current_user.get('email') or current_user.get('username')
    if not access_data.layer_community_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="layer_community_id is required")

    # Kiểm tra xem layer_community_id có tồn tại và thuộc về user
    layer_community = db.query(LayerCommunity).filter(
        LayerCommunity.layer_community_id == access_data.layer_community_id,
        LayerCommunity.user_id == user_id
    ).first()
    if not layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found or not owned by user")

    # Kiểm tra access_rights
    if layer_community.access_rights != "Restricted":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Layer community must have Restricted access rights")

    response = []
    try:
        for user_inform in access_data.user_informs:
            if not user_inform:
                continue
            db_access = CommunityAccessControl(
                layer_community_id=access_data.layer_community_id,
                feature_community_id=None,
                user_informs=user_inform
            )
            db.add(db_access)
            response.append({
                "layer_community_id": access_data.layer_community_id,
                "user_informs": user_inform
            })
            if is_valid_email(user_inform):
                data_type = "layer"
                await send_share_notification(user_inform, username, data_type)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return response

@router.post("/add-feature-access", response_model=List[dict])
async def add_feature_access_control(access_data: AccessControlCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")
    username = current_user.get('email') or current_user.get('username')
    if not access_data.feature_community_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="feature_community_id is required")


    # Kiểm tra xem feature_community_id có tồn tại và thuộc về user
    feature_community = db.query(FeatureCommunity).filter(
        FeatureCommunity.feature_community_id == access_data.feature_community_id,
        FeatureCommunity.user_id == user_id
    ).first()
    if not feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature community not found or not owned by user")

    # Kiểm tra access_rights
    if feature_community.access_rights != "Restricted":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Feature community must have Restricted access rights")

    response = []
    try:
        for user_inform in access_data.user_informs:
            if not user_inform:
                continue
            db_access = CommunityAccessControl(
                layer_community_id=None,
                feature_community_id=access_data.feature_community_id,
                user_informs=user_inform
            )
            db.add(db_access)
            response.append({
                "feature_community_id": access_data.feature_community_id,
                "user_informs": user_inform
            })
            if is_valid_email(user_inform):
                data_type = "feature"
                await send_share_notification(user_inform, username, data_type)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return response
@router.get("/get-access-controls", response_model=AccessControlResponse)
async def get_access_controls(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_name = current_user.get("username")
    email = current_user.get("email")
    
    # Determine which field to use for filtering
    user_inform = user_name if user_name is not None else email
    if not user_inform:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User name or email is required")

    try:
        # Query to join tables and get layer_community data
        layer_communities = db.query(LayerCommunity).join(
            CommunityAccessControl,
            CommunityAccessControl.layer_community_id == LayerCommunity.layer_community_id
        ).filter(
            CommunityAccessControl.user_informs == user_inform,
            LayerCommunity.access_rights == 'Restricted',
            LayerCommunity.status == True
        ).distinct().all()

        # Query to join tables and get feature_community data
        feature_communities = db.query(FeatureCommunity).join(
            CommunityAccessControl,
            CommunityAccessControl.feature_community_id == FeatureCommunity.feature_community_id
        ).filter(
            CommunityAccessControl.user_informs == user_inform,
            FeatureCommunity.access_rights == 'Restricted'
        ).distinct().all()

        # Convert to list of dictionaries
        list_layer_id = []
        for lc in layer_communities:
            layer_data = {
                "layer_community_id": lc.layer_community_id,
                "layer_id": lc.layer_id,
                "user_id": lc.user_id,
                "layer_community_name": lc.layer_community_name,
                "layer_community_description": lc.layer_community_description,
                "status": lc.status,
                "access_rights": lc.access_rights,
                "created_at": lc.created_at.isoformat() if lc.created_at else None,
                "updated_at": lc.updated_at.isoformat() if lc.updated_at else None
            }
            if lc.layer_community_image:
                layer_data["layer_community_image"] = base64.b64encode(lc.layer_community_image).decode('utf-8')
            list_layer_id.append(layer_data)
            
        list_feature_id = []
        for fc in feature_communities:
            feature_data = {
                "feature_community_id": fc.feature_community_id,
                "feature_id": fc.feature_id,
                "user_id": fc.user_id,
                "feature_community_name": fc.feature_community_name,
                "feature_community_description": fc.feature_community_description,
                "status": fc.status,
                "access_rights": fc.access_rights,
                "created_at": fc.created_at.isoformat() if fc.created_at else None,
                "updated_at": fc.updated_at.isoformat() if fc.updated_at else None
            }
            if fc.feature_community_image:
                feature_data['feature_community_image'] = base64.b64encode(fc.feature_community_image).decode('utf-8')
            list_feature_id.append(feature_data)

        return {
            "list_layer_id": list_layer_id,
            "list_feature_id": list_feature_id
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
@router.get("/layer_community/{layer_community_id}", response_model=List[str])
async def get_user_informs_by_layer(layer_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Kiểm tra xem layer_community_id có thuộc về user không (nếu cần bảo mật)
    layer = db.query(LayerCommunity).filter(
        LayerCommunity.layer_community_id == layer_community_id,
        LayerCommunity.user_id == user_id
    ).first()

    if not layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found or not owned by user")

    # Lấy danh sách user_informs
    user_informs = db.query(CommunityAccessControl.user_informs).filter(
        CommunityAccessControl.layer_community_id == layer_community_id
    ).all()

    # Chuyển về list các string
    return [item[0] for item in user_informs]

@router.get("/feature_community/{feature_community_id}", response_model=List[str])
async def get_user_informs_by_layer(feature_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Kiểm tra xem layer_community_id có thuộc về user không (nếu cần bảo mật)
    feature = db.query(FeatureCommunity).filter(
        FeatureCommunity.feature_community_id == feature_community_id,
        FeatureCommunity.user_id == user_id
    ).first()

    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found or not owned by user")

    # Lấy danh sách user_informs
    user_informs = db.query(CommunityAccessControl.user_informs).filter(
        CommunityAccessControl.feature_community_id == feature_community_id
    ).all()

    # Chuyển về list các string
    return [item[0] for item in user_informs]

@router.delete("/delete-by-layer/{layer_community_id}")
async def delete_by_layer_community_id(layer_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Kiểm tra xem layer_community_id có tồn tại và thuộc về user
    layer_community = db.query(LayerCommunity).filter(
        LayerCommunity.layer_community_id == layer_community_id,
        LayerCommunity.user_id == user_id
    ).first()
    if not layer_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer community not found or not owned by user")

    try:
        deleted_count = db.query(CommunityAccessControl).filter(
            CommunityAccessControl.layer_community_id == layer_community_id
        ).delete(synchronize_session=False)
        db.commit()
        return {"message": f"Successfully deleted {deleted_count} access control records for layer_community_id {layer_community_id}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.delete("/delete-by-feature/{feature_community_id}")
async def delete_by_feature_community_id(feature_community_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = await get_current_user(token)
    user_id = current_user.get("user_id")

    # Kiểm tra xem feature_community_id có tồn tại và thuộc về user
    feature_community = db.query(FeatureCommunity).filter(
        FeatureCommunity.feature_community_id == feature_community_id,
        FeatureCommunity.user_id == user_id
    ).first()
    if not feature_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature community not found or not owned by user")

    try:
        deleted_count = db.query(CommunityAccessControl).filter(
            CommunityAccessControl.feature_community_id == feature_community_id
        ).delete(synchronize_session=False)
        db.commit()
        return {"message": f"Successfully deleted {deleted_count} access control records for feature_community_id {feature_community_id}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
