from fastapi import (APIRouter, Depends)
from typing import List, Union

from app.core.config import settings
from app.models.user import UserDB
from app.utils.dependencies import get_current_user 
from app.datasources.external.p_info import PInfo
from app.datasources.external.meilisearch import MeiliSearch
from app.datasources.external.icecat import Icecat
from app.datasources.external.crawlab import Crawlab



router = APIRouter()


@router.get('/items/search')
async def search(
    query: str,
    user: UserDB = Depends(get_current_user()),
    response_model=None,
    status_code=200
    ):
   
    response = list()

    for ean in (item.strip() for item in query.split(',')):
        p_info_results = await PInfo(
            api_url = settings.P_INFO_API_URL,
            api_key = settings.P_INFO_API_KEY
            ).search(query=ean)
        meilisearch = MeiliSearch('http://34.107.102.246/')
        pim_results = await meilisearch.search(ean)
        icecat_results = await Icecat().search(ean)
        async with Crawlab(
            settings.CRAWLAB_API_URL,
            settings.CRAWLAB_API_KEY
            ) as crawlab_client:
            crawlab_results = await crawlab_client.search(ean)
        response.append({
            'EAN': ean,
            'results': {
                **pim_results,
                **{'p_info': p_info_results},
                **{'icecat': icecat_results},
                **{'crawlab': crawlab_results}
                }
            })
    
    return response


@router.get('/icecat/search')
async def search(
    query: str,
    user: UserDB = Depends(get_current_user()),
    response_model=None,
    status_code=200
    ):
   
    response = list()

    for ean in (item.strip() for item in query.split(',')):
        icecat_results = await Icecat().search_full_icecat(
            ean,
            username=settings.ICECAT_USER,
            icecat_api_key=settings.ICECAT_API_KEY,
            requested_by=user.id
            )
        response.append(icecat_results)
    return response