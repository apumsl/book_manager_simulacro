"""Punto de entrada de Book Manager.

Para ejecutarlo, desde la carpeta src: python -m book_manager.main
"""
from pathlib import Path

from book_manager.preload_data.preload_data import cargar_datos
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioEditorial, RepositorioGenero,
    RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion)
from book_manager.services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio, ServicioStock,
    ServicioTipoCotizacion)
from book_manager.ui.console import ConsolaUI

DATOS = Path(__file__).resolve().parent / 'data'


def main(import_default_data=False):
    """Arma repositorios y servicios, y arranca la consola.

    Args:
        import_default_data: si es True y todavía no hay datos guardados,
            carga los datos iniciales desde migrations/csv.
    """
    primera_vez = not (DATOS / 'generos.csv').exists()

    # 1. Repositorios: primero los independientes y después los que
    # dependen de ellos. Cada uno guarda en su propio CSV.
    repo_generos = RepositorioGenero(DATOS / 'generos.csv')
    repo_editoriales = RepositorioEditorial(DATOS / 'editoriales.csv')
    repo_monedas = RepositorioMoneda(DATOS / 'monedas.csv')
    repo_tipos = RepositorioTipoCotizacion(DATOS / 'tipos_cotizacion.csv')
    repo_libros = RepositorioLibro(
        repo_generos, repo_editoriales, DATOS / 'libros.csv')
    repo_precios = RepositorioPrecio(
        repo_libros, repo_monedas, DATOS / 'precios.csv')
    repo_stock = RepositorioStock(repo_libros, DATOS / 'stock.csv')
    repo_cotizaciones = RepositorioCotizacionDolar(
        repo_tipos, DATOS / 'cotizaciones.csv')

    # 2. Precarga: solo la primera vez, cuando no hay datos guardados.
    if import_default_data and primera_vez:
        cargar_datos(
            repo_generos, repo_editoriales, repo_monedas, repo_tipos,
            repo_libros, repo_precios, repo_stock, repo_cotizaciones)

    # 3. Servicios
    svc_generos = ServicioGenero(repo_generos, repo_libros)
    svc_editoriales = ServicioEditorial(repo_editoriales, repo_libros)
    svc_libros = ServicioLibro(repo_libros, repo_precios, repo_stock)
    svc_stock = ServicioStock(repo_stock)
    svc_monedas = ServicioMoneda(repo_monedas, repo_precios)
    svc_tipos = ServicioTipoCotizacion(repo_tipos, repo_cotizaciones)
    svc_precios = ServicioPrecio(repo_precios)
    svc_cotizaciones = ServicioCotizacionDolar(repo_cotizaciones)

    # 4. Consola
    app = ConsolaUI(
        svc_generos, svc_editoriales, svc_libros, svc_stock,
        svc_monedas, svc_tipos, svc_precios, svc_cotizaciones)
    app.iniciar()


if __name__ == "__main__":
    main(import_default_data=True)
