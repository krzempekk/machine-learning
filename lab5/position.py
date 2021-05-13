import math
import numpy as np

from enum import Enum


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def distance_from(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def get_adjacent(self, direction):
        return self + direction.value


def get_random_direction():
    directions = list(Direction)
    return list(Direction)[np.random.randint(len(directions))]


class Direction(Enum):
    UP = Position(0, -1)
    UP_RIGHT = Position(1, -1)
    RIGHT = Position(1, 0)
    DOWN_RIGHT = Position(1, 1)
    DOWN = Position(0, 1)
    DOWN_LEFT = Position(-1, 1)
    LEFT = Position(-1, 0)
    UP_LEFT = Position(-1, -1)

    def rotate(self, angle):
        directions = list(Direction)
        pos = directions.index(self)
        return directions[(pos + angle) % len(directions)]
