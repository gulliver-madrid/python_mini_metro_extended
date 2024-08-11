import unittest
from dataclasses import dataclass
from typing import Sequence

from unittest_prettify.colorize import colorize  # type: ignore [import-untyped]

from src.dev.path_editing import (
    SegmentWithDirection,
    SimpleSegment,
    get_segments_with_direction,
)

from .text_colors import BG_BLUE


@dataclass(frozen=True, kw_only=True)
class Case:
    description: str
    segments_with_direction: Sequence[SegmentWithDirection]
    expected: list[tuple[SimpleSegment, bool]]


Cases = Sequence[Case]

cases = [
    Case(
        description="forward_no_loop",
        segments_with_direction=get_segments_with_direction(
            [(1, 2), (2, 3)], is_loop=False
        ),
        expected=[
            ((1, 2), True),
            ((2, 3), True),
            ((3, 2), False),
            ((2, 1), False),
        ],
    ),
    Case(
        description="forward_loop",
        segments_with_direction=get_segments_with_direction(
            [(1, 2), (2, 3), (3, 1)], is_loop=True
        ),
        expected=[
            ((1, 2), True),
            ((2, 3), True),
            ((3, 1), True),
        ],
    ),
    Case(
        description="backwards_no_loop",
        segments_with_direction=get_segments_with_direction(
            [(1, 2), (2, 3)], is_loop=False, is_forward=False
        ),
        expected=[
            ((3, 2), False),
            ((2, 1), False),
            ((1, 2), True),
            ((2, 3), True),
        ],
    ),
    Case(
        description="backwards_loop",
        segments_with_direction=get_segments_with_direction(
            [(1, 2), (2, 3), (3, 1)], is_loop=True, is_forward=False
        ),
        expected=[
            ((1, 3), False),
            ((3, 2), False),
            ((2, 1), False),
        ],
    ),
]


@colorize(color=BG_BLUE)
class TestGetSegmentsWithDirection(unittest.TestCase):

    def test_get_segments_with_direction_case_forward_no_loop(self) -> None:
        """
        Tests that get_segments_with_direction() works properly.
        """
        for case in cases:
            segments_with_direction = case.segments_with_direction
            expected = case.expected
            with self.subTest(desc=case.description):
                with self.subTest(type="length"):
                    self.assertEqual(
                        len(segments_with_direction),
                        len(expected),
                        (segments_with_direction, expected),
                    )
                for i, (segment, (stations, is_forward)) in enumerate(
                    zip(segments_with_direction, expected)
                ):
                    with self.subTest(i=i):
                        self.assertEqual(
                            segment,
                            SegmentWithDirection(stations, is_forward=is_forward),
                        )


if __name__ == "__main__":
    unittest.main()
