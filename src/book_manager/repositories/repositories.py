"""Repositorios de persistencia de Book Manager mediante SQLAlchemy."""
import abc
import datetime
from typing import TypeVar, Generic, List, Optional, Type
from book_manager.database.decorators import auditar

from sqlalchemy.orm import Query, Session, joinedload

from book_manager.entities.entities import (
    Auditoria, CotizacionDolar, Editorial, EntidadBase, Genero, Libro,
    Moneda, Precio, Stock, TipoCotizacion
)
from book_manager.models.models import (
    AuditoriaModel, GeneroModel, EditorialModel, MonedaModel,
    TipoCotizacionModel, LibroModel, PrecioModel, StockModel,
    CotizacionDolarModel
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
    """CRUD básico que mapea entidades a modelos de SQLAlchemy."""

    def __init__(self, conexion: ConexionDB, modelo: Type[M]) -> None:
        self.conexion = conexion
        self.modelo = modelo

    @abc.abstractmethod
    def _a_entidad(self, modelo: M) -> T:
        """Convierte un modelo de SQLAlchemy en una entidad de dominio."""
        pass

    @abc.abstractmethod
    def _a_modelo_kwargs(self, entidad: T) -> dict:
        """Convierte una entidad de dominio en un dict para SQLAlchemy."""
        pass

    def _query_base(self, sesion: Session) -> Query:
        """Retorna la query base.

        Las subclases pueden sobreescribir para eager loading.
        """
        return sesion.query(self.modelo)

    def crear(self, entidad: T) -> T:
        with self.conexion.transaccion() as sesion:
            if (getattr(entidad, 'id', None)
                    and sesion.query(self.modelo).filter_by(
                        id=entidad.id).first()):
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
            modelo_completo = self._query_base(
                sesion).filter_by(id=nuevo_id).one()
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
                raise ValueError(
                    f"No existe una entidad con id {entidad.id} "
                    "para actualizar")

            kwargs = self._a_modelo_kwargs(entidad)
            for key, value in kwargs.items():
                setattr(modelo, key, value)
            sesion.flush()

        with self.conexion.transaccion() as sesion:
            modelo_completo = self._query_base(
                sesion).filter_by(id=entidad.id).one()
            return self._a_entidad(modelo_completo)

    def eliminar(self, id: int) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(self.modelo).filter_by(id=id).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False


class RepositorioGenero(RepositorioGenericoDB[Genero, GeneroModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, GeneroModel)

    def _a_entidad(self, modelo: GeneroModel) -> Genero:
        return Genero(id=modelo.id, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: Genero) -> dict:
        return {'nombre': entidad.nombre}

    @auditar(accion="CREAR_GENERO")
    def crear(self, entidad: Genero) -> Genero:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_GENERO")
    def actualizar(self, entidad: Genero) -> Genero:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_GENERO")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


class RepositorioEditorial(RepositorioGenericoDB[Editorial, EditorialModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, EditorialModel)

    def _a_entidad(self, modelo: EditorialModel) -> Editorial:
        return Editorial(id=modelo.id, nombre=modelo.nombre, sede=modelo.sede)

    def _a_modelo_kwargs(self, entidad: Editorial) -> dict:
        return {'nombre': entidad.nombre, 'sede': entidad.sede}

    @auditar(accion="CREAR_EDITORIAL")
    def crear(self, entidad: Editorial) -> Editorial:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_EDITORIAL")
    def actualizar(self, entidad: Editorial) -> Editorial:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_EDITORIAL")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


class RepositorioMoneda(RepositorioGenericoDB[Moneda, MonedaModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, MonedaModel)

    def _a_entidad(self, modelo: MonedaModel) -> Moneda:
        return Moneda(id=modelo.id, codigo=modelo.codigo, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: Moneda) -> dict:
        return {'codigo': entidad.codigo, 'nombre': entidad.nombre}

    @auditar(accion="CREAR_MONEDA")
    def crear(self, entidad: Moneda) -> Moneda:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_MONEDA")
    def actualizar(self, entidad: Moneda) -> Moneda:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_MONEDA")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


class RepositorioTipoCotizacion(
        RepositorioGenericoDB[TipoCotizacion, TipoCotizacionModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, TipoCotizacionModel)

    def _a_entidad(self, modelo: TipoCotizacionModel) -> TipoCotizacion:
        return TipoCotizacion(id=modelo.id, nombre=modelo.nombre)

    def _a_modelo_kwargs(self, entidad: TipoCotizacion) -> dict:
        return {'nombre': entidad.nombre}

    @auditar(accion="CREAR_TIPO_COTIZACION")
    def crear(self, entidad: TipoCotizacion) -> TipoCotizacion:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_TIPO_COTIZACION")
    def actualizar(self, entidad: TipoCotizacion) -> TipoCotizacion:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_TIPO_COTIZACION")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


class RepositorioLibro(RepositorioGenericoDB[Libro, LibroModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, LibroModel)

    def _query_base(self, sesion: Session) -> Query:
        return sesion.query(self.modelo).options(
            joinedload(self.modelo.genero),
            joinedload(self.modelo.editorial)
        )

    def _a_entidad(self, modelo: LibroModel) -> Libro:
        genero = Genero(id=modelo.genero.id, nombre=modelo.genero.nombre)
        editorial = Editorial(
            id=modelo.editorial.id, nombre=modelo.editorial.nombre,
            sede=modelo.editorial.sede)
        return Libro(
            id=modelo.id, isbn=modelo.isbn, titulo=modelo.titulo,
            autor=modelo.autor, genero=genero, editorial=editorial)

    def _a_modelo_kwargs(self, entidad: Libro) -> dict:
        return {
            'isbn': entidad.isbn, 'titulo': entidad.titulo,
            'autor': entidad.autor, 'genero_id': entidad.genero.id,
            'editorial_id': entidad.editorial.id
        }

    @auditar(accion="CREAR_LIBRO")
    def crear(self, entidad: Libro) -> Libro:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_LIBRO")
    def actualizar(self, entidad: Libro) -> Libro:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_LIBRO")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


class RepositorioPrecio(RepositorioGenericoDB[Precio, PrecioModel]):
    def __init__(self, conexion: ConexionDB) -> None:
        super().__init__(conexion, PrecioModel)

    def _query_base(self, sesion: Session) -> Query:
        return sesion.query(self.modelo).options(
            joinedload(self.modelo.libro).joinedload(LibroModel.genero),
            joinedload(self.modelo.libro).joinedload(LibroModel.editorial),
            joinedload(self.modelo.moneda)
        )

    def _a_entidad(self, modelo: PrecioModel) -> Precio:
        genero = Genero(id=modelo.libro.genero.id,
                        nombre=modelo.libro.genero.nombre)
        editorial = Editorial(id=modelo.libro.editorial.id,
                              nombre=modelo.libro.editorial.nombre,
                              sede=modelo.libro.editorial.sede)
        libro = Libro(id=modelo.libro.id, isbn=modelo.libro.isbn,
                      titulo=modelo.libro.titulo, autor=modelo.libro.autor,
                      genero=genero, editorial=editorial)
        moneda = Moneda(id=modelo.moneda.id,
                        codigo=modelo.moneda.codigo,
                        nombre=modelo.moneda.nombre)
        return Precio(id=modelo.id, libro=libro, moneda=moneda,
                      monto=float(modelo.monto),
                      fecha_vigencia=modelo.fecha_vigencia)

    def _a_modelo_kwargs(self, entidad: Precio) -> dict:
        return {
            'libro_id': entidad.libro.id, 'moneda_id': entidad.moneda.id,
            'monto': entidad.monto, 'fecha_vigencia': entidad.fecha_vigencia
        }

    @auditar(accion="CREAR_PRECIO")
    def crear(self, entidad: Precio) -> Precio:
        return super().crear(entidad)

    @auditar(accion="ACTUALIZAR_PRECIO")
    def actualizar(self, entidad: Precio) -> Precio:
        return super().actualizar(entidad)

    @auditar(accion="ELIMINAR_PRECIO")
    def eliminar(self, id: int) -> bool:
        return super().eliminar(id)


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
    def __init__(self, conexion: ConexionDB) -> None:
        self.conexion = conexion

    def _query_base(self, sesion: Session) -> Query:
        return sesion.query(StockModel).options(
            joinedload(StockModel.libro).joinedload(LibroModel.genero),
            joinedload(StockModel.libro).joinedload(LibroModel.editorial)
        )

    def _a_entidad(self, modelo: StockModel) -> Stock:
        genero = Genero(id=modelo.libro.genero.id,
                        nombre=modelo.libro.genero.nombre)
        editorial = Editorial(id=modelo.libro.editorial.id,
                              nombre=modelo.libro.editorial.nombre,
                              sede=modelo.libro.editorial.sede)
        libro = Libro(id=modelo.libro.id, isbn=modelo.libro.isbn,
                      titulo=modelo.libro.titulo, autor=modelo.libro.autor,
                      genero=genero, editorial=editorial)
        return Stock(id=modelo.id, libro=libro, cantidad=modelo.cantidad)

    @auditar(accion="CREAR_STOCK")
    def crear(self, stock: Stock) -> Stock:
        with self.conexion.transaccion() as sesion:
            if sesion.query(StockModel).filter_by(
                    libro_id=stock.libro.id).first():
                raise ValueError(
                    f"Ya existe stock para el libro {stock.libro.id}")
            nuevo = StockModel(libro_id=stock.libro.id,
                                cantidad=stock.cantidad)
            if getattr(stock, 'id', None):
                nuevo.id = stock.id
            sesion.add(nuevo)
            sesion.flush()
            nuevo_id = nuevo.id

        with self.conexion.transaccion() as sesion:
            return self._a_entidad(
                self._query_base(sesion).filter_by(id=nuevo_id).one())

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self.conexion.transaccion() as sesion:
            modelo = self._query_base(sesion).filter_by(
                libro_id=libro_id).first()
            return self._a_entidad(modelo) if modelo else None

    @auditar(accion="ACTUALIZAR_STOCK")
    def actualizar(self, stock: Stock) -> Stock:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(StockModel).filter_by(
                libro_id=stock.libro.id).first()
            if not modelo:
                raise ValueError(
                    f"No existe stock para libro {stock.libro.id} "
                    "que se pueda actualizar")
            modelo.cantidad = stock.cantidad
            sesion.flush()

        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(
                libro_id=stock.libro.id).one())

    @auditar(accion="ELIMINAR_STOCK")
    def eliminar(self, libro_id: int) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(StockModel).filter_by(
                libro_id=libro_id).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False


class IRepositorioCotizacionDolar(abc.ABC):
    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
            self, tipo_id: int,
            fecha: datetime.date) -> Optional[CotizacionDolar]:
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
    def __init__(self, conexion: ConexionDB) -> None:
        self.conexion = conexion

    def _query_base(self, sesion: Session) -> Query:
        return sesion.query(CotizacionDolarModel).options(
            joinedload(CotizacionDolarModel.tipo_cotizacion))

    def _a_entidad(self, modelo: CotizacionDolarModel) -> CotizacionDolar:
        tipo = TipoCotizacion(id=modelo.tipo_cotizacion.id,
                              nombre=modelo.tipo_cotizacion.nombre)
        return CotizacionDolar(
            id=modelo.id, tipo_cotizacion=tipo, fecha=modelo.fecha,
            valor_compra=float(modelo.valor_compra),
            valor_venta=float(modelo.valor_venta)
        )

    @auditar(accion="CREAR_COTIZACION")
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self.conexion.transaccion() as sesion:
            if sesion.query(CotizacionDolarModel).filter_by(
                    tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                    fecha=cotizacion.fecha).first():
                raise ValueError(
                    "Ya existe una cotización para ese tipo de dolar y fecha")
            nuevo = CotizacionDolarModel(
                tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                fecha=cotizacion.fecha,
                valor_compra=cotizacion.valor_compra,
                valor_venta=cotizacion.valor_venta
            )
            if getattr(cotizacion, 'id', None):
                nuevo.id = cotizacion.id
            sesion.add(nuevo)
            sesion.flush()
            nuevo_id = nuevo.id

        with self.conexion.transaccion() as sesion:
            return self._a_entidad(
                self._query_base(sesion).filter_by(id=nuevo_id).one())

    def leer_por_tipo_y_fecha(
            self, tipo_id: int,
            fecha: datetime.date) -> Optional[CotizacionDolar]:
        with self.conexion.transaccion() as sesion:
            modelo = self._query_base(sesion).filter_by(
                tipo_cotizacion_id=tipo_id, fecha=fecha).first()
            return self._a_entidad(modelo) if modelo else None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self.conexion.transaccion() as sesion:
            modelos = self._query_base(sesion).filter_by(
                tipo_cotizacion_id=tipo_id).all()
            return [self._a_entidad(m) for m in modelos]

    @auditar(accion="ACTUALIZAR_COTIZACION")
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(CotizacionDolarModel).filter_by(
                tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                fecha=cotizacion.fecha).first()
            if not modelo:
                raise ValueError(
                    "No existe una cotización para ese tipo de dólar "
                    "en esa fecha para actualizar")
            modelo.valor_compra = cotizacion.valor_compra
            modelo.valor_venta = cotizacion.valor_venta
            sesion.flush()

        with self.conexion.transaccion() as sesion:
            return self._a_entidad(self._query_base(sesion).filter_by(
                tipo_cotizacion_id=cotizacion.tipo_cotizacion.id,
                fecha=cotizacion.fecha).one())

    @auditar(accion="ELIMINAR_COTIZACION")
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        with self.conexion.transaccion() as sesion:
            modelo = sesion.query(CotizacionDolarModel).filter_by(
                tipo_cotizacion_id=tipo_id, fecha=fecha).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False


class RepositorioAuditoria(
        RepositorioGenericoDB[Auditoria, AuditoriaModel]):
    """Persistencia de los registros de auditoría.

    No lleva el decorador auditar, para no generar registros en cadena.
    """

    def __init__(self, conexion: ConexionDB) -> None:
        """Inicializa el repositorio con la conexión a la base."""
        super().__init__(conexion, AuditoriaModel)

    def _a_entidad(self, modelo: AuditoriaModel) -> Auditoria:
        """Convierte un registro de la tabla en una entidad."""
        return Auditoria(id=modelo.id, accion=modelo.accion,
                         fecha=modelo.fecha, detalles=modelo.detalles)

    def _a_modelo_kwargs(self, entidad: Auditoria) -> dict:
        """Convierte una entidad en los campos del modelo.

        Si la entidad no trae fecha, la completa la base con la actual.
        """
        campos = {'accion': entidad.accion, 'detalles': entidad.detalles}
        if entidad.fecha is not None:
            campos['fecha'] = entidad.fecha
        return campos

    def _query_base(self, sesion: Session) -> Query:
        """Ordena los registros del más reciente al más antiguo."""
        return sesion.query(AuditoriaModel).order_by(
            AuditoriaModel.fecha.desc())