from fastapi import APIRouter, FastAPI

from src.accounts.routes import router as accounts_router
from src.health.routes import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, prefix="/health")
api_router.include_router(accounts_router, prefix="/accounts")


app = FastAPI(
    title="Accountrix API",
    description="This is a simple API allowing user to perform CRUD operations on accounts.",
    contact={"email": "krzysztof.plonka64@gmail.com"},
)
app.include_router(api_router)
