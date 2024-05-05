from typing import Optional, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from src.user.schemas import UserInDB
from src.user.services import verify_token
from src.facilities.schemas import FacilityItemCreate, FacilityItemInDB, \
    FacilityItemType, FacilityItemDistrict

facilities_router = APIRouter()


@facilities_router.post('/facility-item', response_model=FacilityItemInDB)
async def create_facility_item(
        facility_item: FacilityItemCreate,
        user: UserInDB = Depends(verify_token)
):
    user_id = user.id
    facility_item_doc = await FacilityItemInDB.create_facility_item(
        facility_item_data=facility_item, user_id=str(user_id))
    return facility_item_doc


@facilities_router.get('/facility-item/{facility_item_id}', response_model=FacilityItemInDB)
async def get_facility_item(
    facility_item_id: str,
):
    facility_item_doc = await FacilityItemInDB.get(facility_item_id)
    return facility_item_doc


@facilities_router.get('/facility-items', response_model=List[FacilityItemInDB])
async def get_facility_items(
        item_type: Optional[FacilityItemType] = None,
        district: Optional[FacilityItemDistrict] = None
):
    search_criteria = {}
    if item_type:
        search_criteria['item_type'] = item_type.value
    if district:
        search_criteria['district'] = district.value

    facility_item_docs = await FacilityItemInDB.find(search_criteria).to_list()

    return facility_item_docs


@facilities_router.put('/facility-item/{facility_item_id}', response_model=FacilityItemInDB)
async def update_facility_item(
        facility_item_id: str,
        facility_item: FacilityItemCreate,
        # token: dict = Depends(verify_token)
):
    if not ObjectId.is_valid(facility_item_id):
        raise HTTPException(status_code=400, detail="Invalid facility item ID")

    facility_item_doc = await FacilityItemInDB.get(facility_item_id)
    if facility_item_doc is None:
        raise HTTPException(status_code=404, detail="Facility item not found")

    await facility_item_doc.set(facility_item.dict())

    return facility_item_doc


@facilities_router.delete('/facility-item/{facility_item_id}')
async def delete_facility_item(
        facility_item_id: str,
):
    if not ObjectId.is_valid(facility_item_id):
        raise HTTPException(status_code=400, detail="Invalid facility item ID")

    facility_item_doc = await FacilityItemInDB.find_one(
        FacilityItemInDB.id == ObjectId(facility_item_id)
    )

    if facility_item_doc is None:
        raise HTTPException(status_code=404, detail="Facility item not found")

    await facility_item_doc.delete()

    return {"message": "Facility item deleted successfully"}
