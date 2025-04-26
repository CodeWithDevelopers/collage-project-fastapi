# app/services/user_service.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import user_helper
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any, Optional
from passlib.context import CryptContext
from app.schemas.user import UsersResponse, UserOut
from app.models.counter import get_next_sequence
from app.utils.query_params import get_sort_criteria, get_projection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db):
        self.db = db  # Fix: add db reference
        self.collection = db["users"]

    def build_response(self, success: bool, message: str, data: Any = None, code: int = 200):
        return {
            "success": success,
            "message": message,
            "data": data,
            "code": code
        }

    async def create_user(self, user_data: dict):
        user_data["id"] = await get_next_sequence(self.collection.database, "user_id")
        user_data["password"] = pwd_context.hash(user_data["password"])
        user_data["is_deleted"] = False
        user_data["role"] = user_data.get("role", "user")
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(user_data)
        user = await self.collection.find_one({"_id": result.inserted_id})
        return self.build_response(True, "User created successfully", user_helper(user), 201)

    async def list_users(
        self,
        page: int = 1,
        limit: int = 10,
        sort: Optional[str] = None,
        fields: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> List[UserOut]:  # Now returns a list of UserOut
        skip = (page - 1) * limit
        sort_criteria = get_sort_criteria(sort)
        projection = get_projection(fields)

        query = filters or {}

        cursor = self.collection.find(query, projection)

        if sort_criteria:
            cursor = cursor.sort(sort_criteria)

        cursor = cursor.skip(skip).limit(limit)
        results = []
        async for user in cursor:
            user["id"] = int(user["id"])
            results.append(UserOut(**user))  # Append each user to the list

        return results  # Now returning the list directly


    async def get_all_users(self) -> Dict[str, Any]:
        users_cursor = self.collection.find({"is_deleted": False})
        users = await users_cursor.to_list(length=100)
        user_list = [UsersResponse(**user_helper(user)) for user in users]
        return self.build_response(True, "All users fetched successfully", user_list)

    async def get_user_by_id(self, user_id: int):
        user = await self.collection.find_one({"id": user_id, "is_deleted": False})
        if user:
            return self.build_response(True, "User found", user_helper(user))
        return self.build_response(False, "User not found", None, 404)

    async def get_user_by_email(self, email: str):
        user = await self.collection.find_one({"email": email, "is_deleted": False})
        if user:
            return self.build_response(True, "User found", user_helper(user))
        return self.build_response(False, "User not found", None, 404)

    async def update_user(self, user_id: int, update_data: dict):
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one({"id": user_id}, {"$set": update_data})
        updated_user = await self.get_user_by_id(user_id)
        return self.build_response(True, "User updated successfully", updated_user["data"])

    async def delete_user(self, user_id: int):
        await self.collection.update_one({"id": user_id}, {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}})
        return self.build_response(True, "User deleted successfully", {"user_id": user_id})

    async def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
