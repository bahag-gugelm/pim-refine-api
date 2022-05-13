from typing import Union, List

from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource
from app.models.item import CrawlabItemInfoModel
from app.utils.cache import cached



class Crawlab(DataSource):
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.session = AsyncClient(verify=False)
        self.session.headers.update({'Authorization': api_key})
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.aclose()


    @cached
    async def search(self, query: str) -> dict:
        item = await CrawlabItemInfoModel.objects.get_or_none(ean=query)
        if item:
            return item.info


    async def get_spiders(self):
        response = await self.session.get(f'{self.api_url}/spiders')
        if response.status_code in (200, ):
            json_body = response.json()
            if json_body['status'] in ('ok', ):
                return json_body['data']['list']
            else:
                return json_body['error']


    async def get_results(self, task_id: str) -> dict:
        response = await self.session.get(f'{self.api_url}/tasks/{task_id}/results')
        if response.status_code in (200, ):
            json_body = response.json()
            if json_body['status'] in ('ok', ):
                return json_body['data']
            else:
                return json_body['error']
