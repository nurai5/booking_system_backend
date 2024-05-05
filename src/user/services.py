from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo.errors import DuplicateKeyError

from src.user.schemas import UserInDB, UserCreate
from src.user.security import hash_password, verify_password
from src.core.settings import db, secret_key, algorithm


async def insert_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    user_db = UserInDB(email=user.email, hashed_password=hashed_password)
    try:
        await db["users"].insert_one(user_db.dict())
        return user_db
    except DuplicateKeyError:
        raise DuplicateKeyError("Email already registered.")


async def get_user(email: str):
    user = await db["users"].find_one({"email": email})
    return user


async def authenticate_user(email: str, password: str):
    user = await UserInDB.by_email(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        expiration = payload.get("exp")
        if expiration and datetime.now(timezone.utc) > datetime.fromtimestamp(expiration, timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        user = await UserInDB.by_email(username)
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user
