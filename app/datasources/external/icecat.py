import logging
import re
from typing import Union, List
from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource
from app.models.item import IceCatItemInfoModel


class Icecat(DataSource):
    def __init__(self):
        self.session = AsyncClient(verify=False)
        self.logger = logging.getLogger(__name__)


    def _cleanup_txt(self, text: str):
        if text:
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text).strip().replace('\n', '')


    def _extract_attributes(self, data: dict):
        product_info = {
            "EAN": data.get("GeneralInfo").get("GTIN"),
            "Title": data.get("GeneralInfo").get("Title"),
            "Brand": data.get("GeneralInfo").get("Brand"),
            "ShortDescription": data.get("GeneralInfo").get("SummaryDescription").get("ShortSummaryDescription"),
            "LongDescription": data.get("GeneralInfo").get("SummaryDescription").get("LongSummaryDescription"),
            "BulletPoints": data.get("GeneralInfo").get("BulletPoints").get("Values"),
            "FullDescription": self._cleanup_txt(data.get("GeneralInfo").get("Description").get("LongDesc")),
            "LongProductName": data.get("GeneralInfo").get("Description").get("LongProductName"),
        }
        feature_groups = data.get("FeaturesGroups")
        for feature_group in feature_groups:
            for feature in feature_group.get("Features"):
                if type(feature.get("PresentationValue"))==list:
                    product_info.update(
                        {
                            feature.get("Feature").get("Name").get("Value"): ", ".join(feature.get("PresentationValue"))
                        }
                    )
                else:
                    product_info.update(
                        {
                            feature.get("Feature").get("Name").get("Value"): feature.get("PresentationValue")
                        }
                    )

        image_list = []
        for image_item in data.get("Gallery"):
            image_list.append(image_item.get("Pic"))
        product_info.update({"Images": ", ".join(image_list)})
        for multimedia_item in data.get("Multimedia"):
            if type(multimedia_item.get("URL"))==list:
                product_info.update(
                    {
                        multimedia_item.get("Type"): ", ".join(multimedia_item.get("URL"))
                    }
                )
            else:
                product_info.update(
                    {
                        multimedia_item.get("Type"): multimedia_item.get("URL")
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
                return None # Product not availiable in icecat.


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
                    return None
        return self._extract_attributes(cached_item.info)
