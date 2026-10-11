from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


class ConexionDB:
    """Maneja la conexión a la base de datos con SQLAlchemy.

    Args:
        url (str): URL de conexión, por ejemplo 'sqlite:///archivo.db'.
        echo (bool): Si es True, muestra en consola el SQL generado.
    """

    def __init__(self, url: str, echo: bool = False) -> None:
        self.__engine: Engine = create_engine(url, echo=echo)

    @property
    def engine(self) -> Engine:
        """Engine de SQLAlchemy asociado a esta conexión."""
        return self.__engine

    def probar_conexion(self) -> bool:
        """Prueba la conexión ejecutando una consulta simple.

        Returns:
            bool: True si la conexion funciona, False si falla
            """
        try:
            with self.__engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def cerrar(self) -> None:
        """Cierra las conexiones y Libera los recursos cerrando el engine"""
        self.__engine.dispose()
