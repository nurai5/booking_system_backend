from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# COMMON
debug = os.getenv('DEBUG')
secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')
access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
refresh_token_expire_minutes = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))

start_time_from_env = os.getenv("START_TIME")
end_time_from_env = os.getenv("END_TIME")

# DATABASE
db_client = os.getenv('MONGO_URI')
db_port = int(os.getenv('MONGO_PORT'))

db = {'users': 'users', 'facility_items': 'facility_items', 'booking': 'booking'}
# client = AsyncIOMotorClient('mongodb://localhost:27017')
# db = client.test

collection_users = db['users']
# db_field_owners = db['field_owners']
collection_facility_items = db['facility_items']
collection_bookings = db['booking']


# async def create_indexes():
#     await collection_users.create_index([('email', 1)], unique=True)
#
#
# async def create_booking_indexes():
#     await collection_bookings.create_index([('facility_item_id', 1)])
#     await collection_bookings.create_index([('start_time', 1), ('end_time', 1)])
