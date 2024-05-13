from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, Field
from beanie import Document, PydanticObjectId

from src.user.security import hash_password, verify_password


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class TGUserCreate(BaseModel):
    telegram_id: int = Field(..., alias='id')
    first_name: str = Field(default=None, alias='first_name')
    username: str = Field(default=None, alias='username')
    photo_url: HttpUrl = Field(default=None, alias='photo_url')
    auth_date: str = Field(..., alias='auth_date')


class UserInDB(Document):
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None

    telegram_id: Optional[int] = None
    first_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: Optional[str] = None

    class Settings:
        name = 'users_collection'

    @classmethod
    async def create_user(cls, user_data: UserCreate) -> "UserInDB":
        hashed_password = hash_password(user_data.password)
        user = cls(email=user_data.email, hashed_password=hashed_password)
        await user.create()
        return user

    @classmethod
    async def create_tg_user(cls, user_data: TGUserCreate):
        user = cls(
            telegram_id=user_data.telegram_id,
            first_name=user_data.first_name,
            username=user_data.username,
            photo_url=user_data.photo_url,
            auth_date=user_data.auth_date
        )
        await user.create()
        return user

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    @classmethod
    async def by_user_id(cls, user_id: str) -> Optional["UserInDB"]:
        return await cls.find_one(cls.id == PydanticObjectId(user_id))

    @classmethod
    async def by_email(cls, email: str) -> Optional["UserInDB"]:
        return await cls.find_one(cls.email == email)
    
    @classmethod
    async def by_telegram_id(cls, telegram_id: int) -> Optional["UserInDB"]:
        return await cls.find_one(cls.telegram_id == telegram_id)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

