from logging import exception
from passlib.context import CryptContext

from fastapi import Depends, FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users.password import get_password_hash

from sqlalchemy import create_engine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.core.config import settings
from app.db import database, bdx_database
from app.utils.dependencies import get_user_manager
from app.models.user import UserDB, UserModel, UserCreate
from app.routers.users import fastapi_users, jwt_authentication
from app.routers import items
from app.routers import schedules


app = FastAPI()
app.state.database = database
app.state.bdx_database = bdx_database


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    bdx_database_ = app.state.bdx_database
    if not database_.is_connected:
        await database_.connect()
    if not bdx_database_.is_connected:
        await bdx_database_.connect()
    
    try:
        jobstores = {
            'default': SQLAlchemyJobStore(engine=create_engine(settings.SQLALCHEMY_DATABASE_URI))
            }
        app.state.scheduler = AsyncIOScheduler(jobstores=jobstores)
        app.state.scheduler.start()
        logger.info("Created Schedule Object")   
    except Exception as e:    
        logger.error(f"Unable to Create Schedule Object because of {e}")


    # doesn't work under Win
    # su = await UserModel.objects.get_or_none(email=settings.FIRST_SUPERUSER)
    # if not su:
    #     async with get_user_manager() as user_manager:
    #             user = await user_manager.create(
    #                 UserCreate(
    #                     email=settings.FIRST_SUPERUSER,
    #                     hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
    #                     is_superuser=True,
    #                     is_active=True,
    #                     is_verified=True
    #                     )
    #             )


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    bdx_database_ = app.state.bdx_database
    if database_.is_connected:
        await database_.disconnect()
    if bdx_database_.is_connected:
        await bdx_database_.disconnect()
    app.state.scheduler.shutdown()
    logger.info("Scheduler is shut down")


app.include_router(fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

app.include_router(items.router, tags=["search"])
app.include_router(schedules.router, tags=["scheduler"])
