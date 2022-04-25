from app.datasources.generic import DataSource
from app.models.item import PimQuery20_5, PimQuery29



class BdxAm(DataSource):
    async def search(self, query: str):
        attribs_exclude_fields = {
            'Material_group', 'Variant_product',
            'Mandators', 'SAP_name', 'lfd_nr'
            }
        res205 = await PimQuery20_5.objects.get_or_none(EAN=query)
        res = res205 and res205.dict()
        if res:
            res29 = await PimQuery29.objects.all(Variant_product=res['Variant_product'])
            res['Attributes'] = [item.dict(exclude=attribs_exclude_fields) for item in res29]
            return res


    async def pim2ean(self, query: str):
        res = await PimQuery20_5.objects.get_or_none(Variant_product=query)
        if res:
            return res.EAN
