from functools import wraps
import enum
from fastapi import status, HTTPException, Request
from .security import get_current_user_or_theatre, get_token_payload
from . import settings

class Role(enum.Enum):
    USER = "user"
    THEATRE = "theatre"
    ADMIN = "admin"

class PermissionDependency:
    def __init__(self, role, klass):
        self.role = role
        self.klass = klass

    async def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization token missing from header",
            )
        token = token.split(" ")[1]
        user = await get_current_user_or_theatre(token, settings.ACCESS_TOKEN_SECRET_KEY, self.klass)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        required_role = get_token_payload(token, settings.ACCESS_TOKEN_SECRET_KEY)
        if not required_role:
            raise HTTPException(status_code=400, detail="Invalid token provided")
        required_role = required_role["roles"]
        if user.role not in required_role or user.role != self.role.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have permission to perform this action.",
            )
        return user

def login_required(klass):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            access_token = request.headers.get("Authorization") or ""
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authorization token missing from header",
                )
            access_token = access_token.split(" ")[1]
            user = await get_current_user_or_theatre(access_token, settings.ACCESS_TOKEN_SECRET_KEY, klass)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator