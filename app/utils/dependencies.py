from fastapi import Depends
from fastapi_users.db import OrmarUserDatabase

from app.models.user import UserDB, UserModel
from app.db.managers import UserManager



def get_user_db():
    yield OrmarUserDatabase(UserDB, UserModel)


def get_user_manager(user_db: OrmarUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_current_user():
    from app.routers.users import fastapi_users
    return fastapi_users.current_user(active=True)


def get_current_admin():
    from app.routers.users import fastapi_users
    return fastapi_users.current_user(superuser=True)
