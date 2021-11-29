from fastapi_users import BaseUserManager

from app.models.user import UserCreate, UserDB
from app.core.config import settings



class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY
