from fastapi import APIRouter
from starlette.config import Config
import httpx
router = APIRouter(prefix="/news", tags=["news"])


config = Config(".env")

@router.get("/get_news")
async def get_gis_news():
    api_key = config("NEWSAPI_KEY")
    url = f"https://newsapi.org/v2/everything?q=GIS+geographic&apiKey={api_key}&language=en&sortBy=publishedAt"
    async with httpx.AsyncClient() as client:
        
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Cannot get news", "status_code": response.status_code}