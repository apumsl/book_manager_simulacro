""" Entidades de dominio de Book Manager."""

from datetime import date


class EntidadBase:
    """Clase base para todas las entidades del sistema.

    Garantiza un identificador único.
    """

    def __init__(self, id: int) -> None:
        self.__id: int = id

    @property
    def id(self) -> int:
        """Identificador único de la entidad (es solo lectura)."""
        return self.__id

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id={self.__id})'


class Genero (EntidadBase):
    """Categoría literaria a la que pertenece un libro.

    Ejemplos: novela, ensayo, infantil, técnico.
    """

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.__nombre: str = nombre

    @property
    def nombre(self) -> str:
        return self.__nombre

    # setter para validar que no este vacio
    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError('El nombre del genero no puede estar vacio')
        self.__nombre = valor

    def __str__(self) -> str:
        return f'Genero(id={self.id}, nombre={self.__nombre})'


class Editorial(EntidadBase):
    """Proveedor/ distibuidora que provee los libros a la librería"""

    def __init__(self, id: int, nombre: str, sede: str) -> None:
        super().__init__(id)
        self.__nombre: str = nombre
        self.__sede: str = sede

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError('El nombre de la editorial no puede estar vacio')
        self.__nombre = valor

    @property
    def sede(self) -> str:
        return self.__sede

    @sede.setter
    def sede(self, valor: str) -> None:
        self.__sede = valor

    def __str__(self) -> str:
        return (f'Editorial(id={self.id}, nombre={self.__nombre}, '
                f'sede={self.__sede})')


class Moneda(EntidadBase):
    """Moneda en la que se puede expresar un precio (ARS, USD, etc.)."""

    def __init__(self, id: int, codigo: str, nombre: str) -> None:
        super().__init__(id)
        self.__codigo: str = codigo
        self.__nombre: str = nombre

    @property
    def codigo(self) -> str:
        return self.__codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError('El código de la moneda no puede estar vacío')
        self.__codigo = valor

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError('El nombre de la moneda no puede estar vacío')
        self.__nombre = valor

    def __str__(self) -> str:
        return f'Moneda(id={self.id}, codigo={self.__codigo})'


class TipoCotizacion(EntidadBase):
    """Tipo de cotización del dolar (oficial, Blue, MEP, etc.)"""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.__nombre: str = nombre

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError(
                'El nombre del tipo de cotización no puede estar vacío')
        self.__nombre = valor

    def __str__(self) -> str:
        return f'TipoCotizacion(id={self.id}, nombre={self.__nombre})'

# defino las clases que utilizan las clase anteriores
# defino clase CotizacionDolar


class CotizacionDolar(EntidadBase):
    """Valor de cotizacion del dólar para un tipo y fecha determinados."""

    def __init__(self, id: int, tipo_cotizacion: TipoCotizacion,
                 fecha: date, valor_compra: float,
                 valor_venta: float) -> None:
        super().__init__(id)
        self.__tipo_cotizacion: TipoCotizacion = tipo_cotizacion
        self.__fecha: date = fecha
        self.__valor_compra: float = valor_compra
        self.__valor_venta: float = valor_venta

    @property
    def tipo_cotizacion(self) -> TipoCotizacion:
        return self.__tipo_cotizacion

    @property
    def fecha(self) -> date:
        return self.__fecha

    @property
    def valor_compra(self) -> float:
        return self.__valor_compra

    @valor_compra.setter
    def valor_compra(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError('El valor de la compra debe ser mayor a cero')
        self.__valor_compra = valor

    @property
    def valor_venta(self) -> float:
        return self.__valor_venta

    @valor_venta.setter
    def valor_venta(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError('El valor de venta debe ser mayor a cero')
        self.__valor_venta = valor

    def __str__(self) -> str:
        return (f'CotizacionDolar(id={self.id}, '
                f'tipo={self.__tipo_cotizacion.nombre}, '
                f'fecha={self.__fecha}, venta={self.__valor_venta})')

# defino clase  Libro


class Libro(EntidadBase):
    """Libro del catalogo de la librería, con su género y editorial asociada"""

    def __init__(self, id: int, isbn: str, titulo: str, autor: str,
                 genero: Genero, editorial: Editorial) -> None:
        super().__init__(id)
        self.__isbn: str = isbn
        self.__titulo: str = titulo
        self.__autor: str = autor
        self.__genero: Genero = genero
        self.__editorial: Editorial = editorial

    @property
    def isbn(self) -> str:
        return self.__isbn

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError('El título del libro no puede estar vacío')
        self.__titulo = valor

    @property
    def autor(self) -> str:
        return self.__autor

    @property
    def genero(self) -> Genero:
        return self.__genero

    @genero.setter
    def genero(self, valor: Genero) -> None:
        self.__genero = valor

    @property
    def editorial(self) -> Editorial:
        return self.__editorial

    @editorial.setter
    def editorial(self, valor: Editorial) -> None:
        self.__editorial = valor

    def __str__(self) -> str:
        return (f'Libro(id={self.id}, isbn={self.__isbn}, '
                f'titulo={self.__titulo}, '
                f'genero={self.__genero.nombre}, '
                f'editorial={self.__editorial.nombre})')


class Precio(EntidadBase):
    """Precio de un libro en una moneda, vigente desde una fecha."""

    def __init__(self, id: int, libro: Libro, moneda: Moneda,
                 monto: float, fecha_vigencia: date) -> None:
        super().__init__(id)
        self.__libro: Libro = libro
        self.__moneda: Moneda = moneda
        self.__monto: float = monto
        self.__fecha_vigencia: date = fecha_vigencia

    @property
    def libro(self) -> Libro:
        return self.__libro

    @property
    def moneda(self) -> Moneda:
        return self.__moneda

    @property
    def monto(self) -> float:
        return self.__monto

    @monto.setter
    def monto(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError('El monto debe ser mayor a cero')
        self.__monto = valor

    @property
    def fecha_vigencia(self) -> date:
        return self.__fecha_vigencia

    def __str__(self) -> str:
        return (f'Precio(id={self.id}, libro={self.__libro.titulo}, '
                f'monto={self.__monto} {self.__moneda.codigo})')


class Stock(EntidadBase):
    """Cantidad disponible en el stock de un libro determinado"""

    def __init__(self, id: int, libro: Libro, cantidad: int) -> None:
        super().__init__(id)
        self.__libro: Libro = libro
        self.__cantidad: int = cantidad

    @property
    def libro(self) -> Libro:
        return self.__libro

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if valor < 0:
            raise ValueError('La cantidad no puede ser negativa')
        self.__cantidad = valor

    def __str__(self) -> str:
        return (f'Stock(id={self.id}, libro={self.__libro.titulo}, '
                f'cantidad={self.__cantidad})')
