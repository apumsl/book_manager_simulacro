"""Repositorios de persistencia del dominio Book Manager mediante SQLAlchemy."""
import abc
import datetime
from typing import TypeVar, Generic, List, Optional, Type

from sqlalchemy.orm import joinedload

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda, Precio,
    Stock, TipoCotizacion
)
from book_manager.models.models import (
    GeneroModelo, EditorialModelo, MonedaModelo, TipoCotizacionModelo,
    LibroModelo, PrecioModelo, StockModelo, CotizacionDolarModelo
)
from book_manager.database.connection import ConexionDB

T = TypeVar('T', bound=EntidadBase)
M = TypeVar('M')


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        pass


class RepositorioGenericoDB(IRepositorio[T], Generic[T, M]):
    """Implementación del CRUD básico mapeando Entidades a Modelos SQLAlchemy."""

    def __init__(self, conexion: ConexionDB, modelo: Type[M]) -> None:
        self.conexion = conexion
        self.modelo = modelo

    @abc.abstractmethod
    def _a_entidad(self, modelo: M) -> T:
        """Convierte un modelo de SQLAlchemy en una entidad de dominio."""
        pass

    @abc.abstractmethod
    def _a_modelo_kwargs(self, entidad: T) -> dict:
        """Convierte una entidad de dominio en un diccionario para SQLAlchemy."""
        pass

    def _query_base(self, sesion):
        """Retorna la query base. Las subclases pueden sobreescribir para eager loading."""
        return sesion.query(self.modelo)

    def crear(self, entidad: T) -> T:
        with self.conexion.transaccion() as sesion:
            if getattr(entidad, 'id', None) and sesion.query(self.modelo).filter_by(id=entidad.id).first():
                raise ValueError(f"Ya existe una entidad con id {entidad.id}")
            
            kwargs = self._a_modelo_kwargs(entidad)
            if getattr(entidad, 'id', None):
                kwargs['id'] = entidad.id
                
            nuevo = self.modelo(**kwargs)
            sesion.add(nuevo)
            sesion.flush()
            nuevo_id = nuevo.id
            
        # Refresca con relaciones completas
        with self.conexion.transaccion() as sesion:
            modelo_completo = self._query_base(sesion).filter_by(id=nuevo_id).one()
            return self._a_entidad(modelo_completo)

    def leer_por_id(self, id: int) -> Optional[T]:
        with self.conexion.transaccion() as sesion:
            modelo = self._query_base(sesion).filter_by(id=id).first()
            return self._a_entidad(modelo) if modelo else None

    def leer_todos(self) -> List[T]:
        with self.conexion.transaccion() as sesion:
            modelos = self._query_base(sesion).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, entidad: T) -> T:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(self.modelo).filter_by(id=entidad.id).first()
            if not modelo:
                raise ValueError(f"No existe una entidad con id {entidad.id} para actualizar")
            
            kwargs = self._a_modelo_kwargs(entidad)
            for key, value in kwargs.items():
                setattr(modelo, key, value)
            sesion.flush()
            
        with self.conexion.transaccion() as sesion:
            modelo_completo = self._query_base(sesion).filter_by(id=entidad.id).one()
            return self._a_entidad(modelo_completo)

    def eliminar(self, id: int) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(self.modelo).filter_by(id=id).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False


class RepositorioGenero(RepositorioGenericoDB[Genero, GeneroModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, GeneroModelo)

    def _a_entidad(self, modelo: GeneroModelo) -> Genero:
        return Genero(id=modelo.id, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: Genero) -> dict:
        return {'nombre': entidad.nombre}


class RepositorioEditorial(RepositorioGenericoDB[Editorial, EditorialModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, EditorialModelo)

    def _a_entidad(self, modelo: EditorialModelo) -> Editorial:
        return Editorial(id=modelo.id, nombre=modelo.nombre, sede=modelo.sede)

    def _a_modelo_kwargs(self, entidad: Editorial) -> dict:
        return {'nombre': entidad.nombre, 'sede': entidad.sede}


class RepositorioMoneda(RepositorioGenericoDB[Moneda, MonedaModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, MonedaModelo)

    def _a_entidad(self, modelo: MonedaModelo) -> Moneda:
        return Moneda(id=modelo.id, codigo=modelo.codigo, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: Moneda) -> dict:
        return {'codigo': entidad.codigo, 'nombre': entidad.nombre}


class RepositorioTipoCotizacion(RepositorioGenericoDB[TipoCotizacion, TipoCotizacionModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, TipoCotizacionModelo)

    def _a_entidad(self, modelo: TipoCotizacionModelo) -> TipoCotizacion:
        return TipoCotizacion(id=modelo.id, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: TipoCotizacion) -> dict:
        return {'nombre': entidad.nombre}


class RepositorioLibro(RepositorioGenericoDB[Libro, LibroModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, LibroModelo)

    def _query_base(self, sesion):
        return sesion.query(self.modelo).options(
            joinedload(self.modelo.genero),
            joinedload(self.modelo.editorial)
        )

    def _a_entidad(self, modelo: LibroModelo) -> Libro:
        genero = Genero(id=modelo.genero.id, nombre=modelo.genero.nombre)
        editorial = Editorial(id=modelo.editorial.id, nombre=modelo.editorial.nombre, sede=modelo.editorial.sede)
        return Libro(id=modelo.id, isbn=modelo.isbn, titulo=modelo.titulo, autor=modelo.autor, genero=genero, editorial=editorial)

    def _a_modelo_kwargs(self, entidad: Libro) -> dict:
        return {
            'isbn': entidad.isbn, 'titulo': entidad.titulo, 
            'autor': entidad.autor, 'genero_id': entidad.genero.id, 
            'editorial_id': entidad.editorial.id
        }


class RepositorioPrecio(RepositorioGenericoDB[Precio, PrecioModelo]):
    def __init__(self, conexion: ConexionDB):
        super().__init__(conexion, PrecioModelo)

    def _query_base(self, sesion):
        return sesion.query(self.modelo).options(
            joinedload(self.modelo.libro).joinedload(LibroModelo.genero),
            joinedload(self.modelo.libro).joinedload(LibroModelo.editorial),
            joinedload(self.modelo.moneda)
        )

    def _a_entidad(self, modelo: PrecioModelo) -> Precio:
        genero = Genero(id=modelo.libro.genero.id, nombre=modelo.libro.genero.nombre)
        editorial = Editorial(id=modelo.libro.editorial.id, nombre=modelo.libro.editorial.nombre, sede=modelo.libro.editorial.sede)
        libro = Libro(id=modelo.libro.id, isbn=modelo.libro.isbn, titulo=modelo.libro.titulo, autor=modelo.libro.autor, genero=genero, editorial=editorial)
        moneda = Moneda(id=modelo.moneda.id, codigo=modelo.moneda.codigo, nombre=modelo.moneda.nombre)
        return Precio(id=modelo.id, libro=libro, moneda=moneda, monto=float(modelo.monto), fecha_vigencia=modelo.fecha_vigencia)

    def _a_modelo_kwargs(self, entidad: Precio) -> dict:
        return {
            'libro_id': entidad.libro.id, 'moneda_id': entidad.moneda.id, 
            'monto': entidad.monto, 'fecha_vigencia': entidad.fecha_vigencia
        }


class IRepositorioStock(abc.ABC):
    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        pass


class RepositorioStock(IRepositorioStock):
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def _query_base(self, sesion):
        return sesion.query(StockModelo).options(
            joinedload(StockModelo.libro).joinedload(LibroModelo.genero),
            joinedload(StockModelo.libro).joinedload(LibroModelo.editorial)
        )

    def _a_entidad(self, modelo: StockModelo) -> Stock:
        genero = Genero(id=modelo.libro.genero.id, nombre=modelo.libro.genero.nombre)
        editorial = Editorial(id=modelo.libro.editorial.id, nombre=modelo.libro.editorial.nombre, sede=modelo.libro.editorial.sede)
        libro = Libro(id=modelo.libro.id, isbn=modelo.libro.isbn, titulo=modelo.libro.titulo, autor=modelo.libro.autor, genero=genero, editorial=editorial)
        return Stock(id=modelo.id, libro=libro, cantidad=modelo.cantidad)

    def crear(self, stock: Stock) -> Stock:
        with self.conexion.transaccion() as sesion:
            if sesion.query(StockModelo).filter_by(libro_id=stock.libro.id).first():
                raise ValueError(f"Ya existe stock para el libro {stock.libro.id}")
            nuevo = StockModelo(libro_id=stock.libro.id, cantidad=stock.cantidad)
            if getattr(stock, 'id', None):
                nuevo.id = stock.id
            sesion.add(nuevo)
            sesion.flush()
            nuevo_id = nuevo.id
            
        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(id=nuevo_id).one())

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self.conexion.transaccion() as sesion:
            modelo = self._query_base(sesion).filter_by(libro_id=libro_id).first()
            return self._a_entidad(modelo) if modelo else None

    def actualizar(self, stock: Stock) -> Stock:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(StockModelo).filter_by(libro_id=stock.libro.id).first()
            if not modelo:
                raise ValueError(f"No existe stock para libro {stock.libro.id} que se pueda actualizar")
            modelo.cantidad = stock.cantidad
            sesion.flush()
            
        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(libro_id=stock.libro.id).one())

    def eliminar(self, libro_id: int) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(StockModelo).filter_by(libro_id=libro_id).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False


class IRepositorioCotizacionDolar(abc.ABC):
    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        pass


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def _query_base(self, sesion):
        return sesion.query(CotizacionDolarModelo).options(joinedload(CotizacionDolarModelo.tipo_cotizacion))

    def _a_entidad(self, modelo: CotizacionDolarModelo) -> CotizacionDolar:
        tipo = TipoCotizacion(id=modelo.tipo_cotizacion.id, nombre=modelo.tipo_cotizacion.nombre)
        return CotizacionDolar(
            id=modelo.id, tipo_cotizacion=tipo, fecha=modelo.fecha, 
            valor_compra=float(modelo.valor_compra), valor_venta=float(modelo.valor_venta)
        )

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self.conexion.transaccion() as sesion:
            if sesion.query(CotizacionDolarModelo).filter_by(tipo_cotizacion_id=cotizacion.tipo_cotizacion.id, fecha=cotizacion.fecha).first():
                raise ValueError("Ya existe una cotización para ese tipo de dolar y fecha")
            nuevo = CotizacionDolarModelo(
                tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                fecha=cotizacion.fecha, valor_compra=cotizacion.valor_compra, valor_venta=cotizacion.valor_venta
            )
            if getattr(cotizacion, 'id', None):
                nuevo.id = cotizacion.id
            sesion.add(nuevo)
            sesion.flush()
            nuevo_id = nuevo.id
            
        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(id=nuevo_id).one())

    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        with self.conexion.transaccion() as sesion:
            modelo = self._query_base(sesion).filter_by(tipo_cotizacion_id=tipo_id, fecha=fecha).first()
            return self._a_entidad(modelo) if modelo else None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self.conexion.transaccion() as sesion:
            modelos = self._query_base(sesion).filter_by(tipo_cotizacion_id=tipo_id).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(CotizacionDolarModelo).filter_by(tipo_cotizacion_id=cotizacion.tipo_cotizacion.id, fecha=cotizacion.fecha).first()
            if not modelo:
                raise ValueError("No existe una cotización para ese tipo de dólar en esa fecha para actualizar")
            modelo.valor_compra = cotizacion.valor_compra
            modelo.valor_venta = cotizacion.valor_venta
            sesion.flush()
            
        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(tipo_cotizacion_id=cotizacion.tipo_cotizacion.id, fecha=cotizacion.fecha).one())

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(CotizacionDolarModelo).filter_by(tipo_cotizacion_id=tipo_id, fecha=fecha).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False