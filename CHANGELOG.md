# Changelog
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
