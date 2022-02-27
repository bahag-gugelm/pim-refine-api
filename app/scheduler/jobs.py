from itertools import compress

from app.datasources.external.crawlab import Crawlab
from app.core.config import settings
from app.models.item import CrawlabItemInfoModel


async def crawlab_import():
    def _filter_fields(item):
        garbage_fields = (
            '_id', 'task_id', 'files',
            'images', 'ean', 'ean13', 'gtin'
            )
        return {k: v for k, v in item.items() if k not in garbage_fields}

    ean_fields = ('ean', 'ean13', 'gtin')
    
    async with Crawlab(
        settings.CRAWLAB_API_URL,
        settings.CRAWLAB_API_KEY
        ) as client:
        spiders = await client.get_spiders()
        latest_tasks = [spider['latest_tasks'][0]['_id'] for spider in spiders]
        for task_id in latest_tasks:
            results = await client.get_results(task_id)
            if results:
                for item in results:
                    item = {k.lower(): v for k, v in item.copy().items()}
                    ean_field = [field in item.keys() for field in ean_fields]
                    if any(ean_field):
                        ean_field = list(compress(ean_fields, ean_field)).pop()
                        ean = item[ean_field]
                        db_item = await CrawlabItemInfoModel.objects.get_or_none(ean=ean)
                        if ean and len(ean) == 13:
                            if db_item and db_item.task_id != item['task_id']:
                                    item = await db_item.update(
                                        info=_filter_fields(item),
                                        task_id=item['task_id']
                                        )
                            else:
                                item = await CrawlabItemInfoModel(
                                ean=ean,
                                info=_filter_fields(item),
                                task_id=item['task_id']
                                ).save()
                                

scheduler_jobs = {
    'crawlab_import' : crawlab_import
    }
