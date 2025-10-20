from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/service_map", tags=["service_map"])

@router.get("/tourism", response_model=dict)
async def get_tourism_geojson():
    file_path = "geodata/Tourism.geojson"  # Đường dẫn tới file Tourism.geojson
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="File Tourism.geojson not found")

@router.get("/education", response_model=dict)
async def get_tourism_geojson():
    file_path = "geodata/Education.geojson"  # Đường dẫn tới file Tourism.geojson
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="File Education.geojson not found")

@router.get("/medical", response_model=dict)
async def get_tourism_geojson():
    file_path = "geodata/Medical.geojson"  # Đường dẫn tới file Tourism.geojson
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="File Medical.geojson not found")

@router.get("/market", response_model=dict)
async def get_tourism_geojson():
    file_path = "geodata/Market.geojson"  # Đường dẫn tới file Tourism.geojson
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="File Market.geojson not found")