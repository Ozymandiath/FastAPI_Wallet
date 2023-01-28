from fastapi import status, HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import bad_field
from .models import User
from .schemas import UserCreateSchema
from .utils import hash_password


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
