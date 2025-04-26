# A helper to manage auto-incrementing IDs

from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_next_sequence(db: AsyncIOMotorDatabase, name: str) -> int:
    result = await db["counters"].find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True
    )
    return result["value"]
