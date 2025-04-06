from fastapi import APIRouter, FastAPI

from src.accounts.routes import router as accounts_router
from src.health.routes import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, prefix="/health")
api_router.include_router(accounts_router, prefix="/accounts")


app = FastAPI()
app.include_router(api_router)
