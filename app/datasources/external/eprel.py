import logging
import httpx



logger = logging.getLogger(__name__)


class EPREL:
    api_base_url = 'https://eprel.ec.europa.eu/api/products/'
    qr_base_url = 'https://eprel.ec.europa.eu/qr/'


    async def get_category(self, eprel_id: str) -> str:
        response = httpx.get(
            url=f'{self.qr_base_url}{eprel_id}'
            )
        category = response.url.path.split('/')[-2]
        if category not in ('error', ):
            return category
        
        logger.warning(f'Can\'t get category for id={eprel_id}')


    async def get_info(self, eprel_id: str, eprel_cat: str) -> dict:
        response = httpx.get(
            url=f'{self.api_base_url}{eprel_cat}/{eprel_id}'
            )
        if all([not response.is_error, response.text]):    
            return response.json()
        
        logger.warning(f'Can\'t get the info for id={eprel_id}')
               

    async def get_label(self, eprel_id: str, eprel_cat: str, img_format: str = 'PNG') -> bytes:
        response = httpx.get(
            url=f'{self.api_base_url}{eprel_cat}/{eprel_id}/labels/?format={img_format}'
            )
        if all([response.ok, 'html' not in response.text]):
            return response.content
        
        logger.warning(f'Can\'t get the label for id={eprel_id}')


    async def get_eel_pack(self, eprel_cat: str, eprel_id: str, ) -> bytes:
        response = httpx.get(
            url=f'{self.api_base_url}{eprel_cat}/{eprel_id}/labels'
            )
        if all([response.ok, 'html' not in response.text]):
            return response.content

        logger.warning(f'Can\'t get the label-pack for id={eprel_id}')

    
    async def search(self, query: str):
        return await self.get_info(query, await self.get_category(query))
