"""Items y loaders del scraper de Cúspide."""
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional

import scrapy
from itemloaders.processors import Identity, Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def limpiar_precio(valor: str) -> Optional[Decimal]:
    """Convierte un precio de Cúspide a Decimal.

    Acepta el formato del JSON-LD ('29500.00') y el del HTML
    ('$ 29.500,00', con espacio no separable). Devuelve None si el texto
    no contiene un número, para que el loader lo descarte.
    """
    texto = str(valor).replace('$', '').replace('\xa0', '').strip()
    if not texto:
        return None
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def normalizar_espacios(texto: str) -> Optional[str]:
    """Reduce espacios, tabulaciones y saltos de línea a un solo espacio.

    Devuelve None si el texto queda vacío, para que el loader lo descarte.
    """
    limpio = ' '.join(str(texto).split())
    return limpio or None


def limpiar_forma_pago(linea: str) -> Optional[str]:
    """Extrae el nombre de una forma de pago del popup de Cúspide.

    Solo considera las líneas que empiezan con '>' y conserva el texto
    anterior a ':' (por ejemplo, 'Tarjetas de créditos').
    """
    linea = str(linea).strip()
    if not linea.startswith('>'):
        return None
    nombre = linea.lstrip('> ').split(':')[0].strip()
    return nombre or None


def sin_duplicados(valores: Iterable[str]) -> list[str]:
    """Elimina valores repetidos conservando el orden original."""
    return list(dict.fromkeys(valores))


class CuspideItem(scrapy.Item):
    """Datos de un resultado de búsqueda de Cúspide para un libro propio."""

    libro_id = scrapy.Field()
    titulo_buscado = scrapy.Field()
    isbn_catalogo = scrapy.Field()
    posicion = scrapy.Field()
    titulo_web = scrapy.Field()
    url = scrapy.Field()
    isbn_web = scrapy.Field()
    precio = scrapy.Field()
    moneda = scrapy.Field()
    imagen_url = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    fecha_extraccion = scrapy.Field()


class CuspideLoader(ItemLoader):
    """Loader que limpia y normaliza los datos de un CuspideItem.

    Por defecto normaliza espacios a la entrada y toma el primer valor a la
    salida. Los campos con reglas propias las definen con los sufijos _in
    (procesador de entrada) y _out (procesador de salida).
    """

    default_item_class = CuspideItem
    default_input_processor = MapCompose(normalizar_espacios)
    default_output_processor = TakeFirst()

    libro_id_in = Identity()
    posicion_in = Identity()
    precio_in = MapCompose(limpiar_precio)
    formas_pago_in = MapCompose(limpiar_forma_pago)
    formas_pago_out = sin_duplicados
    descripcion_out = Join(' ')
