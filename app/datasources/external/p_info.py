from typing import Union, List

from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource



class PInfo(DataSource):
    def __init__(self, api_url: str):
        self.session = AsyncClient(verify=False)
        super().__init__(api_url)

    async def search(self, query: str) -> dict:
        async with self.session as client:
            response = await client.get(f'{self.api_url}?gtin={query}')
            json_body = response.json()
            resp_code = int(json_body['response']['code'])
            if resp_code not in (200, ):
                return
                # raise HTTPException(status_code=resp_code)
            result_set = [src for src in json_body['articles'] if src['specs_raw'] and len([item for item in json_body['articles'] if item and item['specs_raw']]) > 1]
        return result_set
