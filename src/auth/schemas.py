import uuid

from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    age: int

    class Config:
        orm_mode = True


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class UserCreateSchema(UserBaseSchema):
    password: str
    password_confirm: str
    is_active: bool = True
    is_superuser: bool = False


class UserResponse(UserBaseSchema):
    user_id: uuid.UUID
