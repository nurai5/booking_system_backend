from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.user.services import verify_token
from src.booking.dependencies import validate_booking_times, check_booking_overlap
from src.booking.schemas import BookingItemInDB, BookingItemCreate
from src.booking.services import get_default_time_slots
from src.facilities.schemas import FacilityItemDistrict, FacilityItemInDB, \
    MongoDBObjectId

booking_router = APIRouter()


@booking_router.post('/booking-item', response_model=BookingItemInDB)
async def create_booking_item(
        booking_item: BookingItemCreate = Depends(validate_booking_times),
        # token: dict = Depends(verify_token)
):
    facility_item_doc = await FacilityItemInDB.get(booking_item.facility_item_id)

    if not facility_item_doc:
        raise HTTPException(status_code=404, detail="Facility item not found")

    overlap = await check_booking_overlap(booking_item)
    if overlap:
        raise HTTPException(status_code=400, detail="Booking overlaps with existing booking")

    booking_item_doc = await BookingItemInDB(**booking_item.dict()).create()
    return booking_item_doc


@booking_router.get('/schedule/')
async def get_schedule(
        date: Optional[datetime] = Query(None, example="2024-03-12"),
        district: Optional[FacilityItemDistrict] = None
        # token: dict = Depends(verify_token)
):
    if date is None:
        date = datetime.now()
    filters = {}
    if district:
        filters['district'] = district.value

    result = []
    facility_item_docs = await FacilityItemInDB.find(filters).to_list()

    facility_item_ids = [MongoDBObjectId.validate(item.id) for item in facility_item_docs]
    # facility_items_booking_objs = await BookingItemInDB.find({'facility_item_id': {'$in': facility_item_ids}}).to_list()

    for facility_item_doc in facility_item_docs:
        facility_booking_docs = await BookingItemInDB.find({'facility_item_id': MongoDBObjectId.validate(facility_item_doc.id)}).to_list()

        item_result = {}
        item_result['id'] = MongoDBObjectId.validate(facility_item_doc.id)
        item_result['type'] = facility_item_doc.item_type
        item_result['address'] = facility_item_doc.address
        item_result['district'] = facility_item_doc.district

        slots = get_default_time_slots(date)

        available_slots = []
        for start, end in slots:
            overlapping_bookings = [booking for booking in facility_booking_docs if
                                    booking.start_time < end and booking.end_time > start]
            if not overlapping_bookings:
                available_slots.append({
                    "id": None,
                    "start": start,
                    "end": end,
                    "available": True,
                })
            else:
                available_slots.append({
                    "id": MongoDBObjectId.validate(overlapping_bookings[0].id),
                    "start": start,
                    "end": end,
                    "available": False,
                })
        item_result['available_slots'] = available_slots

        result.append(item_result)

    return {"date": date, "facility_booking_docs": result}

