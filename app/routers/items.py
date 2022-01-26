from fastapi import (APIRouter, Depends)
from typing import List, Union

from app.models.user import UserDB
from app.routers.users import current_active_user 
from app.datasources.external.p_info import PInfo
from app.datasources.external.meilisearch import MeiliSearch
from app.core.config import settings


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
        p_info_client = PInfo(
            api_url = settings.P_INFO_API_URL,
            api_key = settings.P_INFO_API_KEY
            )
        p_info_results = await p_info_client.search(query=ean)
        meilisearch = MeiliSearch('http://34.107.102.246/')
        pim_results = await meilisearch.search(ean)
        response.append({
            'EAN': ean,
            'results': {**pim_results, **{'p_info': p_info_results}}
            })
    
    return response
