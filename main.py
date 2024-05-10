from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.booking.routes import booking_router
from src.user.routes import auth_router
from src.core.db import init_db
from src.core.settings import debug
from src.facilities.routes import facilities_router

app = FastAPI(
    debug=debug,
    docs_url='/api/docs',
    title='FastAPI Booking System'
)

origins = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def app_lifecycle():
    async with app.router.lifespan_context() as ctx:
        await init_db()
        yield

app.include_router(auth_router, prefix='/api/user', tags=['user'])
app.include_router(facilities_router, prefix='/api/facilities', tags=['facilities'])
app.include_router(booking_router, prefix='/api/booking', tags=['booking'])
