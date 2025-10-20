from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.connect import Base, SessionLocal
from model.projects import Project
from model.layers import Layer
from model.default_vector_layer_inform import DefaultVectorLayerInform
from model.layer_community import LayerCommunity
from model.feature_community import FeatureCommunity

app = FastAPI()

# Thiết lập logging
log_file_path = os.path.join(os.path.dirname(__file__), 'delete_inactive_records.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Hàm xóa các bản ghi không hoạt động quá 30 ngày
def delete_inactive_old_records():
    session = SessionLocal()
    
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        deleted_projects = session.query(Project).filter(
            Project.project_status == False,
            Project.updated_at < thirty_days_ago
        ).delete(synchronize_session=False)
        
        deleted_layers = session.query(Layer).filter(
            Layer.user_layer_status == False,
            Layer.updated_at < thirty_days_ago
        ).delete(synchronize_session=False)
        
        deleted_vector_informs = session.query(DefaultVectorLayerInform).filter(
            DefaultVectorLayerInform.status == False,
            DefaultVectorLayerInform.updated_at < thirty_days_ago
        ).delete(synchronize_session=False)
        
        deleted_layer_communities = session.query(LayerCommunity).filter(
            LayerCommunity.status == False,
            LayerCommunity.updated_at < thirty_days_ago
        ).delete(synchronize_session=False)
        
        deleted_feature_communities = session.query(FeatureCommunity).filter(
            FeatureCommunity.status == False,
            FeatureCommunity.updated_at < thirty_days_ago
        ).delete(synchronize_session=False)
        
        session.commit()
        
        logging.info(f"Deleted {deleted_projects} projects, {deleted_layers} layers, {deleted_vector_informs} vector informs, {deleted_layer_communities} layer communities, {deleted_feature_communities} feature communities")
        print(f"Deleted {deleted_projects} projects, {deleted_layers} layers, {deleted_vector_informs} vector informs, {deleted_layer_communities} layer communities, {deleted_feature_communities} feature communities successfully")
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        
    finally:
        session.close()
        
# Endpoint để xóa dữ liệu
@app.get("/delete-inactive")
async def delete_inactive():
    delete_inactive_old_records()
    return {"message": "Inactive records deleted successfully"}