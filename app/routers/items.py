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
    client = PInfo('https://p-info.bahag.com/temp/api-test/')
    result_set = await client.search(query=query)
    meilisearch = MeiliSearch('http://34.107.102.246/')
    pim_results = await meilisearch.search(query)
    return {
        'EAN': query,
        'internal': pim_results,
        'external': {'p_info': result_set}
        }