import pytest

from .part1 import solve_part1

CLEAN_SQUARE_LOOP = """\
.....
.S-7.
.|.|.
.L-J.
....."""

MESSY_SQUARE_LOOP = """\
-L|F7
7S-7|
L|7||
-L-J|
L|-JF"""

CLEAN_COMPLEX_LOOP = """\
..F7.
.FJ|.
SJ.L7
|F--J
LJ..."""

MESSY_COMPLEX_LOOP = """\
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ"""


@pytest.mark.parametrize(
    ["raw_input", "want"],
    [
        [CLEAN_SQUARE_LOOP, 4],
        [MESSY_SQUARE_LOOP, 4],
        [CLEAN_COMPLEX_LOOP, 8],
        [MESSY_COMPLEX_LOOP, 8],
    ],
)
def test_solve_part1(raw_input: str, want: int):
    assert solve_part1(raw_input) == want
