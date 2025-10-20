from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from starlette.config import Config

router = APIRouter(prefix="/weather", tags=["news"])

config = Config(".env")

class Coordinates(BaseModel):
    lat: float
    lon: float

OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY')  
@router.post("/get_weather")
async def get_weather(coords: Coordinates):
    async with httpx.AsyncClient() as client:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={coords.lat}&lon={coords.lon}&lang=en&units=metric&appid={OPENWEATHER_API_KEY}"
            print(url)
            response = await client.get(url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error fetching weather data")
            
            data = response.json()
            print(data)
            return {
                "city": data.get("name", "Unknown"),
                "country": data.get("sys", {}).get("country", "Unknown"),
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"],
                "sea_level": data['main']['sea_level']
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))