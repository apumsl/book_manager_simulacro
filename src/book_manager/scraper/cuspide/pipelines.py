"""Pipelines del scraper de Cúspide."""
import json
import logging
from pathlib import Path
from typing import Any

from itemadapter import ItemAdapter
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

CAMPOS_OBLIGATORIOS = ('libro_id', 'url', 'precio')

logger = logging.getLogger(__name__)


class ValidacionPipeline:
    """Descarta los ítems a los que les falta un dato obligatorio."""

    def process_item(self, item: Any) -> Any:
        """Deja pasar el ítem solo si tiene libro de origen, URL y precio.

        Raises:
            DropItem: Si falta alguno de los campos obligatorios.
        """
        adaptador = ItemAdapter(item)
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS
                     if adaptador.get(campo) is None]
        if faltantes:
            raise DropItem(f'Faltan {", ".join(faltantes)} '
                           f'en {adaptador.get("url")}')
        return item


class FormasPagoPipeline:
    """Asocia el precio del producto a cada forma de pago disponible.

    Cúspide no publica precios distintos por medio de pago, por lo que
    cada forma de pago lleva el precio de lista del producto.
    """

    def process_item(self, item: Any) -> Any:
        """Convierte la lista de formas de pago en pares forma y precio."""
        adaptador = ItemAdapter(item)
        precio = adaptador.get('precio')
        formas = adaptador.get('formas_pago') or []
        adaptador['formas_pago'] = [
            {'forma': forma, 'precio': precio} for forma in formas]
        return item


class ExportarJsonPipeline:
    """Guarda en un archivo JSON todos los ítems de una ejecución."""

    def __init__(self, ruta_salida: str) -> None:
        """Inicializa el pipeline con la ruta del archivo de salida."""
        self.ruta_salida = Path(ruta_salida)
        self.items: list[dict[str, Any]] = []

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'ExportarJsonPipeline':
        """Crea el pipeline leyendo la ruta de salida de los settings."""
        return cls(crawler.settings.get('CUSPIDE_SALIDA'))

    def open_spider(self) -> None:
        """Vacía la lista de ítems al iniciar la ejecución."""
        self.items = []

    def process_item(self, item: Any) -> Any:
        """Acumula el ítem para escribirlo al finalizar."""
        self.items.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self) -> None:
        """Escribe todos los ítems en el JSON de salida.

        Los precios Decimal se guardan como texto para no perder precisión.
        """
        self.ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_salida, 'w', encoding='utf-8') as archivo:
            json.dump(self.items, archivo, ensure_ascii=False, indent=2,
                      default=str)
        logger.info('%d ítems guardados en %s',
                    len(self.items), self.ruta_salida)


class AlertasPreciosPipeline:
    """Compara precio interno y precio web y genera el CSV de alertas.

    Usa la diferencia que ingresó el usuario al lanzar el spider y crea
    un archivo nuevo en reportes/ en cada ejecución.
    """

    def __init__(self, crawler: Crawler) -> None:
        """Inicializa el pipeline guardando el crawler en ejecución."""
        self.crawler = crawler
        self.items: list[dict[str, Any]] = []

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'AlertasPreciosPipeline':
        """Crea el pipeline a partir del crawler."""
        return cls(crawler)

    def open_spider(self) -> None:
        """Vacía la lista de ítems al iniciar la ejecución."""
        self.items = []

    def process_item(self, item: Any) -> Any:
        """Acumula el ítem para compararlo al finalizar."""
        self.items.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self) -> None:
        """Genera las alertas y las exporta a CSV."""
        spider = self.crawler.spider
        servicio = spider.servicio_alertas
        alertas = servicio.generar_alertas(
            spider.libros, self.items, spider.diferencia)
        ruta = servicio.exportar_csv(alertas)
        logger.info('%d alertas (diferencia mayor a $%s) guardadas en %s',
                    len(alertas), spider.diferencia, ruta)
        if servicio.sin_coincidencia:
            logger.info('Sin resultado con el mismo título (no se '
                        'comparan): %s', ', '.join(servicio.sin_coincidencia))
