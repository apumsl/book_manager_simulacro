# Book Manager
Tomar el sitio Cúspide como referencia para el trabajo.
[Cúspide](https://cuspide.com/)

## Sprint actual: Sprint 2

## Objetivo
Aplicar los conocimientos adquiridos en programación orientada a objetos y en bases de datos relacionales, persistiendo los datos con el ORM SQLAlchemy y consolidando normalización, conexión segura y carga inicial.

## Introducción y contexto
Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación de material bibliográfico, el sistema debe gestionar precios en diferentes monedas y seguir la cotización del dólar para actualizar sus valores en tiempo real.

Se desarrolla una aplicación de consola (CLI) en Python que permite gestionar el inventario, cotizar los libros según el valor del dólar y comparar precios con la competencia web (referencia: Cúspide).

En este segundo sprint la aplicación persiste en una base de datos relacional mediante SQLAlchemy. Los datos cargados en los archivos CSV se migran a tablas relacionales y se consultan APIs externas para obtener la cotización del dólar.

### Entidades
- Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar

