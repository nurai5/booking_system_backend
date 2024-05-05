from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import BaseModel, Field

from src.facilities.schemas import MongoDBObjectId


class BookingItemCreate(BaseModel):
    facility_item_id: MongoDBObjectId
    start_time: datetime = Field(..., example="2024-03-12T03:00:00.000+00:00")
    end_time: datetime = Field(..., example="2024-03-12T04:30:00.000+00:00")


class BookingItemInDB(Document):
    facility_item_id: MongoDBObjectId
    start_time: datetime = Field(..., example="2024-03-12T03:00:00.000+00:00")
    end_time: datetime = Field(..., example="2024-03-12T04:30:00.000+00:00")

    class Settings:
        name = 'booking_items'


def individual_booking_item_serial(obj) -> dict:
    return {
        'id': str(obj['_id']),
        'facility_item_id': obj['facility_item_id'],
        'start_time': obj['start_time'],
        'end_time': obj['end_time'],
    }


def list_booking_item_serial(objs) -> list:
    return [individual_booking_item_serial(obj) for obj in objs]
