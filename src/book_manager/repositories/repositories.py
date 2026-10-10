"""Repositorios de persistencia del dominio Book Manager."""
import abc
import datetime
from typing import TypeVar, Generic, List, Optional

from book_manager.entities.entities import EntidadBase, Stock, CotizacionDolar

T = TypeVar('T', bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en el repositorio.
        Args:
            entidad (T): la entidad a crear.
        Returns:
            T: La entidad creada
        Raises:
            ValueError: Si ya existe una entidad con el mismo ID"""
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad del repositorio por su ID
        Args:
            id(int): El ID de la entidad a leer
        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio
        Returns:
            List[T]: Una Lista de todas las entidades"""
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en el repositorio
        Args:
            entidad(T): La entidad a actualizar (debe tener un ID existente)
        Returns:
            T: La entidad actualizada"""
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad del repositorio por su ID
        Args:
            id (int): El ID de la entidad a eliminar
        Returns:
            bool: True si la entidad fue borrada, False si no se encontró"""
        pass


class RepositorioGenerico(IRepositorio[T]):
    """Implementación en memoria del CRUD básico para cualquier entidad.
    Puede reutilizarse con cualquier entidad que tenga id.
    """

    def __init__(self) -> None:
        self.__datos: dict[int, T] = {}

    def crear(self, entidad: T) -> T:
        """Guarda la entidad en el diccionario interno, indexada por su id"""
        if entidad.id in self.__datos:
            raise ValueError(f'Ya existe una entidad con el id {entidad.id}')
        self.__datos[entidad.id] = entidad
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        """Busca la entidad por id en el diccionario interno"""
        return self.__datos.get(id)

    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades almacenadas, sin orden garantizado."""
        return list(self.__datos.values())

    def actualizar(self, entidad: T) -> T:
        """Reemplaza la entidad existente por la nueva versión recibida."""
        if entidad.id not in self.__datos:
            raise ValueError(
                f'No existe una entidad con id {entidad.id} para actualizar')
        self.__datos[entidad.id] = entidad
        return entidad

    def eliminar(self, id: int) -> bool:
        """Quita la entidad del diccionario interno si existe."""
        if id in self.__datos:
            del self.__datos[id]
            return True
        return False


class IRepositorioStock(abc.ABC):
    """Interfaz para el repositorio del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.
        Args:
            stock (Stock): El objeto Stock a crear.
        Returns:
            Stock: El objeto Stock creado.
        Raises:
            ValueError: Si ya existe stock para el mismo libro."""
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.
        Args:
           libro_id (int): El ID del libro asociado al stock.
        Returns:
           Optional[Stock]: El objeto Stock si se encuentra, None en
             caso contrario."""
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.
        Args:
            stock (Stock): El objeto Stock a actualizar
            (debe tener un libro_id existente)
        Returns:
            Stock: El objeto Stock actualizado.
        Raises:
            ValueError: Si no se encuentra el stock para actualizar.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.
        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.
        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.
        """
        pass


class RepositorioStock (IRepositorioStock):
    """Implementación en memoria del repositorio de Stock, por Libro."""

    def __init__(self) -> None:
        self.__datos: dict[int, Stock] = {}

    def crear(self, stock: Stock) -> Stock:
        """Guarda el stock indexado por el id del libro asociado."""
        libro_id = stock.libro.id
        if libro_id in self.__datos:
            raise ValueError(
                f'Ya existe un registro de Stock del libro {libro_id}')
        self.__datos[libro_id] = stock
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Busca el stock asociado a un libro por su id"""
        return self.__datos.get(libro_id)

    def actualizar(self, stock: Stock) -> Stock:
        """Reemplaza el stock del libro por la nueva versión recibida."""
        libro_id = stock.libro.id
        if libro_id not in self.__datos:
            raise ValueError(
                f'No existe stock para el libro {libro_id} '
                'que se pueda actualizar')
        self.__datos[libro_id] = stock
        return stock

    def eliminar(self, libro_id: int) -> bool:
        """Quita el registro de stock del libro si existe"""
        if libro_id in self.__datos:
            del self.__datos[libro_id]
            return True
        return False


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo CotizacionDolar"""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.
        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.
        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.
        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y fecha.
        """
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
            self, tipo_id: int,
            fecha: datetime.date) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.
        Args:
            tipo_id (int): El ID del tipo de cotización
            (e.g., 'Oficial', 'Blue').
            fecha (datetime.date): La fecha de la cotización.
        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra,
            None en caso contrario.
        """
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico.
        Args:
            tipo_id (int): El ID del tipo de cotización.
        Returns:
            List[CotizacionDolar]: Cotizaciones históricas del tipo.
        """
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.
        Args:
            cotizacion (CotizacionDolar): La Cotizacion a actualizar.
        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.
        """
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.
        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (datetime.date): La fecha de la cotización a eliminar.
        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """
        pass


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Implementación en memoria del repositorio de CotizacionDolar.

    Indexa las cotizaciones por la clave compuesta (tipo_id, fecha).
    """

    def __init__(self) -> None:
        self.__datos: dict[tuple[int, datetime.date], CotizacionDolar] = {}

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Guarda la cotización indexada por (tipo_id, fecha)"""
        clave = (cotizacion.tipo_cotizacion.id, cotizacion.fecha)
        if clave in self.__datos:
            raise ValueError(
                'Ya existe una cotización para ese tipo de dolar y fecha')
        self.__datos[clave] = cotizacion
        return cotizacion

    def leer_por_tipo_y_fecha(
            self, tipo_id: int,
            fecha: datetime.date) -> Optional[CotizacionDolar]:
        """Busca y lee la cotización por la clave compuesta (tipo_id, fecha)"""
        return self.__datos.get((tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Busca y filtra las cotizaciones registradas de un tipo."""
        return [
            c for c in self.__datos.values()
            if c.tipo_cotizacion.id == tipo_id
        ]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Reemplaza la cotización existente de esa clave por la nueva"""
        clave = (cotizacion.tipo_cotizacion.id, cotizacion.fecha)
        if clave not in self.__datos:
            raise ValueError(
                'No existe una cotización para ese tipo de dólar '
                'en esa fecha para actualizar')
        self.__datos[clave] = cotizacion
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Quita la cotización de esa clave compuesta si existe"""
        clave = (tipo_id, fecha)
        if clave in self.__datos:
            del self.__datos[clave]
            return True
        return False
