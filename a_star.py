import time
from typing import List, Tuple, Optional
from position import Position, Cell, CellType


class AStarWeightedSolver:
    def __init__(self, weight: float = 1.5):
        self.weight = weight
        self.nodes_explored = 0

    def is_valid(self, x: int, y: int, size: int) -> bool:
        """Verifica si las coordenadas son válidas"""
        return 0 <= x < size and 0 <= y < size

    def is_unblocked(self, maze, x: int, y: int) -> bool:
        """Verifica si la celda no está bloqueada"""
        return maze.grid[y, x] != CellType.WALL.value

    def is_destination(self, x: int, y: int, dest: Position) -> bool:
        """Verifica si llegamos al destino"""
        return x == dest.x and y == dest.y

    def calculate_h_value(self, x: int, y: int, dest: Position) -> float:
        """Calcula la heurística Euclidiana"""
        return ((x - dest.x) ** 2 + (y - dest.y) ** 2) ** 0.5

    def trace_path(self, cell_details: List[List[Cell]], dest: Position) -> List[Position]:
        """Reconstruye el camino desde el destino hasta el inicio"""
        path = []
        row, col = dest.y, dest.x

        # Seguir los padres hasta llegar al inicio
        while not (cell_details[row][col].parent_x == col and
                   cell_details[row][col].parent_y == row):
            path.append(Position(col, row))
            temp_row = cell_details[row][col].parent_y
            temp_col = cell_details[row][col].parent_x
            row, col = temp_row, temp_col

        path.append(Position(col, row))  # Agregar el inicio
        path.reverse()  # Invertir para obtener el camino correcto
        return path

    def solve(self, maze) -> Tuple[Optional[List[Position]], dict]:
        """
        A* Search Algorithm que busca CUALQUIER salida (no sabe cuál es la real)
        """
        start_time = time.time()
        self.nodes_explored = 0

        src = maze.start
        all_exits = maze.get_all_exits()  # Busca cualquier salida

        # Si no hay salidas disponibles
        if not all_exits:
            return None, {
                'nodes_explored': 0,
                'time': time.time() - start_time,
                'error': 'No exits available'
            }

        # Validaciones iniciales
        if not self.is_valid(src.x, src.y, maze.size):
            return None, {'error': 'Source is invalid'}

        # Verificar si ya estamos en una salida
        if any(self.is_destination(src.x, src.y, exit_pos) for exit_pos in all_exits):
            return [src], {'nodes_explored': 0, 'time': time.time() - start_time}

        # Inicializar closed list
        closed_list = [[False for _ in range(maze.size)] for _ in range(maze.size)]

        # Inicializar cell details
        cell_details = [[Cell() for _ in range(maze.size)] for _ in range(maze.size)]

        # Inicializar nodo de inicio
        i, j = src.y, src.x
        cell_details[i][j].f = 0.0
        cell_details[i][j].g = 0.0
        cell_details[i][j].h = 0.0
        cell_details[i][j].parent_x = j
        cell_details[i][j].parent_y = i

        # Open list como set de tuplas (f, (x, y))
        open_list = set()
        open_list.add((0.0, (j, i)))

        while open_list:
            # Encontrar nodo con menor f
            p = min(open_list)
            open_list.remove(p)

            # Agregar a closed list
            i, j = p[1][1], p[1][0]  # y, x
            closed_list[i][j] = True
            self.nodes_explored += 1

            # Generar 8 sucesores (4 cardinales + 4 diagonales)
            directions = [
                (-1, 0, 1.0),  # Norte
                (1, 0, 1.0),  # Sur
                (0, 1, 1.0),  # Este
                (0, -1, 1.0),  # Oeste
                (-1, 1, 1.414),  # Noreste
                (-1, -1, 1.414),  # Noroeste
                (1, 1, 1.414),  # Sureste
                (1, -1, 1.414)  # Suroeste
            ]

            for di, dj, cost in directions:
                new_i, new_j = i + di, j + dj

                # Verificar si es válido
                if not self.is_valid(new_j, new_i, maze.size):
                    continue

                # Si es CUALQUIER salida (no sabemos cuál es la real)
                if any(self.is_destination(new_j, new_i, exit_pos) for exit_pos in all_exits):
                    cell_details[new_i][new_j].parent_x = j
                    cell_details[new_i][new_j].parent_y = i

                    path = self.trace_path(cell_details, Position(new_j, new_i))

                    return path, {
                        'nodes_explored': self.nodes_explored,
                        'time': time.time() - start_time,
                        'path_length': len(path),
                        'generation': maze.generation,
                        'target_exit': Position(new_j, new_i)  # Qué salida encontró
                    }

                # Si no está en closed list y no está bloqueado
                elif (not closed_list[new_i][new_j] and
                      self.is_unblocked(maze, new_j, new_i)):

                    g_new = cell_details[i][j].g + cost

                    # Heurística: distancia a la salida MÁS CERCANA
                    h_new = min(self.calculate_h_value(new_j, new_i, exit_pos)
                                for exit_pos in all_exits)

                    f_new = g_new + self.weight * h_new  # A* Weighted aquí

                    # Si no está en open list o encontramos mejor camino
                    if (cell_details[new_i][new_j].f == float('inf') or
                            cell_details[new_i][new_j].f > f_new):
                        open_list.add((f_new, (new_j, new_i)))

                        # Actualizar detalles de la celda
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_x = j
                        cell_details[new_i][new_j].parent_y = i

        # No se encontró ninguna salida
        return None, {
            'nodes_explored': self.nodes_explored,
            'time': time.time() - start_time,
            'generation': maze.generation
        }