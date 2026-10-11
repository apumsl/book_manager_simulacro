"""Lectura y escritura de archivos CSV."""
import csv
from pathlib import Path
from typing import Dict, List


def leer_csv(ruta: Path) -> List[Dict[str, str]]:
    """Lee un archivo CSV y devuelve una lista de diccionarios.

    Args:
        ruta: Ruta del archivo CSV.

    Returns:
        Una fila por diccionario, con los valores como texto. Si el
        archivo no existe, devuelve una lista vacía.
    """
    if not ruta.exists():
        return []
    with open(ruta, newline='', encoding='utf-8') as archivo:
        return list(csv.DictReader(archivo))


def escribir_csv(ruta: Path, campos: List[str],
                 filas: List[Dict[str, object]]) -> None:
    """Escribe un archivo CSV completo, reemplazando el anterior.

    Args:
        ruta: Ruta del archivo CSV. Si la carpeta no existe, se crea.
        campos: Nombres de las columnas, en orden.
        filas: Una fila por diccionario.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)
