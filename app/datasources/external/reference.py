from httpx import AsyncClient

from app.datasources.generic import DataSource


class PimEanReference(DataSource):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = AsyncClient(verify=False)
        self.session.headers.update({'X-Token': api_key})
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.aclose()


    async def search(self, query: str) -> dict:
        response = await self.session.get(f'{self.api_url}/pim_ean/{query}')
        json_body = response.json()
        return json_body
