# Changelog

#### [Corrección estilo]
- Se corrigieron las líneas de más de 79 caracteres para cumplir con PEP 8.
- No hay cambios de comportamiento: solo estilo y tipado.

## [Conexión a Supabase]
### Agregado
- Base de datos PostgreSQL alojada en Supabase, configurada mediante la variable `DATABASE_URL`.
- Rol `book_app` con permisos de `SELECT`, `INSERT`, `UPDATE` y`DELETE` sobre las tablas del sistema.
- Función `sincronizar_secuencias` para ajustar los contadores de ID luego de la precarga de datos.
### Cambiado
- `main.py` utiliza `DATABASE_URL` para establecer la conexión.
- La precarga mediante scripts SQL se ejecuta solamente cuando la base de datos está vacía.
### Dependencias
- `psycopg2-binary` como controlador para PostgreSQL.

## [Ejercicio 8]
- Se agrega la opción de menú para obtener las cotizaciones mediante la API.
- Se incorpora la visualización de la lista de precios bimonetaria de los libros, mostrando el precio en pesos y en la moneda seleccionada .
- Se agrega la exportación de precios a archivo CSV para los distintos tipos de monedas disponibles.
- Se modifica `book_manager/ui/console.py` para incorporar las nuevas opciones del menú.

## [Ejercicio 7]
- Integración de la API de cotizaciones del dólar mediante la librería `requests`.
- Incorporación de `python-dotenv` para cargar la URL de la API desde el archivo `.env`.
- Implementación del método `obtener_cotizaciones()` en `ServicioCotizacionDolar` para consultar y descargar las cotizaciones.
- Registro de las cotizaciones obtenidas en la base de datos mediante `RepositorioCotizacionDolar`.
- Búsqueda de tipos de cotización existentes y creación automática cuando no se encuentran registrados.
- Actualización de cotizaciones existentes para evitar duplicados por tipo y fecha.
- Modificación de `main.py` para inyectar `RepositorioTipoCotizacion` en `ServicioCotizacionDolar`.
- Se agregan `requests` y `python-dotenv` a `requirements.txt`.

## [Ejercicio 6]
- Redefinicion de `repositories.py` para mapear entidades a modelos usando SQLAlchemy y `ConexionDB`.
- Eliminación del archivo `almacen_csv.py` y la carpeta `preload_data` por quedar obsoletos.
- Modificación de `main.py` para inyectar la conexión a la base de datos a todos los repositorios y crear la base de datos `book_managerDB` si se ejecuta por primera vez.
- Implementación de carga automática de datos iniciales mediante la ejecución de los scripts `.sql` migrados en el ejercicio 5 en el primer arranque.

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
