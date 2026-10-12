# Changelog
## [Ejercicio 5]

- Creación del script `migrations/migrations.py` para la migración de datos.
- Implementación de lectura dinámica de archivos CSV y generación automática de sentencias INSERT SQL en la carpeta correspondiente.

## [Ejercicio 4]
- Creación de `models/models.py` con los modelos ORM de las 8 tablas: generos, editoriales, monedas, tipos_cotizacion, libros, precios, stock y cotizaciones_dolar.
- Relaciones por clave foránea entre tablas (libro con género y editorial, precio con libro y moneda, stock con libro, cotización con tipo).
- Restricciones en la base: ISBN y código de moneda únicos, un stock por libro, una cotización por tipo y fecha, montos positivos, stock no negativo y compra no mayor a venta.
- Función `crear_tablas()` y se agrega `psycopg2-binary` a `requirements.txt` para conectar con PostgreSQL (Supabase).

## [Ejercicio 3]
- Se agrega a `ConexionDB` el context manager `transaccion()`, que abre una sesión de SQLAlchemy, hace commit si el bloque termina bien y rollback si ocurre un error, y siempre cierra la sesión.

## [Ejercicio 2]
- Creación de la clase `ConexionDB` en `database/connection.py`, que maneja la conexión a la base de datos con SQLAlchemy a partir de una URL.
- Métodos `probar_conexion` (devuelve `True` o `False`) y `cerrar`, y propiedad `engine`.
- Se agrega `sqlalchemy` a `requirements.txt`.

## [Ejercicio 1]
- Creación de la rama `Sprint_2` a partir de `Sprint_1_fix`, que contiene las correcciones del Sprint 1.
- Creación de las carpetas `database/`, `models/` y `migrations/sql`, con sus paquetes `__init__.py`.
- Actualización del README con el objetivo y la introducción del Sprint 2.
