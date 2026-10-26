"""Spider que obtiene de Cúspide los datos de los libros del catálogo."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Iterator, Optional
from urllib.parse import urlencode

import scrapy
from dotenv import load_dotenv
from scrapy.http import Response

from book_manager.database.connection import ConexionDB
from book_manager.repositories.repositories import (
    RepositorioLibro,
    RepositorioPrecio,
    RepositorioStock,
)
from book_manager.services.services import (
    ServicioAlertasPrecio,
    ServicioLibro,
)

from cuspide.items import CuspideItem, CuspideLoader


URL_BUSQUEDA = 'https://www.cuspide.com/'
MAX_RESULTADOS = 10

SELECTOR_TARJETA = 'div.product-small.col.type-product'
SELECTOR_LINK = "a[href*='/producto/']::attr(href)"
SELECTOR_PRECIO = '.product-page-price ::text'
SELECTOR_IMAGEN = '.woocommerce-product-gallery img::attr(src)'
SELECTOR_FORMAS_PAGO = '#pum-945 ::text'
SELECTOR_SINOPSIS = (
    "//*[normalize-space(text())='Sinopsis del producto']"
    "/following-sibling::*[1]//text()"
)
SELECTOR_JSON_LD = "script[type='application/ld+json']::text"
CARPETA_REPORTES = Path(__file__).resolve().parents[3] / 'reportes'


class CuspideSpider(scrapy.Spider):
    """Busca en Cúspide los libros existentes en el catálogo propio.

    Los libros se obtienen directamente desde la base de datos.

    Por cada libro se realiza una búsqueda por título y se recorren
    como máximo los primeros 10 resultados encontrados.

    De cada producto se obtiene:
    - título,
    - ISBN,
    - precio,
    - moneda,
    - imagen,
    - formas de pago,
    - descripción,
    - URL,
    - fecha de extracción.
    """

    name = 'cuspide'
    allowed_domains = ['cuspide.com']

    def __init__(
        self,
        *args: Any,
        diferencia: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Pide la diferencia de precios y carga los libros del catálogo.

        Args:
            diferencia: Monto en pesos a partir del cual se genera una
                alerta. Se puede pasar con ``-a diferencia=5000``; si no
                se pasa, se le pide al usuario por consola.
        """
        super().__init__(*args, **kwargs)

        if diferencia is None:
            diferencia = input(
                'Diferencia de precio en pesos para generar alertas: ')
        self.diferencia = ServicioAlertasPrecio.validar_diferencia(
            diferencia)

        load_dotenv()

        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            raise ValueError(
                'No se encontró DATABASE_URL en el archivo .env.'
            )

        self.conexion = ConexionDB(database_url)

        repo_libros = RepositorioLibro(self.conexion)
        repo_precios = RepositorioPrecio(self.conexion)
        repo_stock = RepositorioStock(self.conexion)

        servicio_libros = ServicioLibro(
            repo_libros,
            repo_precios,
            repo_stock
        )

        libros = servicio_libros.listar()

        self.servicio_alertas = ServicioAlertasPrecio(
            repo_precios,
            CARPETA_REPORTES
        )
        precios_internos = self.servicio_alertas.precios_internos_ars()

        self.libros = [
            {
                'id': libro.id,
                'titulo': libro.titulo,
                'isbn': libro.isbn,
                'precio_interno': precios_internos.get(libro.id)
            }
            for libro in libros
        ]

        self.logger.info(
            'Se cargaron %d libros desde la base de datos.',
            len(self.libros)
        )

    async def start(
        self
    ) -> AsyncIterator[scrapy.Request]:
        """Genera una búsqueda por título para cada libro del catálogo."""
        for libro in self.libros:

            titulo = str(
                libro.get('titulo', '')
            ).strip()

            if not titulo:
                continue

            consulta = urlencode(
                {
                    's': titulo,
                    'post_type': 'product'
                }
            )

            yield scrapy.Request(
                f'{URL_BUSQUEDA}?{consulta}',
                callback=self.parse_busqueda,
                cb_kwargs={
                    'libro': libro
                },
                dont_filter=True
            )

    def parse_busqueda(
        self,
        response: Response,
        libro: dict[str, Any]
    ) -> Iterator[scrapy.Request]:
        """Sigue los primeros resultados de búsqueda de un libro.

        Args:
            response: Página de resultados de Cúspide.
            libro: Libro del catálogo que originó la búsqueda.
        """
        tarjetas = response.css(
            SELECTOR_TARJETA
        )[:MAX_RESULTADOS]

        self.logger.info(
            '"%s": %d resultados tomados',
            libro.get('titulo'),
            len(tarjetas)
        )

        for posicion, tarjeta in enumerate(
            tarjetas,
            start=1
        ):
            url = tarjeta.css(
                SELECTOR_LINK
            ).get()

            if url:
                yield response.follow(
                    url,
                    callback=self.parse_producto,
                    cb_kwargs={
                        'libro': libro,
                        'posicion': posicion
                    },
                    dont_filter=True
                )

    def parse_producto(
        self,
        response: Response,
        libro: dict[str, Any],
        posicion: int
    ) -> Iterator[CuspideItem]:
        """Extrae los datos de la ficha de un producto.

        El precio, título e ISBN se intentan obtener primero
        desde el JSON-LD.

        Si alguno de estos datos no está disponible,
        también se utilizan selectores HTML como respaldo.

        Args:
            response: Página de detalle del producto.
            libro: Libro del catálogo que originó la búsqueda.
            posicion: Posición del producto entre los resultados.
        """
        loader = CuspideLoader(
            response=response
        )

        loader.add_value(
            'libro_id',
            libro.get('id')
        )

        loader.add_value(
            'titulo_buscado',
            libro.get('titulo')
        )

        loader.add_value(
            'isbn_catalogo',
            libro.get('isbn')
        )

        loader.add_value(
            'posicion',
            posicion
        )

        loader.add_value(
            'url',
            response.url
        )

        loader.add_value(
            'fecha_extraccion',
            datetime.now().isoformat(
                timespec='seconds'
            )
        )

        producto = self._producto_json_ld(
            response
        )

        oferta = self._primera_oferta(
            producto
        )

        loader.add_value(
            'titulo_web',
            producto.get('name')
        )

        loader.add_value(
            'isbn_web',
            producto.get('sku')
        )

        loader.add_value(
            'precio',
            oferta.get('price')
        )

        loader.add_value(
            'moneda',
            oferta.get('priceCurrency')
        )

        loader.add_css(
            'titulo_web',
            'h1::text'
        )

        loader.add_css(
            'precio',
            SELECTOR_PRECIO
        )

        loader.add_css(
            'imagen_url',
            SELECTOR_IMAGEN
        )

        loader.add_css(
            'formas_pago',
            SELECTOR_FORMAS_PAGO
        )

        loader.add_xpath(
            'descripcion',
            SELECTOR_SINOPSIS
        )

        yield loader.load_item()

    @staticmethod
    def _producto_json_ld(
        response: Response
    ) -> dict[str, Any]:
        """Devuelve el nodo Product del JSON-LD de la página.

        Returns:
            dict: Datos del producto o diccionario vacío
            si no se encuentra.
        """
        bloques = response.css(
            SELECTOR_JSON_LD
        ).getall()

        for bloque in bloques:
            try:
                datos = json.loads(
                    bloque
                )
            except json.JSONDecodeError:
                continue

            documentos = (
                datos
                if isinstance(datos, list)
                else [datos]
            )

            for documento in documentos:

                if not isinstance(
                    documento,
                    dict
                ):
                    continue

                nodos = documento.get(
                    '@graph',
                    [documento]
                )

                productos = [
                    nodo
                    for nodo in nodos
                    if isinstance(nodo, dict)
                    and nodo.get('@type') == 'Product'
                ]

                if productos:
                    return productos[0]

        return {}

    @staticmethod
    def _primera_oferta(
        producto: dict[str, Any]
    ) -> dict[str, Any]:
        """Devuelve la primera oferta del producto."""
        ofertas = producto.get(
            'offers',
            {}
        )

        if isinstance(
            ofertas,
            list
        ):
            return (
                ofertas[0]
                if ofertas
                else {}
            )

        if isinstance(
            ofertas,
            dict
        ):
            return ofertas

        return {}

    def closed(
        self,
        reason: str
    ) -> None:
        """Cierra la conexión a la base cuando termina el spider."""
        if hasattr(
            self,
            'conexion'
        ):
            self.conexion.cerrar()

        self.logger.info(
            'Spider finalizado. Motivo: %s',
            reason
        )
