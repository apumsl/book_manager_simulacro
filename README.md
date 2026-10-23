# Book Manager
Tomar el sitio Cúspide como referencia para el trabajo.
[Cúspide](https://cuspide.com/)

## Sprint actual: Sprint 3

## Objetivo
Aplicar los conocimientos adquiridos en programación orientada a objetos y persistencia de datos, incorporando la obtención de información desde la web mediante scraping para comparar los precios internos con los de la competencia.

## Introducción y contexto
Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación de material bibliográfico, el sistema debe gestionar precios en diferentes monedas y seguir la cotización del dólar para actualizar sus valores en tiempo real.

Se desarrolla una aplicación de consola (CLI) en Python que permite gestionar el inventario, cotizar los libros según el valor del dólar y comparar precios con la competencia web (referencia: Cúspide).

En este tercer sprint, partiendo de la rama Sprint_2, se obtienen precios de librerías con venta online mediante un scraper desarrollado con Scrapy. Solo se buscan los libros del catálogo propio. Con esos datos se generan alertas de diferencia de precios en CSV y un reporte en Excel. Además, se incorpora la carga de datos desde scripts SQL y la auditoría de todas las operaciones del sistema mediante un decorador.

### Entidades
- Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar, Auditoria