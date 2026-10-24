# Changelog

## [Ejercicio 3]
- Se implementó `CuspideSpider` con Scrapy.
- El scraper obtiene los libros directamente desde la base de datos.
- Se procesan los primeros 10 resultados por título.
- Se extraen precio, imagen, formas de pago y descripción.
- Se implementaron Loaders y Pipelines para procesar los datos.

## [Ejercicio 2]
- Se crea la función `cargar_sql` en `migrations/migrations.py`, que ejecuta las sentencias de un archivo SQL dentro de una sesión. Admite sentencias en varias líneas, ignora comentarios y escapa los `:` para que SQLAlchemy no los interprete como parámetros.
- Se crea `cargar_scripts_sql`, que carga todos los scripts de precarga en una única transacción, respetando el orden de las claves foráneas y validando antes que no falte ningún archivo.
- Se trasladan desde `main.py` a `migrations.py` la carga de scripts y `sincronizar_secuencias`; `main.py` solo invoca `cargar_scripts_sql`.
- `migrar_datos` genera los scripts con el nombre real de la tabla destino (`cotizaciones` → `cotizaciones_dolar`), eliminando el parche que corregía el nombre durante la carga. Se regenera `cotizaciones.sql`.
- Se fija `sqlalchemy>=2.0,<2.1` en `requirements.txt`: la versión 2.1 cambia el driver por defecto de PostgreSQL a psycopg 3, incompatible con `psycopg2-binary`.

## [Ejercicio 1]
- Creación de la rama `Sprint_3` a partir de `Sprint_2`.
- Creación del proyecto Scrapy `cuspide` en `scraper/`, con su estructura base (items, pipelines, middlewares, settings y spiders).
- Creación de la carpeta `reportes/` para los reportes Excel y las alertas CSV que genera la aplicación.
- Actualización de `.gitignore` para excluir las salidas generadas (`exports/` y `reportes/`) y la caché de Scrapy.
- Se deja de versionar `exports/precios_exportados.csv` por ser un archivo generado.
- Se agrega `scrapy` a `requirements.txt`.
- Actualización del README con el objetivo y la introducción del Sprint 3.