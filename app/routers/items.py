from fastapi import (APIRouter, Depends)
from typing import List, Union

from app.models.user import UserDB
from app.routers.users import current_active_user 
from app.datasources.external.p_info import PInfo
from app.datasources.external.meilisearch import MeiliSearch



router = APIRouter()


@router.get('/items/search')
async def search(
    query: str,
    user: UserDB = Depends(current_active_user),
    response_model=None,
    status_code=200
    ):
    response = list()
    for ean in (item.strip() for item in query.split(',')):
        meilisearch = MeiliSearch('http://34.107.102.246/')
        response.append({
            'EAN': ean,
            'results': await meilisearch.search(ean)
            })
    return response