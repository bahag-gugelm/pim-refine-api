import hashlib

from fastapi_cache.decorator import cache
from app.core.config import settings

from starlette.requests import Request
from starlette.responses import Response
from typing import Optional

from fastapi_cache import FastAPICache



# As all the search operations are their respective clients bound methods, we need to get rid of 
# 'self' as the first function's argument which will be a different object in all the successive
# class calls and therefore won't produce same keys for caching, so using just the kwargs.
def _key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
    ):
    prefix = f'{FastAPICache.get_prefix()}:{namespace}:'
    cache_key = prefix + hashlib.md5(
        f"{func.__module__}:{func.__name__}:{kwargs['kwargs']}".encode()
        ).hexdigest()
    return cache_key


cached = cache(expire=settings.CACHE_TTL, key_builder=_key_builder)

