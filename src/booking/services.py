from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException

from src.booking.dependencies import check_booking_overlap
from src.booking.schemas import BookingItemInDB, individual_booking_item_serial
from src.core.settings import db, collection_bookings, start_time_from_env, end_time_from_env


async def insert_booking_item(
        booking_item: BookingItemInDB
):
    overlap = await check_booking_overlap(booking_item)
    if overlap:
        raise HTTPException(status_code=400, detail="Booking overlaps with existing booking")

    booking_item_db = BookingItemInDB(
        facility_item_id=booking_item.facility_item_id,
        start_time=booking_item.start_time,
        end_time=booking_item.end_time,
    )
    try:
        result = await db["booking"].insert_one(booking_item_db.dict())
        inserted_booking_item = await db["booking"].find_one({"_id": result.inserted_id})
        return inserted_booking_item
    except Exception as e:
        raise e


async def find_facility_bookings(
        facility_item_id: str,
        date: datetime
) -> List:
    items = []
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)

    facility_booking_docs = collection_bookings.find({
        "facility_item_id": facility_item_id,
        "start_time": {"$gte": start_of_day},
        "end_time": {"$lt": end_of_day}
    })

    async for item in facility_booking_docs:
        items.append(individual_booking_item_serial(item))

    return items


def get_default_time_slots(date: datetime) -> List:
    start_time = datetime.combine(date, datetime.strptime(start_time_from_env, '%H:%M').time())
    end_time = datetime.combine(date + timedelta(days=1), datetime.strptime(end_time_from_env, '%H:%M').time())

    slots = []
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + timedelta(minutes=30)
        slots.append((current_time, next_time))
        current_time = next_time

    return slots
