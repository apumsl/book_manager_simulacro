from datetime import datetime

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

    def iniciar(self):
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
    def menu_generos(self):
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
                try:
                    id_gen = int(input("Ingrese ID del género: "))
                    nombre = input("Ingrese nombre del género: ")
                    nuevo_genero = Genero(id=id_gen, nombre=nombre)
                    self.svc_generos.crear(nuevo_genero)
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
                try:
                    id_gen = int(input("Ingrese ID a buscar: "))
                    genero = self.svc_generos.buscar_por_id(id_gen)
                    if genero:
                        print(genero)
                    else:
                        print("Género no encontrado.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '4':
                try:
                    id_gen = int(input("Ingrese ID del género a actualizar: "))
                    genero_existente = self.svc_generos.buscar_por_id(id_gen)
                    if genero_existente:
                        nuevo_nombre = input(f"Ingrese nuevo nombre (Actual: {genero_existente.nombre}): ")
                        genero_actualizado = Genero(id=id_gen, nombre=nuevo_nombre)
                        self.svc_generos.actualizar(genero_actualizado)
                        print("Género actualizado con éxito.")
                    else:
                        print("Género no encontrado.")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif opcion == '5':
                try:
                    id_gen = int(input("Ingrese ID del género a eliminar: "))
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
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

    # ==========================================
    # CRUD STOCK (Ejemplo Servicio Específico)
    # ==========================================
    def menu_stock(self):
        while True:
            print("\n--- MENÚ STOCK ---")
            print("1. Crear/Registrar Stock para un Libro")
            print("2. Buscar Stock por ID de Libro")
            print("3. Actualizar Stock")
            print("4. Eliminar Stock de un Libro")
            print("0. Volver")
            
            opcion = input("Seleccione: ")
            
            if opcion == '1':
                try:
                    id_stock = int(input("Ingrese ID del registro de stock: "))
                    id_libro = int(input("Ingrese ID del libro asociado: "))
                    
                    # Verificamos que el libro exista primero
                    libro = self.svc_libros.buscar_por_id(id_libro)
                    if not libro:
                        print(f"Error: No existe un libro con ID {id_libro}. Cree el libro primero.")
                        continue
                        
                    cantidad = int(input("Ingrese cantidad en stock: "))
                    nuevo_stock = Stock(id=id_stock, libro=libro, cantidad=cantidad)
                    self.svc_stock.crear(nuevo_stock)
                    print("Stock registrado con éxito.")
                except ValueError as e:
                    print(f"Error: {e}")
            
            elif opcion == '2':
                try:
                    id_libro = int(input("Ingrese ID del libro para consultar su stock: "))
                    stock = self.svc_stock.buscar_por_libro(id_libro)
                    if stock:
                        print(stock)
                    else:
                        print("No hay registro de stock para ese libro.")
                except ValueError:
                    print("Error: Ingrese un número válido.")
                    
            elif opcion == '3':
                try:
                    id_libro = int(input("Ingrese ID del libro para actualizar stock: "))
                    stock_existente = self.svc_stock.buscar_por_libro(id_libro)
                    if stock_existente:
                        nueva_cantidad = int(input(f"Ingrese nueva cantidad (Actual: {stock_existente.cantidad}): "))
                        stock_actualizado = Stock(id=stock_existente.id, libro=stock_existente.libro, cantidad=nueva_cantidad)
                        self.svc_stock.actualizar(stock_actualizado)
                        print("Stock actualizado.")
                    else:
                        print("Stock no encontrado para ese libro.")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif opcion == '4':
                try:
                    id_libro = int(input("Ingrese ID del libro para eliminar su registro de stock: "))
                    if self.svc_stock.eliminar(id_libro):
                        print("Registro de stock eliminado.")
                    else:
                        print("No se encontró registro de stock para ese libro.")
                except ValueError:
                    print("Error: Ingrese un número entero.")
                    
            elif opcion == '0':
                break

    # ==========================================
    # CRUD EDITORIALES
    # ==========================================
    def menu_editoriales(self):
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
                try:
                    id_ed = int(input("Ingrese ID de la editorial: "))
                    nombre = input("Ingrese nombre: ")
                    sede = input("Ingrese sede: ")
                    nueva_editorial = Editorial(id=id_ed, nombre=nombre, sede=sede)
                    self.svc_editoriales.crear(nueva_editorial)
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
                try:
                    id_ed = int(input("Ingrese ID a buscar: "))
                    editorial = self.svc_editoriales.buscar_por_id(id_ed)
                    if editorial:
                        print(editorial)
                    else:
                        print("Editorial no encontrada.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '4':
                try:
                    id_ed = int(input("Ingrese ID de la editorial a actualizar: "))
                    ed_existente = self.svc_editoriales.buscar_por_id(id_ed)
                    if ed_existente:
                        nuevo_nombre = input(f"Ingrese nuevo nombre (Actual: {ed_existente.nombre}): ")
                        nueva_sede = input(f"Ingrese nueva sede (Actual: {ed_existente.sede}): ")
                        ed_actualizada = Editorial(id=id_ed, nombre=nuevo_nombre, sede=nueva_sede)
                        self.svc_editoriales.actualizar(ed_actualizada)
                        print("Editorial actualizada con éxito.")
                    else:
                        print("Editorial no encontrada.")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif opcion == '5':
                try:
                    id_ed = int(input("Ingrese ID de la editorial a eliminar: "))
                    if self.svc_editoriales.eliminar(id_ed):
                        print("Editorial eliminada.")
                    else:
                        print("No se encontró la editorial.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '0':
                break

    # ==========================================
    # CRUD LIBROS
    # ==========================================
    def menu_libros(self):
        while True:
            print("\n--- MENÚ LIBROS ---")
            print("1. Crear Libro")
            print("2. Listar Libros")
            print("3. Buscar Libro por ID")
            print("4. Actualizar Libro (Título)")
            print("5. Eliminar Libro")
            print("0. Volver al Menú Principal")
            
            opcion = input("Seleccione: ")
            
            if opcion == '1':
                try:
                    id_libro = int(input("Ingrese ID del libro: "))
                    isbn = input("Ingrese ISBN: ")
                    titulo = input("Ingrese Título: ")
                    autor = input("Ingrese Autor: ")
                    
                    # Validar y obtener Género
                    id_gen = int(input("Ingrese ID del Género existente: "))
                    genero_obj = self.svc_generos.buscar_por_id(id_gen)
                    if not genero_obj:
                        print("Error: El Género no existe. Abortando creación.")
                        continue
                        
                    # Validar y obtener Editorial
                    id_ed = int(input("Ingrese ID de la Editorial existente: "))
                    editorial_obj = self.svc_editoriales.buscar_por_id(id_ed)
                    if not editorial_obj:
                        print("Error: La Editorial no existe. Abortando creación.")
                        continue
                        
                    nuevo_libro = Libro(id=id_libro, isbn=isbn, titulo=titulo, autor=autor, genero=genero_obj, editorial=editorial_obj)
                    self.svc_libros.crear(nuevo_libro)
                    print(f"Éxito: Libro '{titulo}' creado.")
                except ValueError as e:
                    print(f"Error en el ingreso de datos: {e}")
            
            elif opcion == '2':
                libros = self.svc_libros.listar()
                if not libros:
                    print("No hay libros registrados.")
                for lib in libros:
                    print(lib)
                    
            elif opcion == '3':
                try:
                    id_libro = int(input("Ingrese ID a buscar: "))
                    libro = self.svc_libros.buscar_por_id(id_libro)
                    if libro:
                        print(libro)
                    else:
                        print("Libro no encontrado.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '4':
                try:
                    id_libro = int(input("Ingrese ID del libro a actualizar: "))
                    lib_existente = self.svc_libros.buscar_por_id(id_libro)
                    if lib_existente:
                        nuevo_titulo = input(f"Ingrese nuevo título (Actual: {lib_existente.titulo}): ")
                        # Se reutilizan los objetos de la relación existente para esta actualización simple
                        lib_actualizado = Libro(id=id_libro, isbn=lib_existente.isbn, titulo=nuevo_titulo, autor=lib_existente.autor, genero=lib_existente.genero, editorial=lib_existente.editorial)
                        self.svc_libros.actualizar(lib_actualizado)
                        print("Libro actualizado con éxito.")
                    else:
                        print("Libro no encontrado.")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif opcion == '5':
                try:
                    id_libro = int(input("Ingrese ID del libro a eliminar: "))
                    if self.svc_libros.eliminar(id_libro):
                        print("Libro eliminado.")
                    else:
                        print("No se encontró el libro.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '0':
                break

    # ==========================================
    # CRUD EDITORIALES
    # ==========================================
    def menu_editoriales(self):
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
                try:
                    id_ed = int(input("Ingrese ID de la editorial: "))
                    nombre = input("Ingrese nombre: ")
                    sede = input("Ingrese sede: ")
                    nueva_editorial = Editorial(id=id_ed, nombre=nombre, sede=sede)
                    self.svc_editoriales.crear(nueva_editorial)
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
                try:
                    id_ed = int(input("Ingrese ID a buscar: "))
                    editorial = self.svc_editoriales.buscar_por_id(id_ed)
                    if editorial:
                        print(editorial)
                    else:
                        print("Editorial no encontrada.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '4':
                try:
                    id_ed = int(input("Ingrese ID de la editorial a actualizar: "))
                    ed_existente = self.svc_editoriales.buscar_por_id(id_ed)
                    if ed_existente:
                        nuevo_nombre = input(f"Ingrese nuevo nombre (Actual: {ed_existente.nombre}): ")
                        nueva_sede = input(f"Ingrese nueva sede (Actual: {ed_existente.sede}): ")
                        ed_actualizada = Editorial(id=id_ed, nombre=nuevo_nombre, sede=nueva_sede)
                        self.svc_editoriales.actualizar(ed_actualizada)
                        print("Editorial actualizada con éxito.")
                    else:
                        print("Editorial no encontrada.")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif opcion == '5':
                try:
                    id_ed = int(input("Ingrese ID de la editorial a eliminar: "))
                    if self.svc_editoriales.eliminar(id_ed):
                        print("Editorial eliminada.")
                    else:
                        print("No se encontró la editorial.")
                except ValueError:
                    print("Error: El ID debe ser un número entero.")
                    
            elif opcion == '0':
                break

    # ==========================================
    # CRUD MONEDAS
    # ==========================================
    def menu_monedas(self):
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
                try:
                    id_mon = int(input("Ingrese ID: "))
                    codigo = input("Ingrese código (ej. ARS, USD): ")
                    nombre = input("Ingrese nombre: ")
                    self.svc_monedas.crear(Moneda(id=id_mon, codigo=codigo, nombre=nombre))
                    print("Moneda creada.")
                except ValueError as e: print(f"Error: {e}")
            elif opcion == '2':
                for m in self.svc_monedas.listar(): print(m)
            elif opcion == '3':
                try:
                    m = self.svc_monedas.buscar_por_id(int(input("ID a buscar: ")))
                    print(m if m else "No encontrada.")
                except ValueError: print("Error de ID.")
            elif opcion == '4':
                try:
                    id_mon = int(input("ID a actualizar: "))
                    m = self.svc_monedas.buscar_por_id(id_mon)
                    if m:
                        self.svc_monedas.actualizar(Moneda(id=id_mon, codigo=input("Nuevo código: "), nombre=input("Nuevo nombre: ")))
                        print("Actualizada.")
                    else: print("No encontrada.")
                except ValueError as e: print(f"Error: {e}")
            elif opcion == '5':
                try: print("Eliminada." if self.svc_monedas.eliminar(int(input("ID a eliminar: "))) else "No encontrada.")
                except ValueError: print("Error de ID.")
            elif opcion == '0': break

    # ==========================================
    # CRUD TIPOS DE COTIZACIÓN
    # ==========================================
    def menu_tipos_cotizacion(self):
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
                try:
                    self.svc_tipos_cotizacion.crear(TipoCotizacion(id=int(input("ID: ")), nombre=input("Nombre (ej. Oficial, Blue): ")))
                    print("Tipo de cotización creado.")
                except ValueError as e: print(f"Error: {e}")
            elif opcion == '2':
                for t in self.svc_tipos_cotizacion.listar(): print(t)
            elif opcion == '3':
                try:
                    t = self.svc_tipos_cotizacion.buscar_por_id(int(input("ID a buscar: ")))
                    print(t if t else "No encontrado.")
                except ValueError: print("Error de ID.")
            elif opcion == '4':
                try:
                    id_tipo = int(input("ID a actualizar: "))
                    if self.svc_tipos_cotizacion.buscar_por_id(id_tipo):
                        self.svc_tipos_cotizacion.actualizar(TipoCotizacion(id=id_tipo, nombre=input("Nuevo nombre: ")))
                        print("Actualizado.")
                    else: print("No encontrado.")
                except ValueError as e: print(f"Error: {e}")
            elif opcion == '5':
                try: print("Eliminado." if self.svc_tipos_cotizacion.eliminar(int(input("ID a eliminar: "))) else "No encontrado.")
                except ValueError: print("Error de ID.")
            elif opcion == '0': break

    # ==========================================
    # CRUD PRECIOS
    # ==========================================
    def menu_precios(self):
        while True:
            print("\n--- MENÚ PRECIOS ---")
            print("1. Crear Precio")
            print("2. Listar Precios")
            print("3. Eliminar Precio")
            print("0. Volver")
            opcion = input("Seleccione: ")
            
            if opcion == '1':
                try:
                    id_precio = int(input("ID del precio: "))
                    libro = self.svc_libros.buscar_por_id(int(input("ID del Libro: ")))
                    if not libro:
                        print("Libro no existe. Abortando.")
                        continue
                    moneda = self.svc_monedas.buscar_por_id(int(input("ID de la Moneda: ")))
                    if not moneda:
                        print("Moneda no existe. Abortando.")
                        continue
                    monto = float(input("Monto: "))
                    fecha_str = input("Fecha de vigencia (YYYY-MM-DD): ")
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    
                    self.svc_precios.crear(Precio(id=id_precio, libro=libro, moneda=moneda, monto=monto, fecha_vigencia=fecha))
                    print("Precio registrado.")
                except ValueError as e: print(f"Error de formato o validación: {e}")
            elif opcion == '2':
                for p in self.svc_precios.listar(): print(p)
            elif opcion == '3':
                try: print("Eliminado." if self.svc_precios.eliminar(int(input("ID del Precio a eliminar: "))) else "No encontrado.")
                except ValueError: print("Error de ID.")
            elif opcion == '0': break

    # ==========================================
    # CRUD COTIZACIÓN DÓLAR
    # ==========================================
    def menu_cotizaciones(self):
        while True:
            print("\n--- MENÚ COTIZACIÓN DÓLAR ---")
            print("1. Crear Cotización")
            print("2. Buscar Cotización por Tipo y Fecha")
            print("3. Listar Histórico por Tipo")
            print("4. Eliminar Cotización")
            print("0. Volver")
            opcion = input("Seleccione: ")
            
            if opcion == '1':
                try:
                    id_cot = int(input("ID de cotización: "))
                    tipo = self.svc_tipos_cotizacion.buscar_por_id(int(input("ID del Tipo de Cotización: ")))
                    if not tipo:
                        print("Tipo de cotización no existe. Abortando.")
                        continue
                    fecha_str = input("Fecha (YYYY-MM-DD): ")
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    compra = float(input("Valor Compra: "))
                    venta = float(input("Valor Venta: "))
                    
                    self.svc_cotizaciones.crear(CotizacionDolar(id=id_cot, tipo_cotizacion=tipo, fecha=fecha, valor_compra=compra, valor_venta=venta))
                    print("Cotización registrada.")
                except ValueError as e: print(f"Error de formato: {e}")
            elif opcion == '2':
                try:
                    tipo_id = int(input("ID del Tipo: "))
                    fecha = datetime.strptime(input("Fecha (YYYY-MM-DD): "), "%Y-%m-%d").date()
                    cot = self.svc_cotizaciones.buscar_por_tipo_y_fecha(tipo_id, fecha)
                    print(cot if cot else "No encontrada.")
                except ValueError: print("Error en ingreso de datos.")
            elif opcion == '3':
                try:
                    hist = self.svc_cotizaciones.listar_historico(int(input("ID del Tipo a consultar: ")))
                    if hist:
                        for h in hist: print(h)
                    else: print("Sin registros para ese tipo.")
                except ValueError: print("Error de ID.")
            elif opcion == '4':
                try:
                    tipo_id = int(input("ID del Tipo: "))
                    fecha = datetime.strptime(input("Fecha (YYYY-MM-DD): "), "%Y-%m-%d").date()
                    print("Eliminada." if self.svc_cotizaciones.eliminar(tipo_id, fecha) else "No encontrada.")
                except ValueError: print("Error en ingreso de datos.")
            elif opcion == '0': break