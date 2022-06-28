import logging
import re
from typing import Union, List
from charset_normalizer import CharsetMatch
from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource
from app.models.item import IceCatItemInfoModel
from app.utils.misc import HTMLTextExtractor


class Icecat(DataSource):
    def __init__(self):
        self.session = AsyncClient(verify=False)
        self.logger = logging.getLogger(__name__)
        self._txt_cleaner = HTMLTextExtractor()


    def _extract_attributes(self, data: dict):
        full_desc = data.get("GeneralInfo").get("Description").get("LongDesc")
        
        product_info = {
            "EAN": data.get("GeneralInfo").get("GTIN"),
            "Title": data.get("GeneralInfo").get("Title"),
            "Brand": data.get("GeneralInfo").get("Brand"),
            "ShortDescription": data.get("GeneralInfo").get("SummaryDescription").get("ShortSummaryDescription"),
            "LongDescription": data.get("GeneralInfo").get("SummaryDescription").get("LongSummaryDescription"),
            "BulletPoints": data.get("GeneralInfo").get("BulletPoints").get("Values"),
            "FullDescription": full_desc and self._txt_cleaner.html_to_text(full_desc) or '',
            "LongProductName": data.get("GeneralInfo").get("Description").get("LongProductName"),
        }
        feature_groups = data.get("FeaturesGroups")
        for feature_group in feature_groups:
            for feature in feature_group.get("Features"):
                if isinstance(feature.get("PresentationValue"), list):
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
            if isinstance(multimedia_item.get("URL"), list):
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
            eprel_link = multimedia_item.get('EprelLink')
            eprel_link and product_info.update({'EprelLink': eprel_link, 'EprelID': eprel_link.split('/')[-1]})
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
            if json_body.get("StatusCode") == 9: # Product not available in open icecat but in full icecat.
                cached_item = await IceCatItemInfoModel.objects.get_or_none(ean=query)
                return cached_item and self._extract_attributes(cached_item.info) or {'info' :'Available in full IceCat'}


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
