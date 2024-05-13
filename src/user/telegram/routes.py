from fastapi import Request
from fastapi.responses import HTMLResponse, FileResponse
from src.user.telegram.services import check_hash

from fastapi import APIRouter
from src.user.schemas import UserInDB, TGUserCreate
from src.user.services import generate_tokens

auth_router = APIRouter()


@auth_router.get("/telegram")
async def telegram_auth(request: Request):
    params = dict(request.query_params)
    try:
        if check_hash(data=params):
            user_data = TGUserCreate.model_validate(params)
            try:
                user = await UserInDB.by_telegram_id(telegram_id=user_data.telegram_id)

                if user is None:
                    user = await UserInDB.create_tg_user(user_data)

                access_token, refresh_token = await generate_tokens(subject=str(user.id))

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }

            except Exception as e:
                return {"message": "Error occurred", "data": str(e)}
    except:
        return {"message": "Access denied"}


@auth_router.get("/telegram_html", response_class=HTMLResponse)
async def telegram_auth_html():
    return FileResponse("src/templates/login.html")
