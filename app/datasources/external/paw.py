from app.datasources.generic import DataSource
from app.models.item import PimQuery20_5, PawInfoModel



class Paw(DataSource):
    async def search(self, query: str):
        res205 = await PimQuery20_5.objects.get_or_none(EAN=query)
        if res205:
            item = await PawInfoModel.objects.get_or_none(variant_id=res205.Variant_product)
            if item:
                return item.info
