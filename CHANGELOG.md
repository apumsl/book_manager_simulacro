# Changelog

## [Ejercicio 5]
- Se crea `ServicioReportePrecios` en `services.py`, que genera un reporte Excel con los resultados de la última ejecución del scraper (`reportes/resultados_cuspide.json`).
- El reporte tiene una fila por cada libro del catálogo con: libro, precio interno, precio web, diferencia (web − interno), fecha de extracción y el criterio de coincidencia usado.
- Se reutiliza la búsqueda del resultado web del Ejercicio 4; si un libro no tiene coincidencia, queda sin precio web ni diferencia.
- Cada reporte se guarda en `reportes/` con fecha y hora en el nombre (`reporte_precios_AAAA-MM-DD_HHMMSS.xlsx`). Si todavía no se ejecutó el scraper, se informa con un error claro.
- Se agrega `openpyxl` a `requirements.txt`.

## [Ejercicio 4]
- Se crea `ServicioAlertasPrecio` en `services.py`, que compara el precio interno en pesos de cada libro con el precio web obtenido por el scraper.
- La diferencia en pesos se ingresa en cada ejecución: con `scrapy crawl cuspide -a diferencia=5000` o, si no se indica, el spider la pide por consola. Se valida que sea un número mayor a cero.
- Para cada libro se compara contra el resultado web con el mismo título o, si no hay, contra uno cuyo título empiece igual (por ejemplo, "El Principito (tapa dura)"). Si ninguno coincide, el libro no se compara, para no generar alertas con libros distintos, y se informa en el log.
- Se agrega `AlertasPreciosPipeline`, que al terminar cada ejecución genera en `reportes/` un CSV nuevo (`alertas_precios_AAAA-MM-DD_HHMMSS.csv`) con los libros cuya diferencia supera el monto ingresado.

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