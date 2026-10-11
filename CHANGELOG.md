# Changelog

## [Ejercicio 4]
- Corrección: los servicios aplican reglas de negocio: nombres obligatorios, ISBN único, precio y cotización positivos, compra no mayor a venta, stock no negativo, y no se eliminan registros con datos asociados.
- Corrección: nueva clase base `ServicioGenerico` con validación y servicios por entidad; `StockService` y `CotizacionDolarService` pasan a llamarse `ServicioStock` y `ServicioCotizacionDolar`.
- Corrección: `console.py` crea los nuevos servicios con sus repositorios.

## [Ejercicio 3]
- Corrección: se corrige el nombre de la interfaz `IRepositorioStock` y los parámetros mal escritos (`entidad`, `cotizacion`) en las interfaces de los repositorios.
- Corrección: docstrings con formato `Args`, `Returns` y `Raises`, typos corregidos, comentarios fuera de lugar eliminados y formato PEP8 en `repositories.py`.
- Corrección: `preload_data.py` usa las interfaces de los repositorios como tipos y cumple PEP8.
- Corrección: los repositorios guardan y cargan sus datos en archivos CSV mediante `almacen_csv.py`; la ruta es opcional y, sin ella, trabajan en memoria.

## [Ejercicio 2]
- Corrección: se agregan setters con validación en `Moneda` (código y nombre) y `TipoCotizacion` (nombre).
- Corrección: formato PEP8 en `entities.py` (espacios, líneas en blanco entre clases, líneas de hasta 79 caracteres) y docstring del módulo al comienzo del archivo.
- Corrección: typos en docstrings y en los `__str__` de las entidades, y eliminación de comentarios fuera de funciones, clases y métodos.

## [Ejercicio 1]
- Corrección: `requirements.txt` ya no lista `requests` ni `beautifulsoup4`, porque el sprint no usa librerías externas.
- Corrección: se normaliza el formato del encabezado `[Ejercicio 7 ]` a `[Ejercicio 7]`.

## [Ejercicio 5]
- Corrección: se separan los datos en un CSV por entidad (generos, editoriales, monedas, tipos_cotizacion, libros, precios, stock, cotizaciones), con id propio y claves foráneas por id.
- Corrección: se elimina `datos_base.csv`, que mezclaba cuatro entidades, y `libros.csv` deja de incluir precio y stock.
- Corrección: `preload_data.py` lee los nuevos CSV, resuelve la ruta desde la ubicación del archivo y relaciona las entidades por id.

## [Ejercicio 7]
- Creación del archivo `main.py` como punto de entrada del sistema.
- Inicialización de `ConsolaUI` y ejecución del menú principal.

## [Ejercicio 6]
- Creación de la interfaz de consola en `ui/console.py` (clase ConsolaUI).
- Implementación completa del CRUD mediante menús interactivos para las 8 entidades (Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar).
- Creación y configuración de `main.py` como punto de entrada principal de la aplicación.
- Integración de la capa de presentación (UI) con los servicios del sistema.

## [Ejercicio 5]
- Creación de archivos CSV para la carga inicial de datos.
- Se utilizaron los archivos `datos_base.csv`, `libros.csv` y `cotizaciones.csv`.
- Se cargan al menos 10 registros por cada clase del dominio.
- Implementación de `preload_data.py` para leer los CSV y crear las entidades correspondientes.
- Integración de la carga inicial con los repositorios utilizados por la interfaz de consola.

## [Ejercicio 4]
- Implementación de la capa de servicios en `services.py`.
- Creación de `ServicioGenerico` para las operaciones de crear, buscar por id, listar, actualizar y eliminar.
- Creación de servicios específicos para `Stock` y `CotizacionDolar`, utilizando sus respectivos repositorios.
- Integración entre la capa de servicios, las entidades y los repositorios.
- Pruebas de las operaciones CRUD para verificar el correcto funcionamiento de los servicios.

## [Ejercicio 3]
- Definición de la interfaz genérica IRepositorio[T] (crear, leer_por_id, leer_todos, actualizar, eliminar) y su implementación en memoria RepositorioGenerico.
- Definición de interfaces específicas IRepositorioStock e IRepositorioCotizacionDolar (con clave propia: libro_id, y tipo+fecha respectivamente) y sus implementaciones.

## [Ejercicio 2]
- Definición de las entidades del dominio: EntidadBase, Genero, Editorial, Moneda, TipoCotizacion, CotizacionDolar, Libro, Precio, Stock.
- Aplicación de encapsulamiento (atributos privados con `__`, properties con validación en los setters).
- Relaciones por composición entre entidades (Libro-Genero, Libro-Editorial, Precio-Libro, Precio-Moneda, Stock-Libro, CotizacionDolar-TipoCotizacion).

## [Ejercicio 1]
- Inicialización del repositorio y creación de la rama Sprint_1.
- Creación de la estructura de directorios del proyecto.
- Creación de paquetes Python (`__init__.py`) en cada módulo.
- Creación de la carpeta migrations/csv para los archivos de datos.
- Agregado de README.md con objetivo e introducción del Sprint 1.
- Agregado de .gitignore y requirements.txt.