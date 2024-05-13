from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo.errors import DuplicateKeyError

from src.user.schemas import UserInDB, UserCreate
from src.user.security import hash_password, verify_password
from src.core.settings import db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES


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


async def generate_tokens(subject: str) -> tuple[str, str]:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = await create_access_token(
        data={"sub": subject}, expires_delta=access_token_expires
    )
    refresh_token = await create_access_token(
        data={"sub": subject}, expires_delta=refresh_token_expires
    )

    return access_token, refresh_token


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        expiration = payload.get("exp")
        if expiration and datetime.now(timezone.utc) > datetime.fromtimestamp(expiration, timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")

        user = await UserInDB.by_user_id(user_id)
        if user is None:
            raise credentials_exception

    except JWTError as e:
        raise credentials_exception
    return user
