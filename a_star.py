import heapq
import numpy as np
from maze_generator import  MazeGenerator
class AStar:
    def __init__(self):
        self.nodos_explorados = 0

    # Heuristica usa distancia Euclidanea
    def heuristica(self, pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    # Encuentra las casillas vacias en las que se puede mover el agente
    def get_vecinos(self, pos, laberinto):
        laberinto_copy = laberinto.get_laberinto()
        fila, columna = pos
        vecinos = []

        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        movimientos_diag = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Verifica que no se pase de los limites del laberínto y que no sea un muro (1)
        for x, y in movimientos:
            new_fila, new_columna = fila + x, columna + y
            if 0 <= new_fila < laberinto_copy.shape[0] and 0 <= new_columna < laberinto_copy.shape[1] and laberinto_copy[new_fila, new_columna] != 1:
                vecinos.append(((new_fila, new_columna), 1.0))

        for x, y in movimientos_diag:
            new_fila, new_columna = fila + x, columna + y
            if not (0 <= new_fila < laberinto_copy.shape[0] and 0 <= new_columna < laberinto_copy.shape[1] and laberinto_copy[new_fila, new_columna] != 1):
                continue

            if laberinto_copy[fila + x, columna] != 1 and laberinto_copy[fila, columna + y] != 1:
                vecinos.append(((new_fila, new_columna), 1.414))
        return vecinos

    # Reconstruye el camino desde el inicio hasta el final
    def reconstruir_camino(self, desde, actual):
        # Empezar con la posición final
        path = [actual]

        # Retrocedemos siguiendo los padres hasta llegar al inicio
        while actual in desde:
            actual = desde[actual]  # Ir al padre de la posición actual
            path.append(actual)  # Agregarlo al camino

        # El camino está al revés (destino->inicio), lo volteamos
        path.reverse()
        return path

    # Busca todas las salidas en la grilla
    def encontrar_salidas(self, laberinto):
        return laberinto.get_exits_pos()

    def encontrar_entrada(self, laberinto):
        return laberinto.get_agent_pos()

    # Resuelve el laberinto buscando la salida hasta encontrar la real
    def solve(self, laberinto: MazeGenerator):
        posicion_actual = self.encontrar_entrada(laberinto)
        salidas_visitadas = set()
        todos_los_caminos = []
        total_nodos = 0

        while True:
            # Encontrar salidas disponibles
            todas_las_salidas = self.encontrar_salidas(laberinto)
            salidas_disponibles = []
            for s in todas_las_salidas:
                if s not in salidas_visitadas:
                    salidas_disponibles.append(s)

            # A* hacia la salida más cercana
            self.nodos_explorados = 0
            # Cola de prioridad para nodos por explorar
            open_set = []
            # Insertar tupla (prioridad_f, posicion)
            heapq.heappush(open_set, (0, posicion_actual))
            desde = {}
            g = {posicion_actual: 0}

            # Heurística hacia salida más cercana
            # Calcula distancia mínima hacia cualquier salida disponible
            min_h = self.heuristica(posicion_actual, salidas_disponibles[0])
            for salida in salidas_disponibles:
                #print(f"salida = {salida}")
                distancia = self.heuristica(posicion_actual, salida)
                if distancia < min_h:
                    min_h = distancia

            # Costo total (g + h)
            f = {posicion_actual: min_h}
            # Posiciones ya exploradas
            visitado = set()

            camino_encontrado = None
            salida_encontrada = None

            while open_set:
                # Sacar el nodo con menor f
                f_actual, actual = heapq.heappop(open_set)

                # Si ya se exploró, se omite
                if actual in visitado:
                    continue

                # Marcar nodo como explorado
                visitado.add(actual)
                self.nodos_explorados += 1

                # Verifica si llegó a alguna salida
                if actual in salidas_disponibles:
                    camino_encontrado = self.reconstruir_camino(desde, actual)
                    salida_encontrada = actual
                    break


                for vecino, costo in self.get_vecinos(actual, laberinto):
                    if vecino in visitado:
                        continue

                    # g nuevo que suma el g actual (costo desde el inicio al actual) y
                    # el costo de moverse hacia el vecino
                    g_nuevo = g[actual] + costo

                    # Si hay un camino mejor a este vecino, actualizar la información y calcular el nuevo f
                    if vecino not in g or g_nuevo < g[vecino]:
                        desde[vecino] = actual
                        g[vecino] = g_nuevo
                        h_min = self.heuristica(vecino, salidas_disponibles[0])
                        for salida in salidas_disponibles:
                            dist = self.heuristica(vecino, salida)
                            if dist < h_min:
                                h_min = dist
                        h_score = h_min
                        f[vecino] = g_nuevo + 1.5 * h_score
                        heapq.heappush(open_set, (f[vecino], vecino))

            # Agregar este camino
            todos_los_caminos.append(camino_encontrado)
            total_nodos += self.nodos_explorados
            salidas_visitadas.add(salida_encontrada)

            # Verifica la salida si es real (4) o falsa (3)
            if salida_encontrada is not None:
                #print(f"salidas encontradas{salida_encontrada}")
                if laberinto.get_laberinto()[salida_encontrada[0], salida_encontrada[1]] == 4:
                    self.nodos_explorados = total_nodos
                    return todos_los_caminos, True
                else:
                    posicion_actual = salida_encontrada
                    laberinto.set_agent_pos(salida_encontrada)
            else:
                posicion_actual = salida_encontrada
                laberinto.set_agent_pos(salida_encontrada)