from typing import Union, List

from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource


class PInfo(DataSource):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = AsyncClient(verify=False)
        self.session.headers.update({'pinfo-product-api-key': api_key})

    async def search(self, query: str) -> dict:
        async with self.session as client:
            response = await client.get(f'{self.api_url}?gtin={query}')
            json_body = response.json()
            resp_code = int(json_body['response']['code'])
            if resp_code not in (200, ):
                return []
                # raise HTTPException(status_code=resp_code)
            
            articles = json_body['articles']
            result_set = [
                src for src in articles if src.get('specs_raw') \
                    and len([item for item in articles if item and item.get('specs_raw')]) > 1
                    ]
            return result_set
