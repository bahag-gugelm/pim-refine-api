from ormar.models import Model
from ormar import JSON, String, ForeignKey, DateTime

from app.db import metadata, database
from app.models.user import UserModel

from sqlalchemy import func


class IceCatItemInfoModel(Model):
    class Meta:
        tablename = 'icecat_info'
        metadata = metadata
        database = database

    ean = String(primary_key=True, index=True, unique=True, nullable=False, max_length=13)
    info = JSON()
    requested_by = ForeignKey(UserModel)
    requested_at = DateTime(server_default=func.current_timestamp())
