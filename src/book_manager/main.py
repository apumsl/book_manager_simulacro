"""Punto de entrada de Book Manager.

Para ejecutarlo, desde la carpeta src: python -m book_manager.main
"""
import os
from sqlalchemy import text
from sqlalchemy.orm import Session
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


def base_vacia(conexion: ConexionDB) -> bool:
    """Indica si la base de datos todavía no tiene datos cargados."""
    with conexion.transaccion() as sesion:
        cantidad = sesion.execute(
            text('SELECT COUNT(*) FROM generos')).scalar()
    return cantidad == 0


TABLAS = [
    'generos', 'editoriales', 'monedas', 'tipos_cotizacion',
    'libros', 'precios', 'stock', 'cotizaciones_dolar'
]


def sincronizar_secuencias(sesion: Session) -> None:
    """Ajusta los contadores de id de PostgreSQL tras insertar con id fijo.

    Sin este ajuste, el primer alta sin id intentaría usar el 1 y chocaría
    con los registros cargados desde los scripts SQL.
    """
    for tabla in TABLAS:
        sesion.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), "
            f"COALESCE(MAX(id), 0) + 1, false) FROM {tabla}"))


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
        print("Aviso: No se encontró la carpeta de migraciones SQL. "
              "Iniciando BD vacía.")
        return

    with conexion.transaccion() as sesion:
        for archivo in orden_archivos:
            ruta_sql = os.path.join(sql_dir, archivo)
            if os.path.exists(ruta_sql):
                with open(ruta_sql, 'r', encoding='utf-8') as f:
                    for linea in f:
                        sql = linea.strip()
                        if sql:
                            # Parche: corregir el desfasaje entre el nombre
                            # del CSV y el de la tabla del modelo
                            if archivo == 'cotizaciones.sql':
                                sql = sql.replace(
                                    'INSERT INTO cotizaciones (',
                                    'INSERT INTO cotizaciones_dolar (')

                            sesion.execute(text(sql))

        sincronizar_secuencias(sesion)


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
