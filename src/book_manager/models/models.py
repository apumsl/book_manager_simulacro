"""Modelos ORM de SQLAlchemy: tablas del sistema y sus relaciones.

Cada clase representa una tabla de la base de datos. Las relaciones se
definen con claves foráneas (ForeignKey) y se navegan con relationship().
"""
import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (CheckConstraint, Date, ForeignKey, Integer, Numeric,
                        String, UniqueConstraint)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship)

from book_manager.database.connection import ConexionDB


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos."""


class GeneroModelo(Base):
    """Tabla de géneros literarios."""

    __tablename__ = 'generos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)

    libros: Mapped[List['LibroModelo']] = relationship(
        back_populates='genero')


class EditorialModelo(Base):
    """Tabla de editoriales."""

    __tablename__ = 'editoriales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True)
    sede: Mapped[str] = mapped_column(String(150))

    libros: Mapped[List['LibroModelo']] = relationship(
        back_populates='editorial')


class MonedaModelo(Base):
    """Tabla de monedas (ARS, USD, etc.)."""

    __tablename__ = 'monedas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(3), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))

    precios: Mapped[List['PrecioModelo']] = relationship(
        back_populates='moneda')


class TipoCotizacionModelo(Base):
    """Tabla de tipos de cotización del dólar (Oficial, Blue, MEP, etc.)."""

    __tablename__ = 'tipos_cotizacion'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)

    cotizaciones: Mapped[List['CotizacionDolarModelo']] = relationship(
        back_populates='tipo_cotizacion')


class LibroModelo(Base):
    """Tabla de libros; cada libro pertenece a un género y una editorial."""

    __tablename__ = 'libros'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    titulo: Mapped[str] = mapped_column(String(255))
    autor: Mapped[str] = mapped_column(String(255))
    genero_id: Mapped[int] = mapped_column(ForeignKey('generos.id'))
    editorial_id: Mapped[int] = mapped_column(ForeignKey('editoriales.id'))

    genero: Mapped[GeneroModelo] = relationship(back_populates='libros')
    editorial: Mapped[EditorialModelo] = relationship(
        back_populates='libros')
    precios: Mapped[List['PrecioModelo']] = relationship(
        back_populates='libro')
    stock: Mapped['StockModelo'] = relationship(back_populates='libro')


class PrecioModelo(Base):
    """Tabla de precios de un libro en una moneda, desde una fecha."""

    __tablename__ = 'precios'
    __table_args__ = (
        CheckConstraint('monto > 0', name='ck_precio_monto_positivo'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey('libros.id'))
    moneda_id: Mapped[int] = mapped_column(ForeignKey('monedas.id'))
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fecha_vigencia: Mapped[datetime.date] = mapped_column(Date)

    libro: Mapped[LibroModelo] = relationship(back_populates='precios')
    moneda: Mapped[MonedaModelo] = relationship(back_populates='precios')


class StockModelo(Base):
    """Tabla de stock; hay un único registro de stock por libro."""

    __tablename__ = 'stock'
    __table_args__ = (
        CheckConstraint('cantidad >= 0', name='ck_stock_no_negativo'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey('libros.id'),
                                          unique=True)
    cantidad: Mapped[int] = mapped_column(Integer)

    libro: Mapped[LibroModelo] = relationship(back_populates='stock')


class CotizacionDolarModelo(Base):
    """Tabla de cotizaciones del dólar; una por tipo y fecha."""

    __tablename__ = 'cotizaciones_dolar'
    __table_args__ = (
        UniqueConstraint('tipo_cotizacion_id', 'fecha',
                         name='uq_cotizacion_tipo_fecha'),
        CheckConstraint('valor_compra > 0', name='ck_compra_positiva'),
        CheckConstraint('valor_venta > 0', name='ck_venta_positiva'),
        CheckConstraint('valor_compra <= valor_venta',
                        name='ck_compra_menor_venta'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_cotizacion_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_cotizacion.id'))
    fecha: Mapped[datetime.date] = mapped_column(Date)
    valor_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    valor_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    tipo_cotizacion: Mapped[TipoCotizacionModelo] = relationship(
        back_populates='cotizaciones')


def crear_tablas(conexion: ConexionDB) -> None:
    """Crea en la base de datos todas las tablas que todavía no existen.

    Args:
        conexion (ConexionDB): Conexión a la base de datos.
    """
    Base.metadata.create_all(conexion.engine)
