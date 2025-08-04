# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pymongo import MongoClient
import motor.motor_asyncio
from info import MONGODB_URI

# --- Sync Client for visit/withdraw tracking ---
sync_client = MongoClient(MONGODB_URI)
sync_db = sync_client['videoplays']
sync_collection = sync_db['playscount']

def record_visit(user: int, count: int):
    existing = sync_collection.find_one({"user": user})
    if existing:
        sync_collection.update_one({"user": user}, {"$set": {"count": count}})
    else:
        sync_collection.insert_one({
            "user": user,
            "count": count,
            "withdraw": False
        })

def record_withdraw(user: int, withdraw: bool):
    sync_collection.update_one({"user": user}, {"$set": {"withdraw": withdraw}})

def get_count(user: int):
    data = sync_collection.find_one({"user": user})
    return data.get("count") if data else None

def get_withdraw(user: int):
    data = sync_collection.find_one({"user": user})
    return data.get("withdraw", False) if data else False

# --- Async User Database (shared logic for both bots) ---
class BaseDatabase:

    def __init__(self, uri: str, db_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[db_name]
        self.col = self.db.users

    def new_user(self, id: int, name: str) -> dict:
        return {
            "id": id,
            "name": name,
            "b_name": None,
            "c_link": None
        }

    async def add_user(self, id: int, name: str):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id: int) -> bool:
        return await self.col.find_one({'id': id}) is not None

    async def total_users_count(self) -> int:
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id: int):
        await self.col.delete_many({'id': user_id})

    async def set_name(self, id: int, name: str):
        await self.col.update_one({'id': id}, {'$set': {'b_name': name}})

    async def get_name(self, id: int):
        user = await self.col.find_one({'id': id})
        return user.get('b_name') if user else None

    async def set_link(self, id: int, link: str):
        await self.col.update_one({'id': id}, {'$set': {'c_link': link}})

    async def get_link(self, id: int):
        user = await self.col.find_one({'id': id})
        return user.get('c_link') if user else None


# Instances
checkdb = BaseDatabase(MONGODB_URI, "TechVJVideoPlayerBot")
db = BaseDatabase(MONGODB_URI, "VJVideoPlayerBot")
