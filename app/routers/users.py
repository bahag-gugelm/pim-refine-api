from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

from app.core.config import settings
from app.models.user import User, UserCreate, UserDB, UserUpdate
from app.utils.dependencies import get_user_manager



SECRET_KEY = settings.SECRET_KEY


jwt_authentication = JWTAuthentication(
    secret=SECRET_KEY,
    lifetime_seconds=3600,
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

current_active_user = fastapi_users.current_user(active=True)
