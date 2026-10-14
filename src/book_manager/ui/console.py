import os
import csv
from datetime import date, datetime
from typing import Optional

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, Genero, Libro, Moneda, Precio, Stock,
    TipoCotizacion)
from book_manager.services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio, ServicioStock,
    ServicioTipoCotizacion)


class ConsolaUI:
    """Interfaz de consola. Recibe los servicios ya construidos."""

    def __init__(self, svc_generos: ServicioGenero,
                 svc_editoriales: ServicioEditorial,
                 svc_libros: ServicioLibro,
                 svc_stock: ServicioStock,
                 svc_monedas: ServicioMoneda,
                 svc_tipos_cotizacion: ServicioTipoCotizacion,
                 svc_precios: ServicioPrecio,
                 svc_cotizaciones: ServicioCotizacionDolar) -> None:
        self.svc_generos = svc_generos
        self.svc_editoriales = svc_editoriales
        self.svc_libros = svc_libros
        self.svc_stock = svc_stock
        self.svc_monedas = svc_monedas
        self.svc_tipos_cotizacion = svc_tipos_cotizacion
        self.svc_precios = svc_precios
        self.svc_cotizaciones = svc_cotizaciones

    def _pedir_entero(self, mensaje: str) -> Optional[int]:
        """Pide un número entero por consola.

        Returns:
            El número ingresado, o None (con aviso) si no es un entero.
        """
        try:
            return int(input(mensaje))
        except ValueError:
            print("Error: Debe ingresar un número entero.")
            return None

    def _pedir_entero_o_actual(self, mensaje: str,
                               actual: int) -> Optional[int]:
        """Pide un entero; si se deja vacío, devuelve el valor actual.

        Returns:
            El número ingresado, el valor actual si no se escribió nada,
            o None (con aviso) si lo escrito no es un entero.
        """
        texto = input(mensaje)
        if texto == "":
            return actual
        try:
            return int(texto)
        except ValueError:
            print("Error: Debe ingresar un número entero.")
            return None

    def _pedir_decimal(self, mensaje: str,
                       actual: Optional[float] = None) -> Optional[float]:
        """Pide un número decimal por consola.

        Si se deja vacío y hay valor actual, devuelve el valor actual.

        Returns:
            El número, el valor actual, o None (con aviso) si no es válido.
        """
        texto = input(mensaje)
        if texto == "" and actual is not None:
            return actual
        try:
            return float(texto)
        except ValueError:
            print("Error: Debe ingresar un número (use punto: 1500.50).")
            return None

    def _pedir_fecha(self, mensaje: str,
                     actual: Optional[date] = None) -> Optional[date]:
        """Pide una fecha con formato AAAA-MM-DD.

        Si se deja vacía y hay valor actual, devuelve el valor actual.

        Returns:
            La fecha, el valor actual, o None (con aviso) si no es válida.
        """
        texto = input(mensaje)
        if texto == "" and actual is not None:
            return actual
        try:
            return datetime.strptime(texto, '%Y-%m-%d').date()
        except ValueError:
            print("Error: La fecha debe tener formato AAAA-MM-DD.")
            return None

    def iniciar(self) -> None:
        while True:
            print("\n" + "="*30)
            print(" BOOK MANAGER - MENÚ PRINCIPAL ")
            print("="*30)
            print("1. Gestionar Géneros")
            print("2. Gestionar Stock")
            print("3. Gestionar Libros")
            print("4. Gestionar Editoriales")
            print("5. Gestionar Monedas")
            print("6. Gestionar Tipos de Cotización")
            print("7. Gestionar Precios")
            print("8. Gestionar Cotización del Dólar")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.menu_generos()
            elif opcion == '2':
                self.menu_stock()
            elif opcion == '3':
                self.menu_libros()
            elif opcion == '4':
                self.menu_editoriales()
            elif opcion == '5':
                self.menu_monedas()
            elif opcion == '6':
                self.menu_tipos_cotizacion()
            elif opcion == '7':
                self.menu_precios()
            elif opcion == '8':
                self.menu_cotizaciones()
            elif opcion == '0':
                print("Saliendo del sistema...")
                break
            else:
                print("Opción no válida. Intente nuevamente.")

    # ==========================================
    # CRUD GÉNEROS (Ejemplo Servicio Genérico)
    # ==========================================
    def menu_generos(self) -> None:
        while True:
            print("\n--- MENÚ GÉNEROS ---")
            print("1. Crear Género")
            print("2. Listar Géneros")
            print("3. Buscar Género por ID")
            print("4. Actualizar Género")
            print("5. Eliminar Género")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_gen = self._pedir_entero("Ingrese ID del género: ")
                if id_gen is None:
                    continue
                nombre = input("Ingrese nombre del género: ")
                try:
                    self.svc_generos.crear(Genero(id=id_gen, nombre=nombre))
                    print(f"Éxito: Género '{nombre}' creado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                generos = self.svc_generos.listar()
                if not generos:
                    print("No hay géneros registrados.")
                for g in generos:
                    print(g)

            elif opcion == '3':
                id_gen = self._pedir_entero("Ingrese ID a buscar: ")
                if id_gen is None:
                    continue
                genero = self.svc_generos.buscar_por_id(id_gen)
                if genero:
                    print(genero)
                else:
                    print("Género no encontrado.")

            elif opcion == '4':
                id_gen = self._pedir_entero(
                    "Ingrese ID del género a actualizar: ")
                if id_gen is None:
                    continue
                genero = self.svc_generos.buscar_por_id(id_gen)
                if genero is None:
                    print("Género no encontrado.")
                    continue
                nuevo_nombre = input(
                    f"Ingrese nuevo nombre (Actual: {genero.nombre}): ")
                try:
                    self.svc_generos.actualizar(
                        Genero(id=id_gen, nombre=nuevo_nombre))
                    print("Género actualizado con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_gen = self._pedir_entero(
                    "Ingrese ID del género a eliminar: ")
                if id_gen is None:
                    continue
                try:
                    if self.svc_generos.eliminar(id_gen):
                        print("Género eliminado.")
                    else:
                        print("No se encontró el género para eliminar.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD STOCK (Ejemplo Servicio Específico)
    # ==========================================
    def menu_stock(self) -> None:
        while True:
            print("\n--- MENÚ STOCK ---")
            print("1. Crear Stock para un Libro")
            print("2. Listar Stock")
            print("3. Buscar Stock por ID de Libro")
            print("4. Actualizar Stock de un Libro")
            print("5. Eliminar Stock de un Libro")
            print("0. Volver")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_stock = self._pedir_entero(
                    "Ingrese ID del registro de stock: ")
                if id_stock is None:
                    continue
                id_libro = self._pedir_entero(
                    "Ingrese ID del libro asociado: ")
                if id_libro is None:
                    continue
                cantidad = self._pedir_entero("Ingrese cantidad: ")
                if cantidad is None:
                    continue
                libro = self.svc_libros.buscar_por_id(id_libro)
                if libro is None:
                    print("Libro no encontrado.")
                    continue
                try:
                    self.svc_stock.crear(
                        Stock(id=id_stock, libro=libro, cantidad=cantidad))
                    print("Éxito: Stock creado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                hay_stock = False
                for libro in self.svc_libros.listar():
                    stock = self.svc_stock.buscar_por_libro(libro.id)
                    if stock:
                        print(stock)
                        hay_stock = True
                if not hay_stock:
                    print("No hay stock registrado.")

            elif opcion == '3':
                id_libro = self._pedir_entero("Ingrese ID del libro: ")
                if id_libro is None:
                    continue
                stock = self.svc_stock.buscar_por_libro(id_libro)
                if stock:
                    print(stock)
                else:
                    print("No hay stock para ese libro.")

            elif opcion == '4':
                id_libro = self._pedir_entero("Ingrese ID del libro: ")
                if id_libro is None:
                    continue
                existente = self.svc_stock.buscar_por_libro(id_libro)
                if existente is None:
                    print("No hay stock para ese libro.")
                    continue
                cantidad = self._pedir_entero(
                    f"Nueva cantidad (actual: {existente.cantidad}): ")
                if cantidad is None:
                    continue
                try:
                    self.svc_stock.actualizar(
                        Stock(id=existente.id, libro=existente.libro,
                              cantidad=cantidad))
                    print("Stock actualizado con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_libro = self._pedir_entero("Ingrese ID del libro: ")
                if id_libro is None:
                    continue
                try:
                    if self.svc_stock.eliminar(id_libro):
                        print("Stock eliminado.")
                    else:
                        print("No hay stock para ese libro.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD EDITORIALES
    # ==========================================
    def menu_editoriales(self) -> None:
        while True:
            print("\n--- MENÚ EDITORIALES ---")
            print("1. Crear Editorial")
            print("2. Listar Editoriales")
            print("3. Buscar Editorial por ID")
            print("4. Actualizar Editorial")
            print("5. Eliminar Editorial")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_ed = self._pedir_entero("Ingrese ID de la editorial: ")
                if id_ed is None:
                    continue
                nombre = input("Ingrese nombre: ")
                sede = input("Ingrese sede: ")
                try:
                    self.svc_editoriales.crear(
                        Editorial(id=id_ed, nombre=nombre, sede=sede))
                    print(f"Éxito: Editorial '{nombre}' creada.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                editoriales = self.svc_editoriales.listar()
                if not editoriales:
                    print("No hay editoriales registradas.")
                for ed in editoriales:
                    print(ed)

            elif opcion == '3':
                id_ed = self._pedir_entero("Ingrese ID a buscar: ")
                if id_ed is None:
                    continue
                editorial = self.svc_editoriales.buscar_por_id(id_ed)
                if editorial:
                    print(editorial)
                else:
                    print("Editorial no encontrada.")

            elif opcion == '4':
                id_ed = self._pedir_entero(
                    "Ingrese ID de la editorial a actualizar: ")
                if id_ed is None:
                    continue
                existente = self.svc_editoriales.buscar_por_id(id_ed)
                if existente is None:
                    print("Editorial no encontrada.")
                    continue
                nuevo_nombre = input(
                    f"Ingrese nuevo nombre (Actual: {existente.nombre}): ")
                nueva_sede = input(
                    f"Ingrese nueva sede (Actual: {existente.sede}): ")
                try:
                    self.svc_editoriales.actualizar(
                        Editorial(id=id_ed, nombre=nuevo_nombre,
                                  sede=nueva_sede))
                    print("Editorial actualizada con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_ed = self._pedir_entero(
                    "Ingrese ID de la editorial a eliminar: ")
                if id_ed is None:
                    continue
                try:
                    if self.svc_editoriales.eliminar(id_ed):
                        print("Editorial eliminada.")
                    else:
                        print("No se encontró la editorial.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD LIBROS
    # ==========================================
    def menu_libros(self) -> None:
        while True:
            print("\n--- MENÚ LIBROS ---")
            print("1. Crear Libro")
            print("2. Listar Libros")
            print("3. Buscar Libro por ID")
            print("4. Actualizar Libro")
            print("5. Eliminar Libro")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_libro = self._pedir_entero("Ingrese ID del Libro: ")
                if id_libro is None:
                    continue
                isbn = input("Ingrese ISBN: ")
                titulo = input("Ingrese Título: ")
                autor = input("Ingrese Autor: ")

                # Validar y obtener Género
                id_gen = self._pedir_entero(
                    "Ingrese ID del Género existente: ")
                if id_gen is None:
                    continue
                genero_obj = self.svc_generos.buscar_por_id(id_gen)
                if genero_obj is None:
                    print("Error: El Género no existe. Abortando creación.")
                    continue

                # Validar y obtener Editorial
                id_ed = self._pedir_entero(
                    "Ingrese ID de la Editorial existente: ")
                if id_ed is None:
                    continue
                editorial_obj = self.svc_editoriales.buscar_por_id(id_ed)
                if editorial_obj is None:
                    print("Error: La Editorial no existe. Abortando creación.")
                    continue

                try:
                    self.svc_libros.crear(Libro(
                        id=id_libro, isbn=isbn, titulo=titulo, autor=autor,
                        genero=genero_obj, editorial=editorial_obj))
                    print(f"Éxito: Libro '{titulo}' creado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                libros = self.svc_libros.listar()
                if not libros:
                    print("No hay libros registrados.")
                for lib in libros:
                    print(lib)

            elif opcion == '3':
                id_libro = self._pedir_entero("Ingrese ID a buscar: ")
                if id_libro is None:
                    continue
                libro = self.svc_libros.buscar_por_id(id_libro)
                if libro:
                    print(libro)
                else:
                    print("Libro no encontrado.")

            elif opcion == '4':
                id_libro = self._pedir_entero(
                    "Ingrese ID del Libro a actualizar: ")
                if id_libro is None:
                    continue
                existente = self.svc_libros.buscar_por_id(id_libro)
                if existente is None:
                    print("Libro no encontrado.")
                    continue

                print("Enter sin escribir nada mantiene el valor actual.")
                isbn = input(f"ISBN (actual: {existente.isbn}): ")
                isbn = isbn or existente.isbn
                titulo = input(f"Título (actual: {existente.titulo}): ")
                titulo = titulo or existente.titulo
                autor = input(f"Autor (actual: {existente.autor}): ")
                autor = autor or existente.autor

                id_gen = self._pedir_entero_o_actual(
                    f"ID de género (actual: {existente.genero.id}): ",
                    existente.genero.id)
                if id_gen is None:
                    continue
                genero = self.svc_generos.buscar_por_id(id_gen)
                if genero is None:
                    print("Error: El Género no existe. Abortando.")
                    continue

                id_ed = self._pedir_entero_o_actual(
                    f"ID de editorial (actual: {existente.editorial.id}): ",
                    existente.editorial.id)
                if id_ed is None:
                    continue
                editorial = self.svc_editoriales.buscar_por_id(id_ed)
                if editorial is None:
                    print("Error: La Editorial no existe. Abortando.")
                    continue

                try:
                    self.svc_libros.actualizar(Libro(
                        id=id_libro, isbn=isbn, titulo=titulo,
                        autor=autor, genero=genero, editorial=editorial))
                    print("Libro actualizado con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_libro = self._pedir_entero(
                    "Ingrese ID del Libro a eliminar: ")
                if id_libro is None:
                    continue
                try:
                    if self.svc_libros.eliminar(id_libro):
                        print(f"Libro '{id_libro}' eliminado.")
                    else:
                        print("No se encontró el libro.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD MONEDAS
    # ==========================================
    def menu_monedas(self) -> None:
        while True:
            print("\n--- MENÚ MONEDAS ---")
            print("1. Crear Moneda")
            print("2. Listar Monedas")
            print("3. Buscar Moneda por ID")
            print("4. Actualizar Moneda")
            print("5. Eliminar Moneda")
            print("0. Volver")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_mon = self._pedir_entero("Ingrese ID de la moneda: ")
                if id_mon is None:
                    continue
                codigo = input("Ingrese código (ej. ARS, USD): ")
                nombre = input("Ingrese nombre: ")
                try:
                    self.svc_monedas.crear(
                        Moneda(id=id_mon, codigo=codigo, nombre=nombre))
                    print(f"Éxito: Moneda '{nombre}' creada.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                monedas = self.svc_monedas.listar()
                if not monedas:
                    print("No hay monedas registradas.")
                for m in monedas:
                    print(m)

            elif opcion == '3':
                id_mon = self._pedir_entero("Ingrese ID a buscar: ")
                if id_mon is None:
                    continue
                moneda = self.svc_monedas.buscar_por_id(id_mon)
                if moneda:
                    print(moneda)
                else:
                    print("Moneda no encontrada.")

            elif opcion == '4':
                id_mon = self._pedir_entero(
                    "Ingrese ID de la moneda a actualizar: ")
                if id_mon is None:
                    continue
                existente = self.svc_monedas.buscar_por_id(id_mon)
                if existente is None:
                    print("Moneda no encontrada.")
                    continue
                print("Enter sin escribir nada mantiene el valor actual.")
                codigo = input(f"Código (actual: {existente.codigo}): ")
                codigo = codigo or existente.codigo
                nombre = input(f"Nombre (actual: {existente.nombre}): ")
                nombre = nombre or existente.nombre
                try:
                    self.svc_monedas.actualizar(
                        Moneda(id=id_mon, codigo=codigo, nombre=nombre))
                    print("Moneda actualizada con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_mon = self._pedir_entero(
                    "Ingrese ID de la moneda a eliminar: ")
                if id_mon is None:
                    continue
                try:
                    if self.svc_monedas.eliminar(id_mon):
                        print("Moneda eliminada.")
                    else:
                        print("No se encontró la moneda.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD TIPOS DE COTIZACIÓN
    # ==========================================
    def menu_tipos_cotizacion(self) -> None:
        while True:
            print("\n--- MENÚ TIPOS COTIZACIÓN ---")
            print("1. Crear Tipo")
            print("2. Listar Tipos")
            print("3. Buscar Tipo por ID")
            print("4. Actualizar Tipo")
            print("5. Eliminar Tipo")
            print("0. Volver")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_tipo = self._pedir_entero(
                    "Ingrese el ID del tipo de cotización: ")
                if id_tipo is None:
                    continue
                nombre = input("Ingrese nombre del tipo de cotización: ")
                try:
                    self.svc_tipos_cotizacion.crear(
                        TipoCotizacion(id=id_tipo, nombre=nombre))
                    print("Tipo de cotización creado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                tipos = self.svc_tipos_cotizacion.listar()
                if not tipos:
                    print("No hay tipos de cotización registrados.")
                for t in tipos:
                    print(t)

            elif opcion == '3':
                id_tipo = self._pedir_entero("Ingrese ID a buscar: ")
                if id_tipo is None:
                    continue
                tipo = self.svc_tipos_cotizacion.buscar_por_id(id_tipo)
                if tipo:
                    print(tipo)
                else:
                    print("Tipo de cotización no encontrado.")

            elif opcion == '4':
                id_tipo = self._pedir_entero(
                    "Ingrese el ID del tipo de cotización a actualizar: ")
                if id_tipo is None:
                    continue
                existente = self.svc_tipos_cotizacion.buscar_por_id(id_tipo)
                if existente is None:
                    print("Tipo de cotización no encontrado.")
                    continue
                nuevo_nombre = input(
                    f"Nuevo nombre (actual: {existente.nombre}): ")
                try:
                    self.svc_tipos_cotizacion.actualizar(
                        TipoCotizacion(id=id_tipo, nombre=nuevo_nombre))
                    print("Tipo de cotización actualizado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_tipo = self._pedir_entero(
                    "Ingrese el ID del tipo de cotización a eliminar: ")
                if id_tipo is None:
                    continue
                try:
                    if self.svc_tipos_cotizacion.eliminar(id_tipo):
                        print("Tipo de cotización eliminado.")
                    else:
                        print("No se encontró el tipo de cotización.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD PRECIOS
    # ==========================================
    def menu_precios(self) -> None:
        while True:
            print("\n--- MENÚ PRECIOS ---")
            print("1. Crear Precio")
            print("2. Listar Precios")
            print("3. Buscar Precio por ID")
            print("4. Actualizar Precio (monto y fecha)")
            print("5. Eliminar Precio")
            print("6. Ver Lista de Precios Bimonetaria")
            print("7. Exportar Precios de Todas las Monedas a CSV")
            print("0. Volver")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_precio = self._pedir_entero("Ingrese ID del precio: ")
                if id_precio is None:
                    continue
                id_libro = self._pedir_entero("Ingrese ID del libro: ")
                if id_libro is None:
                    continue
                libro = self.svc_libros.buscar_por_id(id_libro)
                if libro is None:
                    print("Error: El Libro no existe. Abortando creación.")
                    continue
                id_moneda = self._pedir_entero("Ingrese ID de la moneda: ")
                if id_moneda is None:
                    continue
                moneda = self.svc_monedas.buscar_por_id(id_moneda)
                if moneda is None:
                    print("Error: La Moneda no existe. Abortando creación.")
                    continue
                monto = self._pedir_decimal("Ingrese monto: ")
                if monto is None:
                    continue
                fecha = self._pedir_fecha(
                    "Ingrese fecha de vigencia (AAAA-MM-DD): ")
                if fecha is None:
                    continue
                try:
                    self.svc_precios.crear(Precio(
                        id=id_precio, libro=libro, moneda=moneda,
                        monto=monto, fecha_vigencia=fecha))
                    print("Éxito: Precio creado.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                precios = self.svc_precios.listar()
                if not precios:
                    print("No hay precios registrados.")
                for p in precios:
                    print(p)

            elif opcion == '3':
                id_precio = self._pedir_entero("Ingrese ID a buscar: ")
                if id_precio is None:
                    continue
                precio = self.svc_precios.buscar_por_id(id_precio)
                if precio:
                    print(precio)
                else:
                    print("Precio no encontrado.")

            elif opcion == '4':
                id_precio = self._pedir_entero(
                    "Ingrese ID del precio a actualizar: ")
                if id_precio is None:
                    continue
                existente = self.svc_precios.buscar_por_id(id_precio)
                if existente is None:
                    print("Precio no encontrado.")
                    continue
                print("Enter sin escribir nada mantiene el valor actual.")
                monto = self._pedir_decimal(
                    f"Monto (actual: {existente.monto}): ", existente.monto)
                if monto is None:
                    continue
                fecha = self._pedir_fecha(
                    f"Fecha (actual: {existente.fecha_vigencia}): ",
                    existente.fecha_vigencia)
                if fecha is None:
                    continue
                try:
                    self.svc_precios.actualizar(Precio(
                        id=id_precio, libro=existente.libro,
                        moneda=existente.moneda, monto=monto,
                        fecha_vigencia=fecha))
                    print("Precio actualizado con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_precio = self._pedir_entero(
                    "Ingrese ID del precio a eliminar: ")
                if id_precio is None:
                    continue
                try:
                    if self.svc_precios.eliminar(id_precio):
                        print("Precio eliminado.")
                    else:
                        print("No se encontró el precio.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '6':
                tipos = self.svc_tipos_cotizacion.listar()

                if not tipos:
                    print("No hay tipos de cotización registrados.")
                    continue

                print("\nTipos de cotización disponibles:")
                for tipo in tipos:
                    print(f"{tipo.id}. {tipo.nombre}")

                id_tipo = self._pedir_entero(
                    "Ingrese ID del tipo de cotización: ")
                if id_tipo is None:
                    continue

                cotizaciones = self.svc_cotizaciones.listar_historico(
                    id_tipo)

                if not cotizaciones:
                    print("No hay cotizaciones para ese tipo.")
                    continue

                cotizacion = max(
                    cotizaciones,
                    key=lambda c: c.fecha)

                precios = self.svc_precios.listar()

                print("\n--- LISTA DE PRECIOS BIMONETARIA ---")
                print(
                    f"Cotización utilizada: "
                    f"{cotizacion.tipo_cotizacion.nombre} "
                    f"(${cotizacion.valor_venta:.2f})")

                print("-" * 60)
                print(f"{'Libro':<25} | {'Precio ARS':>15} | {'Precio USD':>10}")
                print("-" * 60)

                for precio in precios:
                    if precio.moneda.codigo.upper() == 'ARS':
                        precio_usd = (
                            precio.monto / cotizacion.valor_venta)

                        print(
                            f"{precio.libro.titulo:<25} "
                            f"| ARS: ${precio.monto:>10.2f} "
                            f"| USD: {precio_usd:>8.2f}")

            elif opcion == '7':
                precios = self.svc_precios.listar()
                tipos = self.svc_tipos_cotizacion.listar()

                precios_ars = [
                    precio for precio in precios
                    if precio.moneda.codigo.upper() == 'ARS'
                ]

                if not precios_ars:
                    print("No hay precios en pesos para exportar.")
                    continue

                cotizaciones_actuales = []

                for tipo in tipos:
                    cotizaciones = self.svc_cotizaciones.listar_historico(
                        tipo.id)

                    if cotizaciones:
                        ultima = max(
                            cotizaciones,
                            key=lambda c: c.fecha)

                        cotizaciones_actuales.append(ultima)

                if not cotizaciones_actuales:
                    print("No hay cotizaciones disponibles.")
                    continue

                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))

                nombre_archivo = os.path.join(
                    base_dir, "exports", "precios_exportados.csv"

                )

                with open(
                        nombre_archivo, 'w', newline='',
                        encoding='utf-8-sig') as archivo:

                    writer = csv.writer(
                        archivo,
                        delimiter=';'
                    )

                    encabezado = [
                        'Libro',
                        'Precio ARS'
                    ]

                    for cotizacion in cotizaciones_actuales:
                        encabezado.append(
                            f"{cotizacion.tipo_cotizacion.nombre} USD"
                        )

                    writer.writerow(encabezado)

                    for precio in precios_ars:
                        fila = [
                            precio.libro.titulo,
                            f"{precio.monto:.2f}"
                        ]

                        for cotizacion in cotizaciones_actuales:
                            precio_usd = (
                                precio.monto /
                                cotizacion.valor_venta
                            )

                            fila.append(
                                f"{precio_usd:.2f}"
                            )

                        writer.writerow(fila)

                print(
                    f"Precios exportados correctamente a "
                    f"'{nombre_archivo}'.")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")

    # ==========================================
    # CRUD COTIZACIÓN DEL DÓLAR
    # ==========================================
    def menu_cotizaciones(self) -> None:
        while True:
            print("\n--- MENÚ COTIZACIÓN DEL DÓLAR ---")
            print("1. Crear Cotización")
            print("2. Listar Cotizaciones")
            print("3. Buscar por Tipo y Fecha")
            print("4. Actualizar Cotización (valores)")
            print("5. Eliminar Cotización")
            print("6. Obtener Cotizaciones por API")
            print("0. Volver")

            opcion = input("Seleccione: ")

            if opcion == '1':
                id_cot = self._pedir_entero("Ingrese ID de la cotización: ")
                if id_cot is None:
                    continue
                id_tipo = self._pedir_entero(
                    "Ingrese ID del tipo de cotización: ")
                if id_tipo is None:
                    continue
                tipo = self.svc_tipos_cotizacion.buscar_por_id(id_tipo)
                if tipo is None:
                    print("Error: El Tipo no existe. Abortando creación.")
                    continue
                fecha = self._pedir_fecha("Ingrese fecha (AAAA-MM-DD): ")
                if fecha is None:
                    continue
                compra = self._pedir_decimal("Ingrese valor de compra: ")
                if compra is None:
                    continue
                venta = self._pedir_decimal("Ingrese valor de venta: ")
                if venta is None:
                    continue
                try:
                    self.svc_cotizaciones.crear(CotizacionDolar(
                        id=id_cot, tipo_cotizacion=tipo, fecha=fecha,
                        valor_compra=compra, valor_venta=venta))
                    print("Éxito: Cotización creada.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '2':
                hay_cotizaciones = False

                for tipo in self.svc_tipos_cotizacion.listar():
                    cotizaciones = self.svc_cotizaciones.listar_historico(
                        tipo.id)

                    if cotizaciones:
                        ultima = max(
                            cotizaciones,
                            key=lambda c: c.fecha
                        )
                        print(ultima)
                        hay_cotizaciones = True
                if not hay_cotizaciones:
                    print("No hay cotizaciones registradas.")

            elif opcion == '3':
                id_tipo = self._pedir_entero(
                    "Ingrese ID del tipo de cotización: ")
                if id_tipo is None:
                    continue
                fecha = self._pedir_fecha("Ingrese fecha (AAAA-MM-DD): ")
                if fecha is None:
                    continue
                cotizacion = self.svc_cotizaciones.buscar_por_tipo_y_fecha(
                    id_tipo, fecha)
                if cotizacion:
                    print(cotizacion)
                else:
                    print("Cotización no encontrada.")

            elif opcion == '4':
                id_tipo = self._pedir_entero(
                    "Ingrese ID del tipo de cotización: ")
                if id_tipo is None:
                    continue
                fecha = self._pedir_fecha("Ingrese fecha (AAAA-MM-DD): ")
                if fecha is None:
                    continue
                existente = self.svc_cotizaciones.buscar_por_tipo_y_fecha(
                    id_tipo, fecha)
                if existente is None:
                    print("Cotización no encontrada.")
                    continue
                print("Enter sin escribir nada mantiene el valor actual.")
                compra = self._pedir_decimal(
                    f"Compra (actual: {existente.valor_compra}): ",
                    existente.valor_compra)
                if compra is None:
                    continue
                venta = self._pedir_decimal(
                    f"Venta (actual: {existente.valor_venta}): ",
                    existente.valor_venta)
                if venta is None:
                    continue
                try:
                    self.svc_cotizaciones.actualizar(CotizacionDolar(
                        id=existente.id,
                        tipo_cotizacion=existente.tipo_cotizacion,
                        fecha=existente.fecha, valor_compra=compra,
                        valor_venta=venta))
                    print("Cotización actualizada con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '5':
                id_tipo = self._pedir_entero(
                    "Ingrese ID del tipo de cotización: ")
                if id_tipo is None:
                    continue
                fecha = self._pedir_fecha("Ingrese fecha (AAAA-MM-DD): ")
                if fecha is None:
                    continue
                try:
                    if self.svc_cotizaciones.eliminar(id_tipo, fecha):
                        print("Cotización eliminada.")
                    else:
                        print("No se encontró la cotización.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '6':
                try:
                    cotizaciones = self.svc_cotizaciones.obtener_cotizaciones()
                    for c in cotizaciones:
                        print(c)
                    print("Cotizaciones obtenidas y registradas con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == '0':
                break

            else:
                print("Opción no válida.")
