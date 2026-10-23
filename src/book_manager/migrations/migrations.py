"""Migración de datos: genera scripts SQL desde CSV y los carga en la base."""
import csv
import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from book_manager.database.connection import ConexionDB

CARPETA_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql')
ORDEN_SCRIPTS = [
    'generos.sql', 'editoriales.sql', 'monedas.sql', 'tipos_cotizacion.sql',
    'libros.sql', 'precios.sql', 'stock.sql', 'cotizaciones.sql',
]
TABLAS_CON_ID = [
    'generos', 'editoriales', 'monedas', 'tipos_cotizacion',
    'libros', 'precios', 'stock', 'cotizaciones_dolar',
]
TABLAS_DESTINO = {'cotizaciones': 'cotizaciones_dolar'}

def migrar_datos(carpeta_csvs: str, carpeta_sqls: str) -> None:
    """ Función encargada de la migración de datos de csv a sql.
    Se encarga de leer los archivos csv y crear los archivos sql
    para la inserción en la base de datos.
    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv
            de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos
            sql generados.
    """

    os.makedirs(carpeta_sqls, exist_ok=True)
    if not os.path.exists(carpeta_csvs):
        print(f"Error: La carpeta {carpeta_csvs} no existe.")
        return

    archivos_csv = [f for f in os.listdir(carpeta_csvs) if f.endswith('.csv')]

    for archivo in archivos_csv:
        ruta_csv = os.path.join(carpeta_csvs, archivo)
        nombre_archivo = os.path.splitext(archivo)[0]
        nombre_tabla = TABLAS_DESTINO.get(nombre_archivo, nombre_archivo)
        ruta_sql = os.path.join(carpeta_sqls, f"{nombre_archivo}.sql")

        with open(ruta_csv, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            campos = reader.fieldnames
            if not campos:
                continue

            columnas_str = ", ".join(campos)
            sentencias = []

            for fila in reader:
                valores = []
                for campo in campos:
                    valor = fila[campo].strip() if fila[campo] else ""
                    if valor.isdigit():
                        valores.append(valor)
                    else:
                        try:
                            float(valor)
                            # Evita tratar fechas YYYY-MM-DD como números
                            if "-" in valor and len(valor) >= 8:
                                raise ValueError
                            valores.append(valor)
                        except ValueError:
                            valor_escapado = valor.replace("'", "''")
                            valores.append(f"'{valor_escapado}'")

                valores_str = ", ".join(valores)
                sentencia = (f"INSERT INTO {nombre_tabla} ({columnas_str}) "
                             f"VALUES ({valores_str});\n")
                sentencias.append(sentencia)

        with open(ruta_sql, mode='w', encoding='utf-8') as f_out:
            f_out.writelines(sentencias)
        print(
            f"Archivo generado: {ruta_sql} ({len(sentencias)} registros "
            f"para la tabla '{nombre_tabla}').")

def cargar_sql(sesion: Session, ruta_sql: str) -> int:
    """Ejecuta las sentencias de un archivo SQL dentro de una sesión.

    Una sentencia termina cuando una línea finaliza en ';', por lo que se
    admiten sentencias escritas en varias líneas. Se ignoran las líneas
    vacías y los comentarios '--'.

    Args:
        sesion: Sesión abierta donde se ejecutan las sentencias.
        ruta_sql: Ruta del archivo .sql a cargar.

    Returns:
        int: Cantidad de sentencias ejecutadas.
    """
    ejecutadas = 0
    partes: list[str] = []
    with open(ruta_sql, encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('--'):
                continue
            partes.append(linea)
            if linea.endswith(';'):
                sentencia = ' '.join(partes).replace(':', '\\:')
                sesion.execute(text(sentencia))
                partes.clear()
                ejecutadas += 1
    return ejecutadas


def sincronizar_secuencias(sesion: Session) -> None:
    """Ajusta los contadores de id de PostgreSQL tras insertar con id fijo.

    Sin este ajuste, la primera alta sin id intentaría usar el 1 y chocaría
    con los registros cargados desde los scripts SQL.
    """
    for tabla in TABLAS_CON_ID:
        sesion.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), "
            f"COALESCE(MAX(id), 0) + 1, false) FROM {tabla}"))


def cargar_scripts_sql(conexion: ConexionDB,
                       carpeta: str = CARPETA_SQL) -> None:
    """Carga todos los scripts SQL de precarga en una única transacción.

    Los scripts se ejecutan en un orden que respeta las claves foráneas.
    Si cualquier sentencia falla, se revierte la carga completa.

    Args:
        conexion: Conexión a la base de datos destino.
        carpeta: Carpeta que contiene los archivos .sql.

    Raises:
        FileNotFoundError: Si falta la carpeta o alguno de los scripts.
    """
    faltantes = [archivo for archivo in ORDEN_SCRIPTS
                 if not os.path.isfile(os.path.join(carpeta, archivo))]
    if faltantes:
        raise FileNotFoundError(
            f'Faltan scripts SQL en {carpeta}: {", ".join(faltantes)}')

    with conexion.transaccion() as sesion:
        for archivo in ORDEN_SCRIPTS:
            cantidad = cargar_sql(sesion, os.path.join(carpeta, archivo))
            print(f'{archivo}: {cantidad} registros cargados.')
        sincronizar_secuencias(sesion)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_csv = os.path.join(base_dir, 'csv')
    dir_sql = os.path.join(base_dir, 'sql')
    migrar_datos(dir_csv, dir_sql)
