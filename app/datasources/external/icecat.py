from typing import Union, List
from fastapi.exceptions import HTTPException
from httpx import AsyncClient

from app.datasources.generic import DataSource


class Icecat(DataSource):
    def __init__(self):
        self.session = AsyncClient(verify=False)


    def _extract_attributes(data: dict):
        product_info = {
            "EAN": data.get("GeneralInfo").get("GTIN"),
            "Title": data.get("GeneralInfo").get("Title"),
            "Brand": data.get("GeneralInfo").get("Brand"),
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
            if json_body.get("data"):
                product_info = Icecat._extract_attributes(json_body.get("data"))
                return product_info
            elif json_body.get("StatusCode")==9:
                return 0 # Product not available in open icecat but in full icecat.
            else:
                return [] # Product not availiable in icecat.


    async def search_full_icecart(self, query: str, username, icecat_api_key) -> dict:
        async with self.session as client:
            api_url = f"https://live.icecat.biz/api/?shopname={username}&lang=DE&content=All&GTIN={query}&app_key={icecat_api_key}"
            response = await client.get(api_url)
            json_body = response.json()
            if json_body.get("data"):
                product_info = product_info = Icecat._extract_attributes(json_body.get("data"))
                return product_info
            else:
                return []