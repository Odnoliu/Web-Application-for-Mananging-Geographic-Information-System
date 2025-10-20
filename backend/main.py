from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, user, news, projects, layers, features, weather, default_vector_layer_inform_router, default_vector_layer_router, default_feature_router
from routers import default_feature_settings_router, feature_informs_router, feature_community, layer_community, community_access_control, service_map, check_in, favourite_place
from db_task_scheduler import delete_inactive_records
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import logging

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="26122004", 
    session_cookie="fastapi_session",
    max_age=3600
)

# Gắn các router
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(news.router)
app.include_router(projects.router)
app.include_router(layers.router)
app.include_router(features.router)
app.include_router(weather.router)
app.include_router(default_vector_layer_router.router)
app.include_router(default_vector_layer_inform_router.router)
app.include_router(default_feature_router.router)
app.include_router(default_feature_settings_router.router)
app.include_router(feature_informs_router.router)
app.include_router(feature_community.router)
app.include_router(layer_community.router)
app.include_router(community_access_control.router)
app.include_router(service_map.router)
app.include_router(check_in.router)
app.include_router(favourite_place.router)
# Cấu hình scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: requests.get("http://localhost:8000/delete-inactive"),
    'cron',
    hour=2,
    minute=0,
    second=0,
    timezone='Asia/Ho_Chi_Minh'
)

# Gọi endpoint khi server khởi động
@app.on_event("startup")
async def startup_event():
    try:
        requests.get("http://localhost:8001/delete-inactive")
        scheduler.start()
        print("Scheduler started. Running deletion job at 2:00 AM daily...")
    except Exception as e:
        print(f"Error during startup deletion: {str(e)}")

# Dừng scheduler khi server tắt
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}