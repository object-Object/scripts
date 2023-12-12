from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


def main():
    raw_input = Path("input.txt").read_text()
    answer = solve_part1(raw_input)
    print(answer)


def solve_part1(raw_input: str) -> int:
    grid = split_grid(raw_input)
    start = find_start(grid)

    head_1, head_2 = start.adjacent(grid)

    visited = dict[Point, int]()

    prev = start
    dist = 1

    while head_1 != start:
        visited[head_1] = dist
        head_1, prev = head_1.next(grid, prev), head_1
        dist += 1

    prev = start
    dist = 1

    while head_2 != start:
        old_dist = visited.get(head_2)
        if old_dist and dist > old_dist:
            break

        visited[head_2] = dist
        head_2, prev = head_2.next(grid, prev), head_2
        dist += 1

    return max(visited.values())


Grid = list[list[str]]


def split_grid(raw_input: str) -> Grid:
    return [list(row) for row in raw_input.splitlines()]


def find_start(grid: Grid) -> Point:
    for y, row in enumerate(grid):
        for x, pipe in enumerate(row):
            if pipe == "S":
                return Point(x, y)
    raise ValueError


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def pipe(self, grid: Grid):
        if not (0 <= self.y < len(grid)):
            raise ValueError(self)

        row = grid[self.y]
        if not (0 <= self.x < len(row)):
            raise ValueError(self)

        return row[self.x]

    def adjacent(self, grid: Grid):
        result = list[Point]()

        for outbound in Direction:
            other = self + outbound.value
            try:
                for inbound in Direction.of(other.pipe(grid)):
                    if other + inbound.value == self:
                        result.append(other)
                        break
            except ValueError:
                pass

        assert len(result) == 2, result
        return result[0], result[1]

    def next(self, grid: Grid, prev: Point):
        a, b = Direction.of(self.pipe(grid))
        if (result := self + a.value) != prev:
            return result
        return self + b.value

    def __add__(self, other: Point):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point):
        return Point(self.x - other.x, self.y - other.y)


class Direction(Enum):
    NORTH = Point(0, -1)
    SOUTH = Point(0, 1)
    WEST = Point(-1, 0)
    EAST = Point(1, 0)

    @classmethod
    def of(cls, pipe: str) -> tuple[Direction, Direction]:
        match pipe:
            case "|":
                return cls.NORTH, cls.SOUTH
            case "-":
                return cls.WEST, cls.EAST
            case "L":
                return cls.NORTH, cls.EAST
            case "J":
                return cls.NORTH, cls.WEST
            case "7":
                return cls.SOUTH, cls.WEST
            case "F":
                return cls.SOUTH, cls.EAST
            case _:
                raise ValueError(pipe)


if __name__ == "__main__":
    main()
