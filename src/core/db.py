from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.booking.schemas import BookingItemInDB
from src.facilities.schemas import FacilityItemInDB
from src.user.schemas import UserInDB


async def init_db():
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    await init_beanie(database=client.booking_system, document_models=[
        UserInDB,
        FacilityItemInDB,
        BookingItemInDB,
    ]
                      )
