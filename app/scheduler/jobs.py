import csv
from ftplib import FTP
from io import StringIO
from itertools import compress, islice

from pysftp import Connection

from app.datasources.external.crawlab import Crawlab
from app.core.config import settings
from app.models.item import CrawlabItemInfoModel, PawInfoModel, PimQuery20_5, PimQuery29



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
                        if all([variant_id not in ('***', ), variant_id not in db_items]):
                            try:
                                new_item = {
                                    'variant_id': variant_id,
                                    'info': {k: v.replace('#', ' ') for k, v in row.items()}
                                    }
                                new_items.append(PawInfoModel(**new_item))
                            except AttributeError:
                                continue
                
                if new_items:
                    await PawInfoModel.objects.bulk_create(new_items)
                
                ftp.delete(f'./{fname}')


async def pim_import(chunk_size=50000):
    files = ('Query_20.5_DE.csv', 'Query_29_DE.csv')
    async def _chunks(iterable, size):
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, size))
            if not chunk:
                break
            yield chunk
    with Connection(
    host=settings.DGE_HOST,
    username=settings.DGE_USER,
    password=settings.DGE_PASSWORD
    ) as sftp:
        for fname in files:
            data_model = PimQuery20_5 if '20.5' in fname else PimQuery29
            db = data_model.Meta.database
            db_table = data_model.Meta.table
            model_fields = [field for field in data_model.__fields__.keys() if field not in ('id',)]
            await data_model.Meta.database.execute(f'TRUNCATE "{data_model.Meta.tablename}";')
            csv_file = sftp.open(fname, mode='r')
            csv_reader = csv.reader(csv_file, delimiter=';')
            next(csv_reader)
            async for chunk in _chunks(csv_reader, chunk_size):
                bulk = [dict(zip(model_fields, item)) for item in chunk]
                async with db.connection() as connection:
                    async with connection.transaction():
                        await db.execute_many(
                            db_table.insert(),
                            bulk
                            )


scheduler_jobs = {
    'crawlab_import': crawlab_import,
    'paw_import': paw_import,
    'pim_import': pim_import
    }
