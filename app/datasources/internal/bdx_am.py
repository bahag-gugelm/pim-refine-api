from app.datasources.generic import DataSource
from app.models.item import PimQuery20_5, PimQuery29
from app.utils.cache import cached

from fastapi_cache import FastAPICache

class BdxAm(DataSource):
    @cached
    async def search(self, query: str):
        attribs_exclude_fields = {
            'id', 'Material_group', 'Variant_product',
            'Mandators', 'SAP_name',
            }
        query = query.lstrip('0')
        res205 = query and await PimQuery20_5.objects.get_or_none(EAN=query)
        res = res205 and res205.dict()
        if res:
            res29 = await PimQuery29.objects.all(Variant_product=res['Variant_product'])
            res['Attributes'] = [item.dict(exclude=attribs_exclude_fields) for item in res29]
            return res
    
    @cached
    async def pim2ean(self, query: str):
        res = await PimQuery20_5.objects.get_or_none(Variant_product=query)
        if res:
            ean = res.EAN
            return f'{"0"*(13-len(ean))}{ean}'
