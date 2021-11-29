from typing import Union, List

from fastapi.exceptions import HTTPException
from meilisearch_python_async import Client

from app.datasources.generic import DataSource



class MeiliSearch(DataSource):
    def __init__(self, api_url: str, api_key: str = None):
        self.session = Client(api_url, api_key)

    async def search(self, query: str) -> dict:
        async with self.session as client:
            index = client.index('internal_pim')
            search_result = await index.search(query, limit=1)
            return search_result.hits