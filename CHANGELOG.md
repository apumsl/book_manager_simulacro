# Changelog

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