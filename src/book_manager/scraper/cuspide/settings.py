"""Configuración del proyecto Scrapy de Cúspide."""
from pathlib import Path

BOT_NAME = 'cuspide'
SPIDER_MODULES = ['cuspide.spiders']
NEWSPIDER_MODULE = 'cuspide.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    'cuspide.pipelines.ValidacionPipeline': 100,
    'cuspide.pipelines.FormasPagoPipeline': 200,
    'cuspide.pipelines.ExportarJsonPipeline': 300,
}

CUSPIDE_SALIDA = str(Path(__file__).resolve().parents[2]
                     / 'reportes' / 'resultados_cuspide.json')

FEED_EXPORT_ENCODING = 'utf-8'
