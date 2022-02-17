import logging
from os import stat
from typing import Union, List
from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource
from app.models.item import IceCatItemInfoModel


class Icecat(DataSource):
    def __init__(self):
        self.session = AsyncClient(verify=False)
        self.logger = logging.getLogger(__name__)


    @staticmethod
    def _extract_attributes(data: dict):
        product_info = {
            "EAN": data.get("GeneralInfo").get("GTIN"),
            "Title": data.get("GeneralInfo").get("Title"),
            "Brand": data.get("GeneralInfo").get("Brand"),
            "ShortDescription": data.get("GeneralInfo").get("SummaryDescription").get("ShortSummaryDescription"),
            "LongDescription": data.get("GeneralInfo").get("SummaryDescription").get("LongSummaryDescription"),
            "BulletPoints": data.get("GeneralInfo").get("BulletPoints").get("Values")
        }
        feature_groups = data.get("FeaturesGroups")
        for feature_group in feature_groups:
            for feature in feature_group.get("Features"):
                product_info.update(
                    {
                        feature.get("Feature").get("Name").get("Value"): feature.get("PresentationValue")
                    }
                )
        return product_info


    async def search(self, query: str) -> dict:
        async with self.session as client:
            api_url = f"https://live.icecat.biz/api/?UserName=openIcecat-live&Language=DE&GTIN={query}&Content=All"
            response = await client.get(api_url)
            json_body = response.json()
            info_data = json_body.get("data")
            if info_data:
                product_info = self._extract_attributes(info_data)
                return product_info
            elif json_body.get("StatusCode") == 9: # Product not available in open icecat but in full icecat.
                return {'Available in full IceCat'} 
            else:
                return [] # Product not availiable in icecat.


    async def search_full_icecat(self, query: str, username, icecat_api_key, requested_by: str) -> dict:
        cached_item = await IceCatItemInfoModel.objects.get_or_none(ean=query)
        if not cached_item:
            async with self.session as client:
                api_url = f"https://live.icecat.biz/api/?shopname={username}&lang=DE&content=All&GTIN={query}&app_key={icecat_api_key}"
                response = await client.get(api_url)
                self.logger.info(f'Item with EAN #{query} was requested by {requested_by}')
                json_body = response.json()
                info_data = json_body.get("data")
                if info_data:
                    item = await IceCatItemInfoModel(
                        ean=query,
                        requested_by=requested_by,
                        info=info_data
                        ).save()
                    product_info = self._extract_attributes(item.info)
                    return product_info
                else:
                    return []
        return self._extract_attributes(cached_item.info)
