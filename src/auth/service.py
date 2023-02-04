from datetime import timedelta
from fastapi import Response, Request, Depends
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import bad_field, unauthorized, unauthorized_field
from .models import User
from .schemas import UserCreateSchema, LoginUserSchema
from .utils import hash_password, verify_password
from src.database import get_db
from src.config import settings
from src.auth.config import AuthJWT


async def require_user(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        user = await db.execute(select(User).filter_by(user_id=user_id))
        db_user_id = user.scalars().first()

        if not db_user_id:
            raise unauthorized("not registered", "User no longer exists")

    except Exception as error:
        jwt_error = error.__class__.__name__
        if jwt_error == "MissingTokenError":
            raise unauthorized("token", "You are not logged in")
        elif jwt_error == "JWTDecodeError" or jwt_error == "InvalidHeaderError":
            raise unauthorized("token", "Token does not exist")
        raise error

    return db_user_id


async def _create_user(user: UserCreateSchema, db: AsyncSession):
    async with db.begin():
        existing_user = await db.execute(select(User).filter(or_(
            User.email == EmailStr(user.email.lower()),
            User.username == user.username
        )))
        existing_user_result = existing_user.scalars().first()

        if existing_user_result:
            if existing_user_result.email != user.email.lower():
                raise bad_field("username", "Username already in use")
            elif existing_user_result.email == user.email.lower():
                raise bad_field("email", "Account already exist")

        if user.password != user.password_confirm:
            raise bad_field("password", "Passwords do not match")

        del user.password_confirm
        user.password = hash_password(user.password)
        user.email = EmailStr(user.email.lower())
        new_user = User(**user.dict())
        db.add(new_user)

    await db.refresh(new_user)
    return new_user


async def _login(user: LoginUserSchema, db: AsyncSession, response: Response, authorize: AuthJWT):
    existing = await db.execute(select(User).filter_by(email=user.email.lower()))
    existing_user = existing.scalars().first()

    if not existing_user:
        raise unauthorized_field("email", "This user does not exist")

    if not verify_password(user.password, existing_user.password):
        raise unauthorized_field("password", "The password is incorrect")

    access_token = authorize.create_access_token(subject=str(existing_user.user_id),
                                                 expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN))

    refresh_token = authorize.create_refresh_token(subject=str(existing_user.user_id),
                                                   expires_time=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN))

    response.set_cookie('access_token', access_token, settings.ACCESS_TOKEN_EXPIRES_IN * 60,
                        settings.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.set_cookie('refresh_token', refresh_token, settings.REFRESH_TOKEN_EXPIRES_IN * 60,
                        settings.REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.set_cookie('logged_in', 'True', settings.ACCESS_TOKEN_EXPIRES_IN * 60,
                        settings.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    return {'status': 'success', 'access_token': access_token}


async def _refresh(db: AsyncSession, response: Response, authorize: AuthJWT):
    try:
        authorize.jwt_refresh_token_required()
        user_id = authorize.get_jwt_subject()

        if not user_id:
            raise unauthorized("token", "Could not refresh access token")

        user = await db.execute(select(User).filter_by(user_id=user_id))

        if not user.scalars().first():
            raise unauthorized("not registered", "The user belonging to this token no logger exist")

        access_token = authorize.create_access_token(subject=user_id,
                                                     expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN))

        response.set_cookie('access_token', access_token, settings.ACCESS_TOKEN_EXPIRES_IN * 60,
                            settings.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

        response.set_cookie('logged_in', 'True', settings.ACCESS_TOKEN_EXPIRES_IN * 60,
                            settings.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

        return {"access_token": access_token}

    except Exception as error:
        if error.__class__.__name__ == "MissingTokenError":
            raise unauthorized("token", "Please provide refresh token")
        raise error


async def _logout(response: Response, authorize: AuthJWT):
    authorize.unset_jwt_cookies()
    response.set_cookie("logged_in", "False")
    return {'status': 'success'}
