# Changelog

## [Ejercicio 7]
- Creación del archivo `main.py` como punto de entrada del sistema.
- `main.py` crea los repositorios (con persistencia en CSV dentro de `data/`), los servicios y la consola.
- El parámetro `import_default_data` carga los datos iniciales solo la primera vez.
- Inicialización de `ConsolaUI` y ejecución del menú principal.

## [Ejercicio 6]
- Creación de la interfaz de consola en `ui/console.py` (clase `ConsolaUI`).
- Implementación completa del CRUD mediante menús interactivos para las 8 entidades (Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar).
- `ConsolaUI` recibe los servicios ya construidos, sin crear repositorios ni cargar datos por su cuenta.
- Los menús separan la conversión de números y fechas de la llamada al servicio, y muestran el mensaje de las reglas de negocio.
- Integración de la capa de presentación (UI) con los servicios del sistema.

## [Ejercicio 5]
- Creación de un CSV de precarga por entidad en `migrations/csv/` (generos, editoriales, monedas, tipos_cotizacion, libros, precios, stock, cotizaciones), con id propio y claves foráneas por id.
- Se cargan 10 registros por cada clase del dominio.
- Implementación de `preload_data.py` para leer los CSV, resolver la ruta desde su ubicación y crear las entidades relacionándolas por id.
- Integración de la carga inicial con los repositorios utilizados por la consola.

## [Ejercicio 4]
- Implementación de la capa de servicios en `services.py`.
- Clase base `ServicioGenerico` con las operaciones de crear, buscar por id, listar, actualizar y eliminar, y un servicio específico por entidad.
- `ServicioStock` y `ServicioCotizacionDolar`, que usan sus repositorios con clave propia.
- Reglas de negocio: nombres obligatorios, ISBN único, precio y cotización positivos, compra no mayor a venta, stock no negativo, y no se eliminan registros con datos asociados.
- Integración entre la capa de servicios, las entidades y los repositorios.

## [Ejercicio 3]
- Definición de la interfaz genérica IRepositorio[T] (crear, leer_por_id, leer_todos, actualizar, eliminar) y su implementación RepositorioGenerico.
- Definición de interfaces específicas IRepositorioStock e IRepositorioCotizacionDolar (con clave propia: libro_id, y tipo+fecha respectivamente) y sus implementaciones.
- Los repositorios guardan y cargan sus datos en archivos CSV mediante `almacen_csv.py`; la ruta es opcional y, sin ella, trabajan en memoria.
- Docstrings con formato `Args`, `Returns` y `Raises` y formato PEP8 en `repositories.py`.

## [Ejercicio 2]
- Definición de las entidades del dominio: EntidadBase, Genero, Editorial, Moneda, TipoCotizacion, CotizacionDolar, Libro, Precio, Stock.
- Aplicación de encapsulamiento (atributos privados con `__`, properties con validación en los setters, incluidos `Moneda` y `TipoCotizacion`).
- Relaciones por composición entre entidades (Libro-Genero, Libro-Editorial, Precio-Libro, Precio-Moneda, Stock-Libro, CotizacionDolar-TipoCotizacion).
- Formato PEP8 y docstrings en todas las entidades.

## [Ejercicio 1]
- Inicialización del repositorio.
- Creación de la estructura de directorios del proyecto.
- Creación de paquetes Python (`__init__.py`) en cada módulo.
- Creación de la carpeta migrations/csv para los archivos de datos.
- Agregado de README.md con objetivo e introducción del Sprint 1.
- Agregado de .gitignore y requirements.txt, este último sin librerías externas porque el sprint no las usa.