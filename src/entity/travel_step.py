from __future__ import annotations

from dataclasses import dataclass

from src.entity.segments.segment import Segment


@dataclass
class TravelStep:
    current: Segment
    is_forward: bool = True
    next: TravelStep | None = None
