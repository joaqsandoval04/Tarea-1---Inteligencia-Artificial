import random
import numpy as np
from typing import List
from position import Position, CellType


class MutantMaze:
    def __init__(self, size: int, wall_move_prob: float = 0.1, num_exits: int = 3):
        self.size = size
        self.wall_move_prob = wall_move_prob
        self.num_exits = num_exits
        self.grid = np.zeros((size, size), dtype=int)
        self.start = Position(0, 0)
        self.exits = []
        self.real_exit_pos = None
        self.movable_walls = set()
        self.generation = 0

        self._generate_maze()

    def _generate_maze(self):
        # Limpiar grid
        self.grid.fill(CellType.EMPTY.value)

        # Generar paredes aleatorias (30% del espacio)
        wall_count = int(self.size * self.size * 0.3)
        for _ in range(wall_count):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (x, y) != (self.start.x, self.start.y):
                self.grid[y, x] = CellType.WALL.value
                if random.random() < 0.5:
                    self.movable_walls.add(Position(x, y))

        # Colocar inicio
        self.grid[self.start.y, self.start.x] = CellType.START.value

        # Generar salidas aleatorias
        self.exits = []
        for _ in range(self.num_exits):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if self.grid[y, x] == CellType.EMPTY.value:
                    exit_pos = Position(x, y)
                    self.exits.append(exit_pos)
                    self.grid[y, x] = CellType.EXIT.value
                    break


        real_exit_idx = random.randint(0, len(self.exits) - 1)
        self.real_exit_pos = self.exits[real_exit_idx]

    def mutate_walls(self):

        if random.random() > self.wall_move_prob:
            return False

        changed = False
        walls_to_move = list(self.movable_walls.copy())
        random.shuffle(walls_to_move)

        num_to_move = max(1, int(len(walls_to_move) * 0.2))

        for i in range(min(num_to_move, len(walls_to_move))):
            old_wall = walls_to_move[i]
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            random.shuffle(directions)

            for dx, dy in directions:
                new_x = old_wall.x + dx
                new_y = old_wall.y + dy

                if not (0 <= new_x < self.size and 0 <= new_y < self.size):
                    continue

                new_pos = Position(new_x, new_y)

                if (self.grid[new_y, new_x] == CellType.EMPTY.value and
                        new_pos != self.start and new_pos not in self.exits):
                    self.grid[old_wall.y, old_wall.x] = CellType.EMPTY.value
                    self.grid[new_y, new_x] = CellType.WALL.value

                    self.movable_walls.remove(old_wall)
                    self.movable_walls.add(new_pos)
                    changed = True
                    break

        if changed:
            self.generation += 1

        return changed

    def get_real_exit(self) -> Position:
        return self.real_exit_pos

    def get_all_exits(self) -> List[Position]:
        return self.exits.copy()

    def is_real_exit(self, pos: Position) -> bool:
        return pos == self.real_exit_pos

    def is_valid_position(self, pos: Position) -> bool:
        return (0 <= pos.x < self.size and
                0 <= pos.y < self.size and
                self.grid[pos.y, pos.x] != CellType.WALL.value)

    def mark_exit_as_visited(self, pos: Position):
        if pos in self.exits:
            self.grid[pos.y, pos.x] = CellType.EMPTY.value

    def print_maze(self, agent_pos: Position = None):
        symbols = {
            CellType.EMPTY.value: '.',
            CellType.WALL.value: '#',
            CellType.START.value: 'S',
            CellType.EXIT.value: 'E'
        }

        print(f"\nLaberinto {self.size}x{self.size} (Generación {self.generation}):")
        print(f"Salida real: ({self.get_real_exit().x}, {self.get_real_exit().y})")
        if agent_pos:
            print(f"Agente en: ({agent_pos.x}, {agent_pos.y})")
        print("-" * (self.size * 2 + 1))

        for y in range(self.size):
            row = "|"
            for x in range(self.size):
                pos = Position(x, y)


                if agent_pos and pos == agent_pos:
                    row += "@ "  # @ para el agente
                else:
                    cell_type = self.grid[y, x]
                    symbol = symbols.get(cell_type, '?')

                    # Marcar paredes móviles
                    if pos in self.movable_walls:
                        symbol = symbol.upper() if symbol != '#' else '█'

                    row += symbol + " "
            print(row + "|")
        print("-" * (self.size * 2 + 1))