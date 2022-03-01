from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

from app.core.config import settings
from app.models.user import User, UserCreate, UserDB, UserUpdate
from app.utils.dependencies import get_user_manager



jwt_authentication = JWTAuthentication(
    secret=settings.SECRET_KEY,
    lifetime_seconds=settings.ACCESS_TOKEN_LIFETIME,
    tokenUrl="auth/jwt/login"
    )

fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
    )

def get_fastapi_users():
    return fastapi_users
