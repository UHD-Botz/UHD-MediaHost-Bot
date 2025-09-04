from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import time

class Database:
    def __init__(self, uri: str, name: str):
        if not uri or not name:
            raise RuntimeError("DB_URI / DB_NAME missing in env")
        self.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=8000)
        self.db = self.client[name]
        # collections
        self.users = self.db.users
        self.bans = self.db.bans
        self.logs = self.db.logs
        self.files = self.db.files
        self.meta = self.db.meta

    async def ping(self) -> bool:
        try:
            await self.db.command("ping")
            return True
        except ServerSelectionTimeoutError:
            return False

    async def ensure_indexes(self):
        await self.users.create_index("user_id", unique=True)
        await self.bans.create_index("user_id", unique=True)
        await self.files.create_index("file_unique_id", unique=True)

    # --- Users ---
    async def add_user(self, user_id: int, first_name: Optional[str], username: Optional[str]):
        now = int(time.time())
        await self.users.update_one(
            {"user_id": user_id},
            {"$setOnInsert": {"user_id": user_id, "joined_at": now},
             "$set": {"first_name": first_name, "username": username}},
            upsert=True
        )

    async def total_users(self) -> int:
        return await self.users.estimated_document_count()

    # --- Bans ---
    async def is_banned(self, user_id: int) -> bool:
        return await self.bans.find_one({"user_id": user_id}) is not None

    async def ban(self, user_id: int, reason: Optional[str], by: Optional[int]):
        await self.bans.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "reason": reason, "by": by, "ts": int(time.time())}},
            upsert=True
        )

    async def unban(self, user_id: int) -> int:
        res = await self.bans.delete_one({"user_id": user_id})
        return res.deleted_count

    # --- Logs ---
    async def log_event(self, **data: Any):
        data["ts"] = data.get("ts", int(time.time()))
        await self.logs.insert_one(data)

    # --- File cache ---
    async def cache_file(self, file_unique_id: str, file_id: str, file_ref: Optional[str] = None, **meta):
        await self.files.update_one(
            {"file_unique_id": file_unique_id},
            {"$set": {"file_unique_id": file_unique_id, "file_id": file_id, "file_ref": file_ref, **meta}},
            upsert=True
        )

    async def get_cached(self, file_unique_id: str) -> Optional[Dict[str, Any]]:
        return await self.files.find_one({"file_unique_id": file_unique_id})
