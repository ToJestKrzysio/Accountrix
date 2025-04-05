from fastapi import APIRouter

from src.common.schema import MessageResponse

router = APIRouter()


@router.get("/", description="Health check endpoint")
def health():
    return MessageResponse(message="OK")
