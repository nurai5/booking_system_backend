from enum import Enum
from typing import Optional

from beanie import Document
from bson import ObjectId
from pydantic import BaseModel


class FacilityItemType(str, Enum):
    FOOTBALL = 'football'
    OTHER = 'other'


class FacilityItemDistrict(str, Enum):
    PERVOMAISKIY = 'Первомайский район'
    OKTYABRSKIY = 'Октябрьский район'
    SVERDLOVSKIY = 'Свердловский район'
    LENINSKIY = 'Ленинский район'


class MongoDBObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, current_handler):
        return {
            'type': 'string',
            'format': 'objectid',
            'examples': ['507f1f77bcf86cd799439011'],
        }


class FacilityItemCreate(BaseModel):
    item_type: FacilityItemType
    address: str
    district: FacilityItemDistrict
    phone: str
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    instagram: Optional[str] = None


class FacilityItemInDB(Document):
    item_type: FacilityItemType
    address: str
    district: FacilityItemDistrict
    phone: str
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    instagram: Optional[str] = None
    user_id: Optional[MongoDBObjectId] = None

    class Settings:
        name = 'facility_items_collection'

    @classmethod
    async def create_facility_item(
            cls, facility_item_data: FacilityItemCreate, user_id: str
    ) -> "FacilityItemInDB":
        facility_item_dict = facility_item_data.dict()
        facility_item_dict["user_id"] = user_id
        facility_item = cls(**facility_item_dict)
        await facility_item.create()
        return facility_item


def individual_facility_item_serial(obj) -> dict:
    return {
        'id': str(obj['_id']),
        'type': obj['type'],
        'address': obj['address'],
        'district': obj['district'],
        'phone': obj['phone'],
        'whatsapp': obj['whatsapp'],
        'telegram': obj['telegram'],
        'instagram': obj['instagram'],
        'user_id': obj['user_id'],
    }
