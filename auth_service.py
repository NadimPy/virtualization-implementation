from fastapi import Header, HTTPException
from SQL.USERS_related import get_user_by_api_key

async def get_current_user(x_api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user