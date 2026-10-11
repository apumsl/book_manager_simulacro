"""Repositorios de persistencia del dominio Book Manager."""
import abc
import datetime
from typing import TypeVar, Generic, List, Optional

from book_manager.entities.entities import EntidadBase, Stock, CotizacionDolar
from pathlib import Path
from book_manager.repositories.almacen_csv import escribir_csv, leer_csv
from book_manager.entities.entities import (
    CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda, Precio,
    Stock, TipoCotizacion)


T = TypeVar('T', bound=EntidadBase)


def _a_fecha(texto: str) -> datetime.date:
    """Convierte un texto con formato AAAA-MM-DD en un objeto date."""
    return datetime.datetime.strptime(texto, '%Y-%m-%d').date()


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
    """Implementación del CRUD básico para cualquier entidad.

    Si recibe una ruta, carga los datos desde un CSV al iniciar y lo
    reescribe después de cada cambio. Sin ruta, funciona solo en memoria.
    Las subclases definen CAMPOS, _a_fila y _desde_fila.
    """

    CAMPOS: List[str] = []

    def __init__(self, ruta: Optional[Path] = None) -> None:
        self.__datos: dict[int, T] = {}
        self._ruta = ruta
        self._cargar()

    def _a_fila(self, entidad: T) -> dict:
        """Convierte una entidad en una fila de CSV."""
        raise NotImplementedError

    def _desde_fila(self, fila: dict) -> T:
        """Convierte una fila de CSV en una entidad."""
        raise NotImplementedError

    def _cargar(self) -> None:
        """Carga las entidades desde el CSV, si hay ruta."""
        if self._ruta is None:
            return
        for fila in leer_csv(self._ruta):
            entidad = self._desde_fila(fila)
            self.__datos[entidad.id] = entidad

    def _guardar(self) -> None:
        """Reescribe el CSV con el estado actual, si hay ruta."""
        if self._ruta is None:
            return
        filas = [self._a_fila(e) for e in self.__datos.values()]
        escribir_csv(self._ruta, self.CAMPOS, filas)

    def crear(self, entidad: T) -> T:
        """Guarda la entidad en el diccionario interno, indexada por su id"""
        if entidad.id in self.__datos:
            raise ValueError(f'Ya existe una entidad con el id {entidad.id}')
        self.__datos[entidad.id] = entidad
        self._guardar()
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
        self._guardar()
        return entidad

    def eliminar(self, id: int) -> bool:
        """Quita la entidad del diccionario interno si existe."""
        if id in self.__datos:
            del self.__datos[id]
            self._guardar()
            return True
        return False


class RepositorioGenero(RepositorioGenerico[Genero]):
    """Repositorio de géneros, persistido en CSV."""

    CAMPOS = ['id', 'nombre']

    def _a_fila(self, entidad: Genero) -> dict:
        return {'id': entidad.id, 'nombre': entidad.nombre}

    def _desde_fila(self, fila: dict) -> Genero:
        return Genero(id=int(fila['id']), nombre=fila['nombre'])


class RepositorioEditorial(RepositorioGenerico[Editorial]):
    """Repositorio de editoriales, persistido en CSV."""

    CAMPOS = ['id', 'nombre', 'sede']

    def _a_fila(self, entidad: Editorial) -> dict:
        return {'id': entidad.id, 'nombre': entidad.nombre,
                'sede': entidad.sede}

    def _desde_fila(self, fila: dict) -> Editorial:
        return Editorial(id=int(fila['id']), nombre=fila['nombre'],
                         sede=fila['sede'])


class RepositorioMoneda(RepositorioGenerico[Moneda]):
    """Repositorio de monedas, persistido en CSV."""

    CAMPOS = ['id', 'codigo', 'nombre']

    def _a_fila(self, entidad: Moneda) -> dict:
        return {'id': entidad.id, 'codigo': entidad.codigo,
                'nombre': entidad.nombre}

    def _desde_fila(self, fila: dict) -> Moneda:
        return Moneda(id=int(fila['id']), codigo=fila['codigo'],
                      nombre=fila['nombre'])


class RepositorioTipoCotizacion(RepositorioGenerico[TipoCotizacion]):
    """Repositorio de tipos de cotización, persistido en CSV."""

    CAMPOS = ['id', 'nombre']

    def _a_fila(self, entidad: TipoCotizacion) -> dict:
        return {'id': entidad.id, 'nombre': entidad.nombre}

    def _desde_fila(self, fila: dict) -> TipoCotizacion:
        return TipoCotizacion(id=int(fila['id']), nombre=fila['nombre'])


class RepositorioLibro(RepositorioGenerico[Libro]):
    """Repositorio de libros, persistido en CSV.

    Guarda solo los ids de género y editorial. Al cargar, los busca en
    sus repositorios, que deben estar cargados antes.
    """

    CAMPOS = ['id', 'isbn', 'titulo', 'autor', 'genero_id', 'editorial_id']

    def __init__(self, repo_generos: IRepositorio[Genero],
                 repo_editoriales: IRepositorio[Editorial],
                 ruta: Optional[Path] = None) -> None:
        self._repo_generos = repo_generos
        self._repo_editoriales = repo_editoriales
        super().__init__(ruta)

    def _a_fila(self, entidad: Libro) -> dict:
        return {'id': entidad.id, 'isbn': entidad.isbn,
                'titulo': entidad.titulo, 'autor': entidad.autor,
                'genero_id': entidad.genero.id,
                'editorial_id': entidad.editorial.id}

    def _desde_fila(self, fila: dict) -> Libro:
        genero = self._repo_generos.leer_por_id(int(fila['genero_id']))
        if genero is None:
            raise ValueError(
                f"El libro {fila['id']} usa un género que no existe")
        editorial = self._repo_editoriales.leer_por_id(
            int(fila['editorial_id']))
        if editorial is None:
            raise ValueError(
                f"El libro {fila['id']} usa una editorial que no existe")
        return Libro(id=int(fila['id']), isbn=fila['isbn'],
                     titulo=fila['titulo'], autor=fila['autor'],
                     genero=genero, editorial=editorial)


class RepositorioPrecio(RepositorioGenerico[Precio]):
    """Repositorio de precios, persistido en CSV.

    Guarda solo los ids de libro y moneda. Al cargar, los busca en sus
    repositorios, que deben estar cargados antes.
    """

    CAMPOS = ['id', 'libro_id', 'moneda_id', 'monto', 'fecha_vigencia']

    def __init__(self, repo_libros: IRepositorio[Libro],
                 repo_monedas: IRepositorio[Moneda],
                 ruta: Optional[Path] = None) -> None:
        self._repo_libros = repo_libros
        self._repo_monedas = repo_monedas
        super().__init__(ruta)

    def _a_fila(self, entidad: Precio) -> dict:
        return {'id': entidad.id, 'libro_id': entidad.libro.id,
                'moneda_id': entidad.moneda.id, 'monto': entidad.monto,
                'fecha_vigencia': entidad.fecha_vigencia.strftime('%Y-%m-%d')}

    def _desde_fila(self, fila: dict) -> Precio:
        libro = self._repo_libros.leer_por_id(int(fila['libro_id']))
        if libro is None:
            raise ValueError(
                f"El precio {fila['id']} usa un libro que no existe")
        moneda = self._repo_monedas.leer_por_id(int(fila['moneda_id']))
        if moneda is None:
            raise ValueError(
                f"El precio {fila['id']} usa una moneda que no existe")
        return Precio(id=int(fila['id']), libro=libro, moneda=moneda,
                      monto=float(fila['monto']),
                      fecha_vigencia=_a_fecha(fila['fecha_vigencia']))


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


class RepositorioStock(IRepositorioStock):
    """Repositorio de Stock por libro, persistido en CSV."""

    CAMPOS = ['id', 'libro_id', 'cantidad']

    def __init__(self, repo_libros: IRepositorio[Libro],
                 ruta: Optional[Path] = None) -> None:
        self.__datos: dict[int, Stock] = {}
        self._repo_libros = repo_libros
        self._ruta = ruta
        self._cargar()

    def _cargar(self) -> None:
        """Carga el stock desde el CSV, si hay ruta."""
        if self._ruta is None:
            return
        for fila in leer_csv(self._ruta):
            libro = self._repo_libros.leer_por_id(int(fila['libro_id']))
            if libro is None:
                raise ValueError(
                    f"El stock {fila['id']} usa un libro que no existe")
            self.__datos[libro.id] = Stock(
                id=int(fila['id']), libro=libro,
                cantidad=int(fila['cantidad']))

    def _guardar(self) -> None:
        """Reescribe el CSV con el estado actual, si hay ruta."""
        if self._ruta is None:
            return
        filas = [
            {'id': s.id, 'libro_id': s.libro.id, 'cantidad': s.cantidad}
            for s in self.__datos.values()
        ]
        escribir_csv(self._ruta, self.CAMPOS, filas)

    def crear(self, stock: Stock) -> Stock:
        """Guarda el stock indexado por el id del libro asociado."""
        libro_id = stock.libro.id
        if libro_id in self.__datos:
            raise ValueError(
                f'Ya existe un registro de Stock del libro {libro_id}')
        self.__datos[libro_id] = stock
        self._guardar()
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
        self._guardar()
        return stock

    def eliminar(self, libro_id: int) -> bool:
        """Quita el registro de stock del libro si existe"""
        if libro_id in self.__datos:
            del self.__datos[libro_id]
            self._guardar()
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
    """Repositorio de CotizacionDolar, persistido en CSV.

    Indexa las cotizaciones por la clave compuesta (tipo_id, fecha).
    """

    CAMPOS = ['id', 'tipo_cotizacion_id', 'fecha', 'valor_compra',
              'valor_venta']

    def __init__(self, repo_tipos: IRepositorio[TipoCotizacion],
                 ruta: Optional[Path] = None) -> None:
        self.__datos: dict[tuple[int, datetime.date], CotizacionDolar] = {}
        self._repo_tipos = repo_tipos
        self._ruta = ruta
        self._cargar()

    def _cargar(self) -> None:
        """Carga las cotizaciones desde el CSV, si hay ruta."""
        if self._ruta is None:
            return
        for fila in leer_csv(self._ruta):
            tipo = self._repo_tipos.leer_por_id(
                int(fila['tipo_cotizacion_id']))
            if tipo is None:
                raise ValueError(
                    f"La cotización {fila['id']} usa un tipo que no existe")
            fecha = _a_fecha(fila['fecha'])
            self.__datos[(tipo.id, fecha)] = CotizacionDolar(
                id=int(fila['id']), tipo_cotizacion=tipo, fecha=fecha,
                valor_compra=float(fila['valor_compra']),
                valor_venta=float(fila['valor_venta']))

    def _guardar(self) -> None:
        """Reescribe el CSV con el estado actual, si hay ruta."""
        if self._ruta is None:
            return
        filas = [
            {'id': c.id, 'tipo_cotizacion_id': c.tipo_cotizacion.id,
             'fecha': c.fecha.strftime('%Y-%m-%d'),
             'valor_compra': c.valor_compra, 'valor_venta': c.valor_venta}
            for c in self.__datos.values()
        ]
        escribir_csv(self._ruta, self.CAMPOS, filas)

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Guarda la cotización indexada por (tipo_id, fecha)"""
        clave = (cotizacion.tipo_cotizacion.id, cotizacion.fecha)
        if clave in self.__datos:
            raise ValueError(
                'Ya existe una cotización para ese tipo de dolar y fecha')
        self.__datos[clave] = cotizacion
        self._guardar()
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
        self._guardar()
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Quita la cotización de esa clave compuesta si existe"""
        clave = (tipo_id, fecha)
        if clave in self.__datos:
            del self.__datos[clave]
            self._guardar()
            return True
        return False
