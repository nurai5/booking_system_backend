from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from src.user.schemas import UserCreate, Token, UserInDB
from src.user.services import insert_user, authenticate_user, create_access_token, get_user
from src.core.settings import secret_key, algorithm, access_token_expire_minutes, refresh_token_expire_minutes

auth_router = APIRouter()


@auth_router.post('/register', response_model=UserInDB)
async def register(user_create: UserCreate):
    try:
        user = await UserInDB.by_email(user_create.email)
        if user is not None:
            raise HTTPException(status_code=409, detail="User with that email already exists")
        await UserInDB.create_user(user_create)
        return {"msg": "User created successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=refresh_token_expire_minutes)

    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = await create_access_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await get_user(email=username)

    except JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=refresh_token_expire_minutes)

    access_token = await create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    refresh_token = await create_access_token(
        data={"sub": user['email']}, expires_delta=refresh_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# @auth_router.post('/register', response_model=UserInDB)
# async def register(user_create: UserCreate):