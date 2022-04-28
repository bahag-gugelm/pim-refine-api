import re

from fastapi import (APIRouter, Depends, HTTPException, status)
from typing import List, Union

from app.core.config import settings
from app.models.user import UserDB
from app.utils.dependencies import get_current_user
from app.datasources.internal.bdx_am import BdxAm
from app.datasources.external.crawlab import Crawlab
from app.datasources.external.icecat import Icecat
from app.datasources.external.p_info import PInfo
from app.datasources.external.paw import Paw


router = APIRouter()


@router.get('/items/search')
async def search(
    query: str,
    user: UserDB = Depends(get_current_user()),
    response_model=None,
    status_code=200
    ):
    pim_client = BdxAm()
    response = list()
    query = re.findall(r'(\d+)', query)
    query_items_length = set(len(num) for num in query)
    if not query_items_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty query",
            )
    if len(query_items_length) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mixed length items in query",
            )
    if query_items_length.pop() not in (13, ):
        eans = list()
        for num in query:
            ean = await pim_client.pim2ean(num)
            ean and eans.append(ean)
        if not eans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid PIM_SKU found in query",
                )
        query = eans
    for ean in query:
        p_info_results = await PInfo(
            api_url = settings.P_INFO_API_URL,
            api_key = settings.P_INFO_API_KEY
            ).search(query=ean)
        pim_results = await pim_client.search(ean)
        icecat_results = await Icecat().search(ean)
        async with Crawlab(
            settings.CRAWLAB_API_URL,
            settings.CRAWLAB_API_KEY
            ) as crawlab_client:
            crawlab_results = await crawlab_client.search(ean)
        paw_results = await Paw().search(ean)
        response.append({
            'EAN': ean,
            'results': {
                **{'internal_pim': pim_results},
                **{'p_info': p_info_results},
                **{'icecat': icecat_results},
                **{'crawlab': crawlab_results},
                **{'paw': paw_results}
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
