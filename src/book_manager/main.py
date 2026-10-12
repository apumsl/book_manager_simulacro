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

def ejecutar_scripts_sql(conexion: ConexionDB) -> None:
    """Ejecuta los scripts SQL generados para poblar la base de datos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_dir = os.path.join(base_dir, 'migrations', 'sql')
    
    # El orden es estricto para no violar las restricciones de clave foránea
    orden_archivos = [
        'generos.sql',
        'editoriales.sql',
        'monedas.sql',
        'tipos_cotizacion.sql',
        'libros.sql',
        'precios.sql',
        'stock.sql',
        'cotizaciones.sql'
    ]

    if not os.path.exists(sql_dir):
        print("Aviso: No se encontró la carpeta de migraciones SQL. Iniciando BD vacía.")
        return

    with conexion.transaccion() as sesion:
        for archivo in orden_archivos:
            ruta_sql = os.path.join(sql_dir, archivo)
            if os.path.exists(ruta_sql):
                with open(ruta_sql, 'r', encoding='utf-8') as f:
                    for linea in f:
                        sql = linea.strip()
                        if sql:
                            # Parche: Corregir desfasaje entre nombre del CSV y modelo SQLAlchemy
                            if archivo == 'cotizaciones.sql':
                                sql = sql.replace('INSERT INTO cotizaciones (', 'INSERT INTO cotizaciones_dolar (')
                            
                            sesion.execute(text(sql))

def main(import_default_data=False):
    """Arma repositorios y servicios, y arranca la consola."""
    
    # 1. Configuración de la base de datos local
    db_path = os.path.join(os.path.dirname(__file__), 'book_manager.db')
    
    # Comprobamos si es la primera vez que se levanta el programa
    primera_vez = not os.path.exists(db_path)

    conexion = ConexionDB(f"sqlite:///{db_path}", echo=False)

    # 2. Asegurar que las tablas existan
    crear_tablas(conexion)

    # 3. Precarga: solo la primera vez si se solicita importar datos
    if import_default_data and primera_vez:
        print("Primera ejecución detectada: Poblando la base de datos con scripts SQL...")
        ejecutar_scripts_sql(conexion)

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