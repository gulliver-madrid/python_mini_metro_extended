from __future__ import annotations

import weakref
from dataclasses import dataclass, field
from typing import ClassVar

from src.entity.segments.segment import Segment

counter = 0

DEBUG_REFERENCES = False


@dataclass
class TravelStep:
    _weak_references: ClassVar[weakref.WeakSet[TravelStep]] = weakref.WeakSet()

    current: Segment
    is_forward: bool = True
    next: TravelStep | None = None
    counter: int = field(init=False)  # just for hash

    def __post_init__(self) -> None:
        global counter
        self.counter = counter
        self._weak_references.add(self)
        counter += 1
        if DEBUG_REFERENCES:
            print(f"There are {len(self._weak_references)} TravelStep references")

    def __del__(self) -> None:
        if DEBUG_REFERENCES:
            print(
                f"Deleting TravelStep. There are {len(self._weak_references)} references"
            )

    def __hash__(self) -> int:
        return hash(self.counter)
