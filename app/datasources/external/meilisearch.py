from typing import Union, List

from fastapi.exceptions import HTTPException
from meilisearch_python_async import Client

from app.datasources.generic import DataSource



class MeiliSearch(DataSource):
    def __init__(self, api_url: str, api_key: str = None):
        self.session = Client(api_url, api_key)

    async def search(self, query: str) -> dict:
        response = dict()
        async with self.session as client:
            for index in await client.get_indexes():
                search_result = await index.search(query, limit=1)
                results_set = search_result.hits and next(iter(search_result.hits)) or None
                if results_set and str(int(results_set['EAN'])) == query:
                    response[index.uid] = results_set 
        return response