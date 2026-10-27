# Changelog

#### [Ejercicio 7]
- Se integraron al menú principal las opciones para ejecutar el scraping, generar el reporte Excel y consultar el historial de auditoría.
- Se conectaron estas opciones con los servicios correspondientes del sistema.
- "Ejecutar scraping" valida la diferencia antes de lanzar el scraper, reduce el log a advertencias, informa la ruta del CSV de alertas y como descargarlo en Colab.
- "Generar reporte" informa si todavía no se ejecutó el scraping, sin interrumpir el programa, y indica como descargar el Excel.
- El historial de auditoría se obtiene mediante `ServicioAuditoria`.
- Se auditan la ejecución del scraping y la generación del reporte; el detalle registra la ruta del archivo generado.
- Se elimina `scraper/cuspide/middlewares.py`, plantilla de Scrapy sin uso en el proyecto.

## [Ejercicio 6]
- Se implementa la clase `Auditoria` en `models.py` heredando de `Base` para mapear las columnas `id`, `accion`, `fecha` y `detalles`.
- Se crea el decorador `@auditar` en `decorators.py` para registrar las operaciones de escritura. Incluye manejo de excepciones (`try/except`) y abre su propia sesión a la base de datos para garantizar que los fallos de auditoría no interrumpan la operación principal del usuario.
- Se aplica el decorador `@auditar` en `repositories.py` exclusivamente sobre los métodos que modifican datos (`crear`, `actualizar`, `eliminar`), asignando etiquetas de acción descriptivas (ej. `"CREAR_GENERO"`).
- Se inicializa la variable `self.sin_coincidencia` como lista vacía dentro del `__init__` de `ServicioAlertasPrecio` para prevenir errores de tipo `AttributeError`.
- Se crea la entidad `Auditoria` con su CRUD completo: `RepositorioAuditoria` (hereda de `RepositorioGenericoDB`, ordena del registro más reciente al más antiguo) y `ServicioAuditoria` (hereda de `ServicioGenerico`).
- Se renombran los modelos de `...Modelo` a `...Model` (y `Auditoria` a `AuditoriaModel`) para coincidir con los nombres que exige la validación del notebook.
- El decorador `auditar` se documenta con type hints, usa `conexion.transaccion()` y registra los detalles con nombres de atributos legibles.

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