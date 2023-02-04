from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.config import AuthJWT

from src.database import get_db
from .schemas import UserCreateSchema, UserResponse, LoginUserSchema
from .service import require_user, _create_user, _login, _refresh, _logout

router = APIRouter()


@router.post("/register")
async def create_user(user: UserCreateSchema, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await _create_user(user, db)


@router.post("/login")
async def login(user: LoginUserSchema,
                response: Response,
                db: AsyncSession = Depends(get_db),
                authorize: AuthJWT = Depends()):
    return await _login(user, db, response, authorize)


@router.get("/refresh")
async def refresh(response: Response,
                  authorize: AuthJWT = Depends(),
                  db: AsyncSession = Depends(get_db)) -> dict:
    return await _refresh(db, response, authorize)


@router.get("/logout")
async def logout(response: Response,
                 authorize: AuthJWT = Depends(),
                 user_id: str = Depends(require_user)):
    return await _logout(response, authorize)


@router.get('/me')
def info(user_id: UserResponse = Depends(require_user)) -> UserResponse:
    return user_id
