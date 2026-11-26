from collections import deque
import json


class GrafoNether:
    """
    Representa la red de portales y túneles del Nether como un GRAFO NO DIRIGIDO
    implementado mediante un diccionario de listas de adyacencia:
        { "estacion_a": ["estacion_b", "estacion_c"], ... }

    Al ser no dirigido, si existe un túnel entre A y B, se puede recorrer en ambos sentidos.
    """

    def __init__(self, adyacencia: dict[str, list[str]] | None = None):
        # Diccionario principal donde cada llave es un portal/base y su valor es la lista de vecinos.
        self.adyacencia: dict[str, list[str]] = {}
        if adyacencia:
            for nodo, vecinos in adyacencia.items():
                self.agregar_nodo(nodo)
                for vecino in vecinos:
                    self.agregar_arista(nodo, vecino)

    @classmethod
    def desde_json(cls, ruta_archivo: str) -> "GrafoNether":
        """Carga la estructura de la red desde un archivo JSON y construye el grafo."""
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return cls(datos)

    def guardar_json(self, ruta_archivo: str) -> None:
        """Guarda el estado actual del grafo en un archivo JSON con formato legible."""
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(self.adyacencia, archivo, indent=2, ensure_ascii=False)

    def agregar_nodo(self, nodo: str) -> None:
        """Agrega una estación/portal al grafo si aún no existe."""
        if nodo not in self.adyacencia:
            self.adyacencia[nodo] = []

    def agregar_arista(self, origen: str, destino: str) -> None:
        """
        Conecta 'origen' y 'destino' de forma bidireccional (grafo no dirigido).
        Evita duplicados comprobando si el vecino ya está en la lista.
        """
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        if destino not in self.adyacencia[origen]:
            self.adyacencia[origen].append(destino)
        if origen not in self.adyacencia[destino]:
            self.adyacencia[destino].append(origen)

    def bfs_camino_mas_corto(self, inicio: str, fin: str) -> tuple[list[str] | None, int, dict[str, int]]:
        """
        Aplica BFS (Búsqueda en Anchura) CON NIVELES para hallar la ruta con menor
        cantidad de transbordos (túneles/saltos) entre 'inicio' y 'fin'.

        ¿Cómo funciona?
        - Explora el grafo por capas/niveles: primero vecinos a 1 salto, luego a 2 saltos, etc.
        - 'visitados' impide recorrer un mismo nodo dos veces y evita ciclos infinitos.
        - 'padres' guarda de qué estación llegamos a cada estación para reconstruir la ruta.
        - 'niveles' almacena cuántos transbordos toma llegar a cada nodo explorado.

        Complejidad temporal: O(V + E), donde V = estaciones y E = túneles.
        Retorna: (camino_ordenado, cantidad_tuneles, niveles_alcanzados)
        """
        if inicio not in self.adyacencia or fin not in self.adyacencia:
            return None, -1, {}

        # Caso base: ya estamos en la estación destino.
        if inicio == fin:
            return [inicio], 0, {inicio: 0}

        visitados: set[str] = {inicio}
        padres: dict[str, str | None] = {inicio: None}
        niveles: dict[str, int] = {inicio: 0}

        # deque se usa como cola FIFO: sacamos por la izquierda (popleft) y metemos por la derecha (append).
        cola: deque[tuple[str, int]] = deque([(inicio, 0)])

        while cola:
            actual, nivel_actual = cola.popleft()

            for vecino in self.adyacencia.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    padres[vecino] = actual
                    nuevo_nivel = nivel_actual + 1
                    niveles[vecino] = nuevo_nivel

                    # Al ser BFS (exploración por niveles), la primera vez que alcanzamos 'fin'
                    # garantizamos que lo hacemos con el mínimo número de saltos posible.
                    if vecino == fin:
                        camino: list[str] = []
                        actual_reconstruccion: str | None = fin

                        # Retrocedemos desde el destino hasta el origen usando el diccionario 'padres'.
                        while actual_reconstruccion is not None:
                            camino.append(actual_reconstruccion)
                            actual_reconstruccion = padres[actual_reconstruccion]

                        # Invertimos la lista para que quede de 'inicio' -> 'fin'.
                        camino.reverse()
                        cantidad_tuneles = len(camino) - 1
                        return camino, cantidad_tuneles, niveles

                    cola.append((vecino, nuevo_nivel))

        # Si la cola se vacía y no se encontró 'fin', no existe conexión entre ambos puntos.
        return None, -1, niveles

    def bfs_auditoria_conectividad(self, nucleo: str = "hub_central") -> dict[str, list[str]]:
        """
        Aplica un BFS COMPLETO partiendo desde 'nucleo' (por defecto 'hub_central').

        ¿Para qué sirve?
        - Recorre toda la componente conexa alcanzable desde el Hub principal.
        - Cualquier estación registrada en 'self.adyacencia' que NO quede en 'visitados'
          está AISLADA (sin camino desde el núcleo), por ejemplo tras apagarse un portal.

        Complejidad temporal: O(V + E).
        """
        if nucleo not in self.adyacencia:
            return {
                "conectados": [],
                "aislados": sorted(self.adyacencia.keys()),
            }

        visitados: set[str] = {nucleo}
        cola: deque[str] = deque([nucleo])

        while cola:
            actual = cola.popleft()
            for vecino in self.adyacencia.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        conectados = sorted(visitados)
        # Toda estación que no fue alcanzada por el BFS completo está desconectada del núcleo.
        aislados = sorted(nodo for nodo in self.adyacencia if nodo not in visitados)

        return {
            "conectados": conectados,
            "aislados": aislados,
        }