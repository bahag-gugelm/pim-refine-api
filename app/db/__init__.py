from os import environ

import databases
import sqlalchemy

from app.core.config import settings



if not settings.PRODUCTION:
    # Use separate DB for tests
    TEST_DATABASE_URI = ''.join([settings.SQLALCHEMY_DATABASE_URI, '_test'])
    database = databases.Database(TEST_DATABASE_URI)
else:
    database = databases.Database(settings.SQLALCHEMY_DATABASE_URI)
    bdx_database = databases.Database(settings.BDX_SQLALCHEMY_DATABASE_URI)


metadata = sqlalchemy.MetaData()
