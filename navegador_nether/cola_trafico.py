from collections import deque


class ColaTraficoTunel:
    """
    Estructura de datos COLA / QUEUE con política FIFO (First In, First Out)
    implementada como clase propia usando collections.deque.

    Se utiliza para controlar el paso por túneles estrechos de un solo carril
    donde jugadores o vagonetas esperan su turno en estricto orden de llegada.

    Operaciones principales:
    - enqueue(): agrega al final de la cola -> O(1)
    - dequeue(): extrae del frente de la cola con popleft() -> O(1)
    - frente(): consulta quién está primero sin sacarlo -> O(1)
    """

    def __init__(self) -> None:
        # 'deque' (double-ended queue) permite inserciones y extracciones en ambos extremos en O(1).
        self._elementos: deque[str] = deque()

    def enqueue(self, solicitud: str) -> None:
        """Agrega una solicitud (jugador o vagoneta) al final de la cola."""
        self._elementos.append(solicitud)

    def dequeue(self) -> str | None:
        """
        Despacha y retira al primer elemento en la cola (orden FIFO).
        Retorna None si la cola está vacía.
        """
        if not self._elementos:
            return None
        return self._elementos.popleft()

    def frente(self) -> str | None:
        """Retorna el elemento que está al frente de la cola sin retirarlo."""
        if not self._elementos:
            return None
        return self._elementos[0]

    def esta_vacia(self) -> bool:
        """Indica si no hay solicitudes pendientes en la cola."""
        return len(self._elementos) == 0

    def obtener_todos(self) -> list[str]:
        """Devuelve una copia en lista del orden actual de la cola."""
        return list(self._elementos)