from fastapi import APIRouter, FastAPI

from src.health.routes import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, prefix="/health")


app = FastAPI()
app.include_router(api_router)
