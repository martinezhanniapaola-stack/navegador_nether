import json


def quicksort_diccionarios(elementos: list[dict], clave: str) -> list[dict]:
    """
    Ordena una lista de diccionarios usando el algoritmo QUICKSORT según 'clave'.

    Sirve tanto para:
    - Ordenar 'waypoints' alfabéticamente por 'nombre'.
    - Ordenar 'rutas' de menor a mayor según 'distancia_bloques'.

    ¿Cómo funciona?
    1. Selecciona un elemento pivote.
    2. Divide en menores (< pivote), iguales (== pivote) y mayores (> pivote).
    3. Ordena recursivamente 'menores' y 'mayores' y concatena.

    Complejidad: O(n log n) en promedio, O(n^2) en el peor caso.
    """
    if len(elementos) <= 1:
        return elementos[:]

    pivote = elementos[len(elementos) // 2][clave]

    # Si 'clave' es texto (como 'nombre'), normalizamos a minúsculas para ordenar alfabéticamente sin fallos.
    if isinstance(pivote, str):
        pivote_cmp = pivote.strip().lower()
        menores = [e for e in elementos if str(e[clave]).strip().lower() < pivote_cmp]
        iguales = [e for e in elementos if str(e[clave]).strip().lower() == pivote_cmp]
        mayores = [e for e in elementos if str(e[clave]).strip().lower() > pivote_cmp]
    else:
        # Si 'clave' es numérica (como 'distancia_bloques'), ordena de menor a mayor.
        menores = [e for e in elementos if e[clave] < pivote]
        iguales = [e for e in elementos if e[clave] == pivote]
        mayores = [e for e in elementos if e[clave] > pivote]

    return (
        quicksort_diccionarios(menores, clave)
        + iguales
        + quicksort_diccionarios(mayores, clave)
    )


def busqueda_binaria_waypoint(waypoints_ordenados: list[dict], nombre_objetivo: str) -> dict | None:
    """
    Busca un waypoint por 'nombre' sobre una lista YA ORDENADA alfabéticamente.

    ¿Cómo funciona?
    - Compara el elemento del punto medio ('medio') con 'nombre_objetivo'.
    - Si coincide, lo devuelve.
    - Si el nombre buscado es mayor, descarta la mitad izquierda ('izquierda = medio + 1').
    - Si es menor, descarta la mitad derecha ('derecha = medio - 1').

    Complejidad temporal: O(log n).
    """
    izquierda = 0
    derecha = len(waypoints_ordenados) - 1
    objetivo = nombre_objetivo.strip().lower()

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        actual = waypoints_ordenados[medio]["nombre"].strip().lower()

        if actual == objetivo:
            return waypoints_ordenados[medio]
        elif actual < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return None


def calcular_equivalente_dimension(waypoint: dict) -> dict:
    """
    Calcula la coordenada equivalente entre Nether y Overworld:
    - 1 bloque en el Nether = 8 bloques en el Overworld.
      Por lo tanto, de Nether a Overworld: X * 8 y Z * 8.
      De Overworld a Nether: X / 8 y Z / 8.
    La altura Y se conserva como referencia vertical.
    """
    dimension = waypoint.get("dimension", "Nether").strip().lower()
    x = waypoint["x"]
    y = waypoint["y"]
    z = waypoint["z"]

    if dimension == "nether":
        return {
            "dimension_equivalente": "Overworld",
            "x": x * 8,
            "y": y,
            "z": z * 8,
        }

    return {
        "dimension_equivalente": "Nether",
        "x": round(x / 8, 2),
        "y": y,
        "z": round(z / 8, 2),
    }


def cargar_json_lista(ruta_archivo: str) -> list[dict]:
    """Lee un archivo JSON que contiene una lista de diccionarios."""
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)