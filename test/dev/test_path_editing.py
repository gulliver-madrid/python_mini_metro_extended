import unittest
from typing import Sequence

from unittest_prettify.colorize import colorize  # type: ignore [import-untyped]

from src.dev.path_editing import SimpleSegment, StationId, find_segments

from .text_colors import BG_BLUE

Case = tuple[Sequence[StationId], Sequence[SimpleSegment]]
Cases = Sequence[Case]


@colorize(color=BG_BLUE)
class TestPathEditing(unittest.TestCase):

    def test_find_segments_without_loop(self) -> None:
        """Tests that find_segments() works properly in non-looped line"""
        cases: Cases = [
            ([], []),
            ([1], []),
            ([1, 2], [(1, 2)]),
            ([1, 2, 3, 4], [(1, 2), (2, 3), (3, 4)]),
        ]
        for case in cases:
            with self.subTest(case=case):
                line, expected = case
                self.assertEqual(find_segments(line), expected)

    def test_find_segments_with_loop(self) -> None:
        """Tests that find_segments() works properly in a looped line"""
        cases: Cases = [
            ([], []),
            ([1], []),
            ([1, 2], [(1, 2), (2, 1)]),
            ([1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1)]),
        ]
        for case in cases:
            with self.subTest(case=case):
                line, expected = case
                self.assertEqual(find_segments(line, is_loop=True), expected)


if __name__ == "__main__":
    unittest.main()
