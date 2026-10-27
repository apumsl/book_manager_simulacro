"""Servicios con la lógica de negocio de Book Manager."""
import csv
import json
import os
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

import requests
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from book_manager.entities.entities import (
    Auditoria,
    CotizacionDolar,
    EntidadBase,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    IRepositorio,
    IRepositorioCotizacionDolar,
    IRepositorioStock,
)

load_dotenv()

T = TypeVar('T', bound=EntidadBase)


class ServicioGenerico(Generic[T]):
    """Servicio base con el CRUD y reglas de negocio.

    Las clases hijas redefinen _validar y _validar_eliminacion para
    aplicar las reglas propias de cada entidad.
    """

    def __init__(self, repositorio: IRepositorio[T]) -> None:
        self._repositorio = repositorio

    def crear(self, entidad: T) -> T:
        """Valida las reglas de negocio y crea la entidad."""
        self._validar(entidad)
        return self._repositorio.crear(entidad)

    def buscar_por_id(self, id: int) -> Optional[T]:
        """Busca una entidad por su id."""
        return self._repositorio.leer_por_id(id)

    def listar(self) -> List[T]:
        """Devuelve todas las entidades."""
        return self._repositorio.leer_todos()

    def actualizar(self, entidad: T) -> T:
        """Valida las reglas de negocio y actualiza la entidad."""
        self._validar(entidad)
        return self._repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Valida que se pueda eliminar y borra la entidad por su id."""
        self._validar_eliminacion(id)
        return self._repositorio.eliminar(id)

    def _validar(self, entidad: T) -> None:
        """Reglas al crear o actualizar. Por defecto no valida nada."""

    def _validar_eliminacion(self, id: int) -> None:
        """Reglas al eliminar. Por defecto no valida nada."""


class ServicioGenero(ServicioGenerico[Genero]):
    """Reglas de negocio de los géneros."""

    def __init__(self, repo_generos: IRepositorio[Genero],
                 repo_libros: IRepositorio[Libro]) -> None:
        super().__init__(repo_generos)
        self.__repo_libros = repo_libros

    def _validar(self, entidad: Genero) -> None:
        """El nombre del género no puede estar vacío."""
        if not entidad.nombre.strip():
            raise ValueError('El nombre del género no puede estar vacío')

    def _validar_eliminacion(self, id: int) -> None:
        """No se puede eliminar un género que tiene libros asociados."""
        for libro in self.__repo_libros.leer_todos():
            if libro.genero.id == id:
                raise ValueError(
                    'No se puede eliminar el género: tiene libros asociados')


class ServicioEditorial(ServicioGenerico[Editorial]):
    """Reglas de negocio de las editoriales."""

    def __init__(self, repo_editoriales: IRepositorio[Editorial],
                 repo_libros: IRepositorio[Libro]) -> None:
        super().__init__(repo_editoriales)
        self.__repo_libros = repo_libros

    def _validar(self, entidad: Editorial) -> None:
        """El nombre de la editorial no puede estar vacío."""
        if not entidad.nombre.strip():
            raise ValueError('El nombre de la editorial no puede estar vacío')

    def _validar_eliminacion(self, id: int) -> None:
        """No se puede eliminar una editorial que tiene libros asociados."""
        for libro in self.__repo_libros.leer_todos():
            if libro.editorial.id == id:
                raise ValueError(
                    'No se puede eliminar la editorial: '
                    'tiene libros asociados')


class ServicioMoneda(ServicioGenerico[Moneda]):
    """Reglas de negocio de las monedas."""

    def __init__(self, repo_monedas: IRepositorio[Moneda],
                 repo_precios: IRepositorio[Precio]) -> None:
        super().__init__(repo_monedas)
        self.__repo_precios = repo_precios

    def _validar(self, entidad: Moneda) -> None:
        """El código y el nombre de la moneda no pueden estar vacíos."""
        if not entidad.codigo.strip() or not entidad.nombre.strip():
            raise ValueError(
                'El código y el nombre de la moneda no pueden estar vacíos')

    def _validar_eliminacion(self, id: int) -> None:
        """No se puede eliminar una moneda que tiene precios asociados."""
        for precio in self.__repo_precios.leer_todos():
            if precio.moneda.id == id:
                raise ValueError(
                    'No se puede eliminar la moneda: tiene precios asociados')


class ServicioTipoCotizacion(ServicioGenerico[TipoCotizacion]):
    """Reglas de negocio de los tipos de cotización."""

    def __init__(self, repo_tipos: IRepositorio[TipoCotizacion],
                 repo_cotizaciones: IRepositorioCotizacionDolar) -> None:
        super().__init__(repo_tipos)
        self.__repo_cotizaciones = repo_cotizaciones

    def _validar(self, entidad: TipoCotizacion) -> None:
        """El nombre del tipo de cotización no puede estar vacío."""
        if not entidad.nombre.strip():
            raise ValueError(
                'El nombre del tipo de cotización no puede estar vacío')

    def _validar_eliminacion(self, id: int) -> None:
        """No se puede eliminar un tipo que tiene cotizaciones asociadas."""
        if self.__repo_cotizaciones.leer_historico_por_tipo(id):
            raise ValueError(
                'No se puede eliminar el tipo de cotización: '
                'tiene cotizaciones asociadas')


class ServicioLibro(ServicioGenerico[Libro]):
    """Reglas de negocio de los libros."""

    def __init__(self, repo_libros: IRepositorio[Libro],
                 repo_precios: IRepositorio[Precio],
                 repo_stock: IRepositorioStock) -> None:
        super().__init__(repo_libros)
        self.__repo_precios = repo_precios
        self.__repo_stock = repo_stock

    def _validar(self, entidad: Libro) -> None:
        """El ISBN y el título son obligatorios y el ISBN es único."""
        if not entidad.isbn.strip():
            raise ValueError('El ISBN no puede estar vacío')
        if not entidad.titulo.strip():
            raise ValueError('El título no puede estar vacío')
        for otro in self._repositorio.leer_todos():
            if otro.isbn == entidad.isbn and otro.id != entidad.id:
                raise ValueError(
                    f'Ya existe un libro con el ISBN {entidad.isbn}')

    def _validar_eliminacion(self, id: int) -> None:
        """No se puede eliminar un libro con precios o stock asociados."""
        for precio in self.__repo_precios.leer_todos():
            if precio.libro.id == id:
                raise ValueError(
                    'No se puede eliminar el libro: tiene precios asociados')
        if self.__repo_stock.leer_por_libro(id) is not None:
            raise ValueError(
                'No se puede eliminar el libro: tiene stock asociado')


class ServicioPrecio(ServicioGenerico[Precio]):
    """Reglas de negocio de los precios."""

    def _validar(self, entidad: Precio) -> None:
        """El monto del precio debe ser mayor a cero."""
        if entidad.monto <= 0:
            raise ValueError('El monto del precio debe ser mayor a cero')


class ServicioStock:
    """Reglas de negocio del stock, indexado por libro."""

    def __init__(self, repositorio: IRepositorioStock) -> None:
        self.__repositorio = repositorio

    def crear(self, stock: Stock) -> Stock:
        """Valida las reglas de negocio y crea el registro de stock."""
        self.__validar(stock)
        return self.__repositorio.crear(stock)

    def buscar_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Busca el stock correspondiente a un libro."""
        return self.__repositorio.leer_por_libro(libro_id)

    def actualizar(self, stock: Stock) -> Stock:
        """Valida las reglas de negocio y actualiza el stock."""
        self.__validar(stock)
        return self.__repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock correspondiente a un libro."""
        return self.__repositorio.eliminar(libro_id)

    def __validar(self, stock: Stock) -> None:
        """La cantidad en stock no puede ser negativa."""
        if stock.cantidad < 0:
            raise ValueError('La cantidad en stock no puede ser negativa')


class ServicioCotizacionDolar:
    """Reglas de negocio de las cotizaciones del dólar."""

    def __init__(self, repositorio: IRepositorioCotizacionDolar,
                 repo_tipos: IRepositorio[TipoCotizacion]) -> None:
        self.__repositorio = repositorio
        self.__repo_tipos = repo_tipos

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Valida las reglas de negocio y crea la cotización."""
        self.__validar(cotizacion)
        return self.__repositorio.crear(cotizacion)

    def buscar_por_tipo_y_fecha(
            self, tipo_id: int,
            fecha: date) -> Optional[CotizacionDolar]:
        """Busca una cotización por tipo y fecha."""
        return self.__repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)

    def listar_historico(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve el histórico de cotizaciones de un tipo."""
        return self.__repositorio.leer_historico_por_tipo(tipo_id)

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Valida las reglas de negocio y actualiza la cotización."""
        self.__validar(cotizacion)
        return self.__repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización según su tipo y fecha."""
        return self.__repositorio.eliminar(tipo_id, fecha)

    def obtener_cotizaciones(self) -> List[CotizacionDolar]:
        """Obtiene las cotizaciones de la API y las guarda en la BD."""
        api_url = os.getenv('API_URL')
        if not api_url:
            raise ValueError('No se encontró API_URL en el archivo .env')

        try:
            respuesta = requests.get(api_url, timeout=10)
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ValueError(
                f'Error al consultar la API del dólar: {error}') from error

        datos = respuesta.json()
        cotizaciones_guardadas = []
        tipos = self.__repo_tipos.leer_todos()
        siguiente_id = max((tipo.id for tipo in tipos), default=0) + 1

        equivalencias = {
            'bolsa': 'mep',
            'contado con liquidación': 'ccl'
        }

        for dato in datos:
            nombre_api = dato['nombre'].lower()
            nombre_tipo = equivalencias.get(nombre_api, nombre_api)
            tipo = next(
                (t for t in tipos
                 if t.nombre.lower() == nombre_tipo),
                None)

            if tipo is None:
                tipo = TipoCotizacion(
                    id=siguiente_id,
                    nombre=dato['nombre'])
                tipo = self.__repo_tipos.crear(tipo)
                tipos.append(tipo)
                siguiente_id += 1

            fecha = datetime.fromisoformat(
                dato['fechaActualizacion'].replace('Z', '+00:00')).date()

            existente = self.__repositorio.leer_por_tipo_y_fecha(
                tipo.id, fecha)

            if existente:
                cotizacion = CotizacionDolar(
                    id=existente.id,
                    tipo_cotizacion=tipo,
                    fecha=fecha,
                    valor_compra=float(dato['compra']),
                    valor_venta=float(dato['venta']))

                cotizacion = self.actualizar(cotizacion)
            else:
                cotizacion = CotizacionDolar(
                    id=0,
                    tipo_cotizacion=tipo,
                    fecha=fecha,
                    valor_compra=float(dato['compra']),
                    valor_venta=float(dato['venta']))

                cotizacion = self.crear(cotizacion)

            cotizaciones_guardadas.append(cotizacion)

        return cotizaciones_guardadas

    def __validar(self, cotizacion: CotizacionDolar) -> None:
        """Los valores deben ser positivos y compra no mayor a venta."""
        if cotizacion.valor_compra <= 0 or cotizacion.valor_venta <= 0:
            raise ValueError('Los valores de la cotización deben ser '
                             'mayores a cero')
        if cotizacion.valor_compra > cotizacion.valor_venta:
            raise ValueError('El valor de compra no puede ser mayor '
                             'al de venta')


class ServicioAuditoria(ServicioGenerico[Auditoria]):
    """Reglas de negocio de los registros de auditoría."""

    def registrar(self, accion: str, detalles: str) -> Auditoria:
        """Crea un registro de auditoría con la fecha actual."""
        return self.crear(Auditoria(id=0, accion=accion,
                                    fecha=datetime.now(),
                                    detalles=detalles))

    def _validar(self, entidad: Auditoria) -> None:
        """La acción registrada no puede estar vacía."""
        if not entidad.accion.strip():
            raise ValueError('La acción de auditoría no puede estar vacía')


CAMPOS_ALERTA: List[str] = [
    'libro_id', 'libro', 'precio_interno', 'precio_web', 'diferencia',
    'umbral', 'situacion', 'criterio', 'titulo_web', 'url',
    'fecha_extraccion',
]


class ServicioAlertasPrecio:
    """Compara el precio interno de cada libro con el precio web.

    Genera una alerta cuando la diferencia, en valor absoluto, supera el
    monto en pesos que ingresa el usuario antes de ejecutar el scraper.
    """

    def __init__(self, repo_precios: IRepositorio[Precio],
                 carpeta_reportes: Path) -> None:
        """Inicializa el servicio de alertas de precio.

        Args:
            repo_precios: Repositorio para acceder a los precios históricos.
            carpeta_reportes: Ruta a la carpeta donde se guardarán los reportes.
        """
        self.__repo_precios: IRepositorio[Precio] = repo_precios
        self.__carpeta_reportes: Path = Path(carpeta_reportes)
        self.sin_coincidencia: List[str] = []

    @staticmethod
    def validar_diferencia(valor: Any) -> Decimal:
        """Convierte el monto ingresado por el usuario en un Decimal.

        Acepta '5000', '5000.50' o '5.000,50'.

        Raises:
            ValueError: Si el valor no es un número mayor a cero.
        """
        texto = str(valor).replace('$', '').replace(' ', '').strip()
        if ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        try:
            monto = Decimal(texto)
        except InvalidOperation:
            raise ValueError(
                f'La diferencia "{valor}" no es un número válido') from None
        if monto <= 0:
            raise ValueError('La diferencia debe ser mayor a cero')
        return monto

    def precios_internos_ars(self) -> Dict[int, Decimal]:
        """Devuelve el precio en pesos vigente de cada libro.

        Si un libro tiene varios precios en ARS, toma el de fecha de
        vigencia más reciente.

        Returns:
            Dict[int, Decimal]: Precio interno indexado por id de libro.
        """
        vigentes: Dict[int, Precio] = {}
        for precio in self.__repo_precios.leer_todos():
            if precio.moneda.codigo != 'ARS':
                continue
            actual = vigentes.get(precio.libro.id)
            if actual is None or precio.fecha_vigencia > actual.fecha_vigencia:
                vigentes[precio.libro.id] = precio
        return {libro_id: Decimal(str(precio.monto))
                for libro_id, precio in vigentes.items()}

    @staticmethod
    def _normalizar_titulo(titulo: Any) -> str:
        """Pasa el título a minúsculas, sin tildes ni signos de puntuación."""
        texto = unicodedata.normalize('NFKD', str(titulo or ''))
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        texto = re.sub(r'[^a-z0-9 ]', ' ', texto.lower())
        return ' '.join(texto.split())

    @classmethod
    def elegir_resultado(cls, titulo: str, resultados: List[Dict[str, Any]]
                         ) -> Tuple[Optional[Dict[str, Any]], str]:
        """Elige contra qué resultado web comparar un libro.

        Primero busca un resultado con el mismo título; si no hay, uno cuyo
        título empiece con el del catálogo, como palabras completas (por
        ejemplo, 'El Principito (tapa dura)'). Si ninguno coincide, no
        compara, para no alertar con un libro distinto.

        Returns:
            Tuple: El resultado elegido (o None) y el criterio usado.
        """
        buscado = cls._normalizar_titulo(titulo)
        ordenados = sorted(resultados,
                           key=lambda r: r.get('posicion') or 0)
        titulos = [(r, cls._normalizar_titulo(r.get('titulo_web')))
                   for r in ordenados]
        for resultado, titulo_web in titulos:
            if titulo_web == buscado:
                return resultado, 'título exacto'
        for resultado, titulo_web in titulos:
            if buscado and f'{titulo_web} '.startswith(f'{buscado} '):
                return resultado, 'título ampliado'
        return None, 'sin coincidencia'

    def generar_alertas(self, libros: List[Dict[str, Any]],
                        resultados: List[Dict[str, Any]],
                        diferencia: Decimal) -> List[Dict[str, Any]]:
        """Compara precio interno y precio web y arma las alertas.

        Args:
            libros: Libros del catálogo (id, titulo y precio_interno).
            resultados: Ítems obtenidos por el scraper.
            diferencia: Monto en pesos a partir del cual se alerta.

        Returns:
            List[Dict[str, Any]]: Una alerta por cada libro que supera
            la diferencia.
        """
        self.sin_coincidencia = []
        por_libro: Dict[int, List[Dict[str, Any]]] = {}
        for resultado in resultados:
            por_libro.setdefault(resultado.get('libro_id'), []).append(
                resultado)

        alertas: List[Dict[str, Any]] = []
        for libro in libros:
            precio_interno = libro.get('precio_interno')
            if precio_interno is None:
                continue
            elegido, criterio = self.elegir_resultado(
                libro['titulo'], por_libro.get(libro['id'], []))
            if elegido is None or elegido.get('precio') is None:
                self.sin_coincidencia.append(libro['titulo'])
                continue
            precio_web = Decimal(str(elegido['precio']))
            delta = precio_web - precio_interno
            if abs(delta) <= diferencia:
                continue
            alertas.append({
                'libro_id': libro['id'],
                'libro': libro['titulo'],
                'precio_interno': f'{precio_interno:.2f}',
                'precio_web': f'{precio_web:.2f}',
                'diferencia': f'{delta:.2f}',
                'umbral': f'{diferencia:.2f}',
                'situacion': ('web más cara' if delta > 0
                              else 'web más barata'),
                'criterio': criterio,
                'titulo_web': elegido.get('titulo_web', ''),
                'url': elegido.get('url', ''),
                'fecha_extraccion': elegido.get('fecha_extraccion', ''),
            })
        return alertas

    def exportar_csv(self, alertas: List[Dict[str, Any]]) -> Path:
        """Escribe las alertas en un CSV nuevo dentro de reportes/.

        El nombre lleva fecha y hora para que cada ejecución genere su
        propio archivo. Se crea aunque no haya alertas.

        Returns:
            Path: Ruta del archivo generado.
        """
        self.__carpeta_reportes.mkdir(parents=True, exist_ok=True)
        marca = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        ruta = self.__carpeta_reportes / f'alertas_precios_{marca}.csv'
        with open(ruta, 'w', encoding='utf-8-sig', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_ALERTA,
                                      delimiter=';')
            escritor.writeheader()
            escritor.writerows(alertas)
        return ruta


CARPETA_REPORTES: Path = Path(__file__).resolve().parents[1] / 'reportes'
COLUMNAS_REPORTE: List[Tuple[str, int]] = [
    ('Libro', 32), ('Precio interno', 16), ('Precio web', 16),
    ('Diferencia', 16), ('Fecha de extracción', 22), ('Coincidencia', 18),
]


class ServicioReportePrecios:
    """Genera el reporte Excel que compara precio interno y precio web.

    Toma los resultados de la última ejecución del scraper
    (resultados_cuspide.json) y arma una fila por cada libro del catálogo.
    """

    def __init__(self, repo_libros: IRepositorio[Libro],
                 servicio_alertas: ServicioAlertasPrecio,
                 carpeta_reportes: Path = CARPETA_REPORTES) -> None:
        """Inicializa el generador de reportes de precios en Excel.

        Args:
            repo_libros: Repositorio para acceder a los datos de los libros.
            servicio_alertas: Instancia del servicio de alertas.
            carpeta_reportes: Ruta de la carpeta de reportes (por defecto CARPETA_REPORTES).
        """
        self.__repo_libros: IRepositorio[Libro] = repo_libros
        self.__servicio_alertas: ServicioAlertas