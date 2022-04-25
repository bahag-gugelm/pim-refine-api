import csv
from ftplib import FTP
from io import StringIO
from itertools import compress

from app.datasources.external.crawlab import Crawlab
from app.core.config import settings
from app.models.item import CrawlabItemInfoModel, PawInfoModel



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
                        if ean and len(ean) == 13:
                            db_item = await CrawlabItemInfoModel.objects.get_or_none(ean=ean)
                            if db_item and db_item.task_id != item['task_id']:
                                await db_item.update(
                                    info=_filter_fields(item),
                                    task_id=item['task_id']
                                    )
                            else:
                                await CrawlabItemInfoModel(
                                ean=ean,
                                info=_filter_fields(item),
                                task_id=item['task_id']
                                ).save()
                                

async def paw_import():
    with FTP(settings.PAW_HOST) as ftp:
        ftp.login(settings.PAW_USER, settings.PAW_PASSWORD)
        for fname in ftp.nlst():
            if fname.endswith('ArticleWhiteList.csv'):
                db_items = await PawInfoModel.objects.fields('variant_id').values_list(flatten=True)
                new_items = list()
                with StringIO() as csv_file:
                    ftp.retrbinary(f'RETR {fname}', lambda chunk: csv_file.write(chunk.decode('utf-8')))
                    csv_file.seek(0)
                    csv_reader = csv.DictReader(csv_file, delimiter=';', quoting=csv.QUOTE_NONE)
                    for row in csv_reader:
                        variant_id = row.pop('Artikelnummer')
                        if variant_id not in ('***', ):
                            try:
                                new_item = {
                                    'variant_id': variant_id,
                                    'info': {k: v.replace('#', ' ') for k, v in row.items()}
                                    }
                            except AttributeError:
                                continue

                            if not variant_id in db_items:
                                new_items.append(PawInfoModel(**new_item))
                if new_items:
                    await PawInfoModel.objects.bulk_create(new_items)
                
                ftp.delete(f'./{fname}') 

scheduler_jobs = {
    'crawlab_import' : crawlab_import,
    'paw_import' : paw_import
    }
