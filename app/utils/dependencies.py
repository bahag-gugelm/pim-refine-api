from fastapi import Depends
from fastapi_users.db import OrmarUserDatabase

from app.models.user import UserDB, UserModel
from app.db.managers import UserManager



def get_user_db():
    yield OrmarUserDatabase(UserDB, UserModel)


def get_user_manager(user_db: OrmarUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)