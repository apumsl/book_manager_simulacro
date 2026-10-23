"""Punto de entrada de Book Manager.

Para ejecutarlo, desde la carpeta src: python -m book_manager.main
"""
import os
from sqlalchemy import text
from book_manager.database.connection import ConexionDB
from book_manager.models.models import crear_tablas
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioEditorial, RepositorioGenero,
    RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion)
from book_manager.services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio, ServicioStock,
    ServicioTipoCotizacion)
from book_manager.ui.console import ConsolaUI
from book_manager.migrations.migrations import cargar_scripts_sql


def base_vacia(conexion: ConexionDB) -> bool:
    """Indica si la base de datos todavía no tiene datos cargados."""
    with conexion.transaccion() as sesion:
        cantidad = sesion.execute(
            text('SELECT COUNT(*) FROM generos')).scalar()
    return cantidad == 0


def main(import_default_data: bool = False) -> None:
    """Arma repositorios y servicios, y arranca la consola."""
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError('No se encontró DATABASE_URL en el archivo .env')

    # 1. Conexión a la base de datos
    conexion = ConexionDB(url, echo=False)

    # 2. Asegurar que las tablas existan
    crear_tablas(conexion)

    # 3. Precarga: solo si se solicita y la base está vacía
    if import_default_data and base_vacia(conexion):
        print('Base vacía: poblando con scripts SQL...')
        cargar_scripts_sql(conexion)

    # 4. Repositorios
    repo_generos = RepositorioGenero(conexion)
    repo_editoriales = RepositorioEditorial(conexion)
    repo_monedas = RepositorioMoneda(conexion)
    repo_tipos = RepositorioTipoCotizacion(conexion)
    repo_libros = RepositorioLibro(conexion)
    repo_precios = RepositorioPrecio(conexion)
    repo_stock = RepositorioStock(conexion)
    repo_cotizaciones = RepositorioCotizacionDolar(conexion)

    # 5. Servicios
    svc_generos = ServicioGenero(repo_generos, repo_libros)
    svc_editoriales = ServicioEditorial(repo_editoriales, repo_libros)
    svc_libros = ServicioLibro(repo_libros, repo_precios, repo_stock)
    svc_stock = ServicioStock(repo_stock)
    svc_monedas = ServicioMoneda(repo_monedas, repo_precios)
    svc_tipos = ServicioTipoCotizacion(repo_tipos, repo_cotizaciones)
    svc_precios = ServicioPrecio(repo_precios)
    svc_cotizaciones = ServicioCotizacionDolar(repo_cotizaciones, repo_tipos)

    # 6. Consola
    app = ConsolaUI(
        svc_generos, svc_editoriales, svc_libros, svc_stock,
        svc_monedas, svc_tipos, svc_precios, svc_cotizaciones)

    try:
        app.iniciar()
    finally:
        conexion.cerrar()


if __name__ == "__main__":
    main(import_default_data=True)
