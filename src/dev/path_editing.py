from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Sequence

StationId = int
SimpleSegment = tuple[StationId, StationId]


@dataclass
class TravelStep:
    station: StationId
    is_forward: bool = True
    next: TravelStep | None = None


@dataclass
class SegmentWithDirection:
    stations: SimpleSegment
    is_forward: bool = field(default=True, kw_only=True)


def find_segments(
    line: Sequence[StationId], *, is_loop: bool = False
) -> list[SimpleSegment]:
    """
    It makes a best effort without validating if line content is coherent. By instance, a line with only 2 elements and looped is accepted.
    """
    segments = list(itertools.pairwise(line))
    if is_loop and len(line) >= 2:
        segments.append((line[-1], line[0]))
    return segments


def get_segments_with_direction(
    segments: Sequence[SimpleSegment], *, is_loop: bool = False, is_forward: bool = True
) -> list[SegmentWithDirection]:
    """
    Returns a list of segments with their directions. The segmens should be unique, the first segment is going to be traveled after the last one.
    """
    segments_with_direction: list[SegmentWithDirection] = []
    if is_forward:
        if is_loop:
            for segment in segments:
                segments_with_direction.append(SegmentWithDirection(segment))
        else:
            for segment in segments:
                segments_with_direction.append(SegmentWithDirection(segment))
            for segment in reversed(segments):
                s1, s2 = segment
                stations = s2, s1
                segments_with_direction.append(
                    SegmentWithDirection(stations, is_forward=False)
                )
    else:
        if is_loop:
            for segment in reversed(segments):
                s1, s2 = segment
                stations = s2, s1
                segments_with_direction.append(
                    SegmentWithDirection(stations, is_forward=False)
                )
        else:
            for segment in reversed(segments):
                s1, s2 = segment
                stations = s2, s1
                segments_with_direction.append(
                    SegmentWithDirection(stations, is_forward=False)
                )
            for segment in segments:
                segments_with_direction.append(SegmentWithDirection(segment))
    return segments_with_direction
