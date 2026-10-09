"""Carga inicial de datos desde los archivos CSV de migrations/csv."""
import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import IRepositorio

CARPETA_CSV: Path = Path(__file__).resolve().parent.parent / 'migrations' / 'csv'


def _leer_csv(nombre_archivo: str) -> list[dict[str, str]]:
    """Lee un CSV de la carpeta de migraciones y devuelve sus filas como diccionarios."""
    with open(CARPETA_CSV / nombre_archivo, 'r', encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def _a_fecha(texto: str) -> date:
    """Convierte un texto con formato AAAA-MM-DD en un objeto date."""
    return datetime.strptime(texto, '%Y-%m-%d').date()


def _buscar(repositorio: IRepositorio, id_entidad: int, descripcion: str) -> Any:
    """Busca una entidad por id y falla con un mensaje claro si no existe."""
    entidad = repositorio.leer_por_id(id_entidad)
    if entidad is None:
        raise ValueError(f'No existe {descripcion} con id {id_entidad}')
    return entidad


def cargar_datos(
    repo_generos: IRepositorio,
    repo_editoriales: IRepositorio,
    repo_monedas: IRepositorio,
    repo_tipos_cotizacion: IRepositorio,
    repo_libros: IRepositorio,
    repo_precios: IRepositorio,
    repo_stock: Any,
    repo_cotizaciones: Any,
) -> None:
    """Lee los CSV de migrations/csv y crea las entidades en cada repositorio.

    Se cargan primero las entidades independientes y después las que dependen
    de ellas (libros, precios, stock y cotizaciones).
    """
    for fila in _leer_csv('generos.csv'):
        repo_generos.crear(Genero(id=int(fila['id']), nombre=fila['nombre']))

    for fila in _leer_csv('editoriales.csv'):
        repo_editoriales.crear(
            Editorial(id=int(fila['id']), nombre=fila['nombre'], sede=fila['sede'])
        )

    for fila in _leer_csv('monedas.csv'):
        repo_monedas.crear(
            Moneda(id=int(fila['id']), codigo=fila['codigo'], nombre=fila['nombre'])
        )

    for fila in _leer_csv('tipos_cotizacion.csv'):
        repo_tipos_cotizacion.crear(
            TipoCotizacion(id=int(fila['id']), nombre=fila['nombre'])
        )

    for fila in _leer_csv('libros.csv'):
        repo_libros.crear(
            Libro(
                id=int(fila['id']),
                isbn=fila['isbn'],
                titulo=fila['titulo'],
                autor=fila['autor'],
                genero=_buscar(repo_generos, int(fila['genero_id']), 'género'),
                editorial=_buscar(repo_editoriales, int(fila['editorial_id']), 'editorial'),
            )
        )

    for fila in _leer_csv('precios.csv'):
        repo_precios.crear(
            Precio(
                id=int(fila['id']),
                libro=_buscar(repo_libros, int(fila['libro_id']), 'libro'),
                moneda=_buscar(repo_monedas, int(fila['moneda_id']), 'moneda'),
                monto=float(fila['monto']),
                fecha_vigencia=_a_fecha(fila['fecha_vigencia']),
            )
        )

    for fila in _leer_csv('stock.csv'):
        repo_stock.crear(
            Stock(
                id=int(fila['id']),
                libro=_buscar(repo_libros, int(fila['libro_id']), 'libro'),
                cantidad=int(fila['cantidad']),
            )
        )

    for fila in _leer_csv('cotizaciones.csv'):
        repo_cotizaciones.crear(
            CotizacionDolar(
                id=int(fila['id']),
                tipo_cotizacion=_buscar(
                    repo_tipos_cotizacion, int(fila['tipo_cotizacion_id']), 'tipo de cotización'
                ),
                fecha=_a_fecha(fila['fecha']),
                valor_compra=float(fila['valor_compra']),
                valor_venta=float(fila['valor_venta']),
            )
        )