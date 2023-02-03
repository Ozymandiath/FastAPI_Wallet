from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.config import AuthJWT

from src.database import get_db
from .schemas import UserCreateSchema, UserResponse, LoginUserSchema
from .service import _create_user, _login, _refresh, _logout

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


@router.get('/hello')
def hello(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"hello": "world"}


@router.get("/refresh")
async def refresh(request: Request,
                  response: Response,
                  authorize: AuthJWT = Depends(),
                  db: AsyncSession = Depends(get_db)) -> dict:
    return await _refresh(db, response, request, authorize)


@router.get("/logout")
async def logout(response: Response,
                 authorize: AuthJWT = Depends()):
    return await _logout(response, authorize)
