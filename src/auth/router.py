from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from .schemas import UserCreateSchema, UserResponse
from .service import _create_user

router = APIRouter()


@router.post("/")
async def create_user(user: UserCreateSchema, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await _create_user(user, db)
