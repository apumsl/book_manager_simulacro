"""Conexión a la base de datos y manejo de transacciones con SQLAlchemy."""
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


class ConexionDB:
    """Maneja la conexión a la base de datos con SQLAlchemy.

    Args:
        url (str): URL de conexión, por ejemplo 'sqlite:///archivo.db'.
        echo (bool): Si es True, muestra en consola el SQL generado.
    """

    def __init__(self, url: str, echo: bool = False) -> None:
        self.__engine: Engine = create_engine(url, echo=echo)
        self.__fabrica_sesiones: sessionmaker = sessionmaker(
            bind=self.__engine, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        """Engine de SQLAlchemy asociado a esta conexión."""
        return self.__engine

    def probar_conexion(self) -> bool:
        """Prueba la conexión ejecutando una consulta simple.

        Returns:
            bool: True si la conexión funciona, False si falla.
        """
        try:
            with self.__engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            return True
        except SQLAlchemyError:
            return False

    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        """Context manager que abre una sesión y maneja la transacción.

        Si el bloque termina sin errores hace commit; si ocurre una
        excepción hace rollback y la vuelve a lanzar. Siempre cierra la
        sesión al final.

        Uso:
            with conexion.transaccion() as sesion:
                sesion.add(objeto)

        Yields:
            Session: La sesión de SQLAlchemy para usar dentro del bloque.
        """
        sesion: Session = self.__fabrica_sesiones()
        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()

    def cerrar(self) -> None:
        """Cierra las conexiones y libera los recursos del engine."""
        self.__engine.dispose()