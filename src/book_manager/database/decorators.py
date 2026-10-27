"""Decorador que registra en la tabla de auditoría cada operación."""
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from book_manager.models.models import AuditoriaModel

F = TypeVar('F', bound=Callable[..., Any])


def _a_dict(objeto: Any) -> Any:
    """Convierte un objeto en una estructura legible para el detalle.

    Quita el prefijo que Python agrega a los atributos privados (por
    ejemplo, '_Libro__isbn' queda como 'isbn') y recorre los objetos
    anidados.
    """
    if hasattr(objeto, '__dict__'):
        return {clave.split('__')[-1]: _a_dict(valor)
                for clave, valor in vars(objeto).items()}
    if isinstance(objeto, list):
        return [_a_dict(item) for item in objeto]
    return objeto


def _leer_previo(repositorio: Any, args: tuple) -> Optional[Any]:
    """Busca la entidad que se va a eliminar para registrar sus datos."""
    try:
        if hasattr(repositorio, 'leer_por_id'):
            return repositorio.leer_por_id(args[0])
        if hasattr(repositorio, 'leer_por_libro'):
            return repositorio.leer_por_libro(args[0])
        if hasattr(repositorio, 'leer_por_tipo_y_fecha') and len(args) > 1:
            return repositorio.leer_por_tipo_y_fecha(args[0], args[1])
    except Exception:
        return None
    return None


def _detalles(resultado: Any, previo: Any, args: tuple,
              kwargs: dict) -> str:
    """Arma el texto de detalles con el resultado o los argumentos."""
    if hasattr(resultado, '__dict__'):
        return str(_a_dict(resultado))
    if previo is not None:
        return str(_a_dict(previo))
    return f'Args: {args} | Kwargs: {kwargs}'


def auditar(accion: str) -> Callable[[F], F]:
    """Registra en la tabla auditoria la acción, la fecha y los detalles.

    Se aplica a métodos de clases que tienen el atributo conexion. Si la
    acción es de eliminación, guarda los datos de la entidad antes de
    borrarla. Un error al auditar no interrumpe la operación principal.

    Args:
        accion: Nombre de la acción, por ejemplo 'CREAR_LIBRO'.
    """
    def decorador(funcion: F) -> F:
        @wraps(funcion)
        def envoltorio(self: Any, *args: Any, **kwargs: Any) -> Any:
            previo = None
            if accion.startswith('ELIMINAR') and args:
                previo = _leer_previo(self, args)
            resultado = funcion(self, *args, **kwargs)
            try:
                with self.conexion.transaccion() as sesion:
                    sesion.add(AuditoriaModel(
                        accion=accion,
                        detalles=_detalles(resultado, previo, args, kwargs)))
            except Exception as error:
                print(f'Error guardando auditoría: {error}')
            return resultado
        return cast(F, envoltorio)
    return decorador
