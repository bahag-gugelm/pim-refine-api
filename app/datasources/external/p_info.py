from typing import Union, List

from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource
from app.utils.cache import cached


class PInfo(DataSource):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = AsyncClient(verify=False)
        self.session.headers.update({'pinfo-product-api-key': api_key})

    @cached
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
            flat_result_set = []
            for shop in result_set:
                dict_temp = {}
                for shop_att in shop:
                    if shop_att=="specs_raw":
                        for specs in shop["specs_raw"]:
                            dict_temp.update({specs["spec"]: specs["value"]})
                    elif shop_att=="specs_raw" or shop_att=="cross":
                        pass
                    elif type(shop.get(shop_att))==list:
                        try:
                            dict_temp.update({shop_att:  ", ".join(shop.get(shop_att))})
                        except TypeError:
                            pass
                    else:
                        dict_temp.update({shop_att: shop.get(shop_att)})
                flat_result_set.append(dict_temp)
            return flat_result_set
