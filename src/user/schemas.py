from typing import Optional

from pydantic import BaseModel, EmailStr
from beanie import Document

from src.user.security import hash_password, verify_password


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserInDB(Document):
    email: EmailStr
    hashed_password: str

    class Settings:
        name = 'users_collection'

    @classmethod
    async def create_user(cls, user_data: UserCreate) -> "UserInDB":
        hashed_password = hash_password(user_data.password)
        user = cls(email=user_data.email, hashed_password=hashed_password)
        await user.create()
        return user

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    @classmethod
    async def by_email(cls, email: str) -> Optional["UserInDB"]:
        return await cls.find_one(cls.email == email)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

