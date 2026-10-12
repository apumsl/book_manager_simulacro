"""Servicios con la lógica de negocio de Book Manager."""
import os
import requests
from datetime import date,datetime
from typing import Generic, List, Optional, TypeVar
from dotenv import load_dotenv



load_dotenv()

from book_manager.entities.entities import (
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

        for dato in datos:
            tipo = next(
                (t for t in tipos
                 if t.nombre.lower() == dato['nombre'].lower()),
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
