import heapq
import json


# Tabla oficial de riesgos según la ficha técnica del proyecto:
# - deltas de basalto = +5
# - puente sobre lava = +4
# - túnel cubierto = +1
PESOS_RIESGO: dict[str, int] = {
    "deltas_basalto": 5,
    "puente_sobre_lava": 4,
    "tunel_cubierto": 1,
}


def calcular_peligro(riesgos: list[str]) -> int:
    """
    Suma el nivel de peligro de cada riesgo presente en la ruta.
    Si aparece un riesgo no listado explícitamente, asigna un valor moderado de 2.
    """
    total = 0
    for riesgo in riesgos:
        clave = riesgo.strip().lower()
        total += PESOS_RIESGO.get(clave, 2)
    return total


class AsistenteSeguridadHeap:
    """
    Montículo Mínimo (Min-Heap) implementado con el módulo estándar 'heapq'.

    Cada elemento almacenado es una tupla con el formato exacto:
        (nivel_peligro, nombre_ruta, distancia_bloques)

    Como Python compara tuplas de izquierda a derecha, el primer elemento ('nivel_peligro')
    determina la prioridad: el menor nivel de peligro siempre queda en la raíz (índice 0).
    Insertar y extraer el mínimo toman O(log n).
    """

    def __init__(self) -> None:
        self._heap: list[tuple[int, str, int]] = []

    def registrar_ruta(self, nombre_ruta: str, nivel_peligro: int, distancia_bloques: int) -> None:
        """Inserta una nueva ruta en el montículo manteniendo la propiedad de Min-Heap en O(log n)."""
        tupla_ruta = (nivel_peligro, nombre_ruta, distancia_bloques)
        heapq.heappush(self._heap, tupla_ruta)

    def extraer_ruta_mas_segura(self) -> tuple[int, str, int] | None:
        """
        Extrae y devuelve la ruta con MENOR nivel de peligro en O(log n).
        Retorna None si no hay rutas disponibles.
        """
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def ver_ruta_mas_segura(self) -> tuple[int, str, int] | None:
        """Consulta la ruta más segura en la raíz del montículo sin extraerla en O(1)."""
        if not self._heap:
            return None
        return self._heap[0]

    def cargar_desde_json(self, ruta_archivo: str) -> None:
        """Carga rutas desde un JSON, calcula su nivel de peligro y las inserta en el Min-Heap."""
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            rutas = json.load(archivo)

        for item in rutas:
            peligro = calcular_peligro(item.get("riesgos", []))
            self.registrar_ruta(
                nombre_ruta=item["nombre_ruta"],
                nivel_peligro=peligro,
                distancia_bloques=int(item["distancia_bloques"]),
            )