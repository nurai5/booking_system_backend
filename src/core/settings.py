from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# COMMON
DEBUG = os.getenv('DEBUG')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))
BASE_URL = os.getenv('BASE_URL')

START_TIME_FROM_ENV = os.getenv("START_TIME")
END_TIME_FROM_ENV = os.getenv("END_TIME")

# DATABASE
MONGO_URI = os.getenv('MONGO_URI')
MONGO_PORT = int(os.getenv('MONGO_PORT'))

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


# TELEGRAM BOT TOKEN
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
