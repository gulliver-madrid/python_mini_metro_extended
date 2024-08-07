from typing import Iterable

from src.entity.metro import Metro


def update_metros_segment_idx(
    metros: Iterable[Metro], *, after_index: int, change: int
) -> None:
    for metro in metros:
        if metro.current_segment_idx > after_index:
            metro.current_segment_idx += change
