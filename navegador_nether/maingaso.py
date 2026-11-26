from busqueda_orden import (
    busqueda_binaria_waypoint,
    calcular_equivalente_dimension,
    cargar_json_lista,
    quicksort_diccionarios,
)
from cola_trafico import ColaTraficoTunel
from grafo_nether import GrafoNether
from heap_seguridad import AsistenteSeguridadHeap, calcular_peligro


def mostrar_menu() -> None:
    """Imprime en consola las opciones requeridas por la ficha técnica."""
    print("\n========================================================")
    print("   NAVEGADOR DEL NETHER Y RED DE PORTALES (IAD-2401)")
    print("========================================================")
    print("1. Buscar coordenada / Waypoint (QuickSort + Búsqueda Binaria)")
    print("2. Calcular ruta con menos transbordos (Grafo + BFS)")
    print("3. Auditar conectividad de la red (BFS Completo)")
    print("4. Consultar ruta más segura (Min-Heap)")
    print("5. Control de tráfico en túneles (Cola FIFO)")
    print("6. Ver ranking de rutas por distancia (QuickSort)")
    print("0. Salir")


def opcion_buscar_waypoint(waypoints: list[dict]) -> None:
    """
    Opción 1: Ordena los waypoints alfabéticamente con QuickSort, busca el solicitado
    con Búsqueda Binaria y muestra coordenadas en su dimensión y su equivalente (x8 / /8).
    """
    if not waypoints:
        print("El directorio de waypoints está vacío.")
        return

    waypoints_ordenados = quicksort_diccionarios(waypoints, clave="nombre")
    nombre = input("Ingresa el nombre del waypoint a buscar: ").strip()

    encontrado = busqueda_binaria_waypoint(waypoints_ordenados, nombre)
    if not encontrado:
        print(f"[!] No se encontró ningún waypoint llamado '{nombre}'.")
        return

    equiv = calcular_equivalente_dimension(encontrado)
    print(f"\n[OK] Waypoint encontrado: {encontrado['nombre']}")
    print(
        f"     Coordenadas ({encontrado['dimension']}): "
        f"X={encontrado['x']}, Y={encontrado['y']}, Z={encontrado['z']}"
    )
    print(
        f"     Equivalente ({equiv['dimension_equivalente']}): "
        f"X={equiv['x']}, Y={equiv['y']}, Z={equiv['z']}"
    )


def opcion_ruta_bfs(grafo: GrafoNether) -> None:
    """
    Opción 2: Calcula el camino con menor cantidad de transbordos usando BFS con niveles
    y muestra tanto la secuencia de estaciones como el número de túneles a atravesar.
    """
    origen = input("Estación/portal de ORIGEN: ").strip()
    destino = input("Estación/portal de DESTINO: ").strip()

    camino, tuneles, _ = grafo.bfs_camino_mas_corto(origen, destino)
    if camino is None:
        print(f"[!] No existe ruta conectada entre '{origen}' y '{destino}'.")
        return

    print(f"\n[OK] Ruta más corta encontrada ({tuneles} túnel(es) / transbordo(s)):")
    print("     " + " -> ".join(camino))


def opcion_auditoria_bfs(grafo: GrafoNether) -> None:
    """
    Opción 3: Ejecuta un BFS completo desde el núcleo (por defecto 'hub_central')
    para listar qué estaciones están conectadas y cuáles quedaron aisladas.
    """
    nucleo = input("Estación núcleo para auditar (Enter para 'hub_central'): ").strip()
    if not nucleo:
        nucleo = "hub_central"

    resultado = grafo.bfs_auditoria_conectividad(nucleo)
    conectados = resultado["conectados"]
    aislados = resultado["aislados"]

    print(f"\n--- Auditoría de conectividad desde '{nucleo}' ---")
    print(f"Estaciones CONECTADAS ({len(conectados)}):")
    print("  " + (", ".join(conectados) if conectados else "Ninguna"))

    print(f"\nEstaciones AISLADAS / DESCONECTADAS ({len(aislados)}):")
    print("  " + (", ".join(aislados) if aislados else "Ninguna"))


def opcion_min_heap(heap_seguridad: AsistenteSeguridadHeap) -> None:
    """
    Opción 4: Permite registrar nuevas rutas calculando su peligro, ver la ruta
    más segura en el tope o extraer la de menor peligro con heapq.heappop().
    """
    print("\n--- Asistente de Seguridad (Min-Heap) ---")
    print("a) Registrar nueva ruta")
    print("b) Extraer ruta más segura (menor nivel de peligro)")
    print("c) Consultar ruta más segura actual (sin extraer)")
    accion = input("Elige una acción (a/b/c): ").strip().lower()

    if accion == "a":
        nombre = input("Nombre de la ruta: ").strip()
        try:
            distancia = int(input("Distancia total en bloques: ").strip())
        except ValueError:
            print("[!] La distancia debe ser un número entero.")
            return

        print("Riesgos base: deltas_basalto (+5), puente_sobre_lava (+4), tunel_cubierto (+1)")
        raw_riesgos = input("Riesgos separados por coma: ").strip()
        riesgos = [r.strip() for r in raw_riesgos.split(",") if r.strip()]

        peligro_total = calcular_peligro(riesgos)
        heap_seguridad.registrar_ruta(nombre, peligro_total, distancia)
        print(
            f"[OK] Ruta '{nombre}' registrada | Peligro: {peligro_total} | Distancia: {distancia} bloques."
        )

    elif accion == "b":
        extraida = heap_seguridad.extraer_ruta_mas_segura()
        if extraida is None:
            print("[!] No hay rutas registradas en el montículo.")
            return
        peligro, nombre, distancia = extraida
        print(
            f"[OK] Ruta más segura EXTRAÍDA: '{nombre}' "
            f"(Nivel de peligro: {peligro}, Distancia: {distancia} bloques)"
        )

    elif accion == "c":
        tope = heap_seguridad.ver_ruta_mas_segura()
        if tope is None:
            print("[!] No hay rutas registradas en el montículo.")
            return
        peligro, nombre, distancia = tope
        print(
            f"[INFO] Ruta más segura en la raíz: '{nombre}' "
            f"(Nivel de peligro: {peligro}, Distancia: {distancia} bloques)"
        )

    else:
        print("[!] Acción no válida.")


def opcion_cola_trafico(cola: ColaTraficoTunel) -> None:
    """
    Opción 5: Simula el control FIFO de jugadores/vagonetas esperando para cruzar
    un túnel estrecho.
    """
    print("\n--- Control de Tráfico de Vagonetas (Cola FIFO) ---")
    print("a) Agregar solicitud a la cola (enqueue)")
    print("b) Ver quién está al frente (frente)")
    print("c) Despachar siguiente turno (dequeue)")
    print("d) Mostrar toda la cola")
    accion = input("Elige una acción (a/b/c/d): ").strip().lower()

    if accion == "a":
        solicitud = input("Nombre del jugador o vagoneta: ").strip()
        if not solicitud:
            print("[!] Debes ingresar un nombre válido.")
            return
        cola.enqueue(solicitud)
        print(f"[OK] '{solicitud}' entró al final de la cola.")

    elif accion == "b":
        primero = cola.frente()
        print(f"[INFO] Al frente de la cola: {primero}" if primero else "[INFO] La cola está vacía.")

    elif accion == "c":
        despachado = cola.dequeue()
        print(
            f"[OK] Despachado para cruzar el túnel: {despachado}"
            if despachado
            else "[INFO] No hay turnos pendientes para despachar."
        )

    elif accion == "d":
        elementos = cola.obtener_todos()
        if not elementos:
            print("[INFO] Cola vacía.")
        else:
            print("[INFO] Orden de espera (Frente -> Final): " + " -> ".join(elementos))

    else:
        print("[!] Acción no válida.")


def opcion_ranking_rutas(rutas: list[dict]) -> None:
    """
    Extra útil (Opción 6): Ordena las rutas descubiertas de menor a mayor distancia
    en bloques utilizando el mismo QuickSort modularizado.
    """
    if not rutas:
        print("[!] No hay rutas registradas en rutas_peligro.json.")
        return

    ordenadas = quicksort_diccionarios(rutas, clave="distancia_bloques")
    print("\n--- Ranking de Rutas (Menor a Mayor Distancia) ---")
    for i, ruta in enumerate(ordenadas, start=1):
        peligro = calcular_peligro(ruta.get("riesgos", []))
        print(
            f"{i}. {ruta['nombre_ruta']} -> {ruta['distancia_bloques']} bloques "
            f"(Peligro calculado: {peligro})"
        )


def main() -> None:
    """Punto de entrada del programa: carga los JSON e inicia el bucle interactivo."""
    grafo = GrafoNether.desde_json("red_nether.json")
    waypoints = cargar_json_lista("waypoints.json")
    rutas_json = cargar_json_lista("rutas_peligro.json")

    heap_seguridad = AsistenteSeguridadHeap()
    heap_seguridad.cargar_desde_json("rutas_peligro.json")

    cola_trafico = ColaTraficoTunel()

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            opcion_buscar_waypoint(waypoints)
        elif opcion == "2":
            opcion_ruta_bfs(grafo)
        elif opcion == "3":
            opcion_auditoria_bfs(grafo)
        elif opcion == "4":
            opcion_min_heap(heap_seguridad)
        elif opcion == "5":
            opcion_cola_trafico(cola_trafico)
        elif opcion == "6":
            opcion_ranking_rutas(rutas_json)
        elif opcion == "0":
            print("Saliendo del sistema. ¡Buen viaje por el Nether!")
            break
        else:
            print("[!] Opción no válida. Intenta nuevamente.")


if __name__ == "__main__":
    main()