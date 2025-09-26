from enum import Enum


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Cell:
    def __init__(self):
        self.parent_x = -1
        self.parent_y = -1
        self.f = float('inf')
        self.g = float('inf')
        self.h = float('inf')