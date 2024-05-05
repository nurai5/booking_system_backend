from fastapi import HTTPException

from src.booking.schemas import BookingItemInDB, BookingItemCreate
from src.core.settings import db


def validate_booking_times(booking_item: BookingItemCreate) -> BookingItemCreate:
    if booking_item.start_time.minute not in {0, 30} or booking_item.start_time.second != 0:
        raise HTTPException(status_code=400, detail="start_time must match 30-minute intervals")
    if booking_item.end_time.minute not in {0, 30} or booking_item.end_time.second != 0:
        raise HTTPException(status_code=400, detail="end_time must match 30-minute intervals")
    if booking_item.end_time <= booking_item.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    return booking_item


async def check_booking_overlap(booking_item: BookingItemCreate):
    query = {
        "facility_item_id": booking_item.facility_item_id,
        "$or": [
            {"start_time": {"$lt": booking_item.end_time}, "end_time": {"$gt": booking_item.start_time}},
        ]
    }
    existing_booking = await BookingItemInDB.find_one(query)

    return existing_booking
