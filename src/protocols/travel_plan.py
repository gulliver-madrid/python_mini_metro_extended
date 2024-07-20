from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.entity.path import Path
    from src.entity.station import Station
    from src.graph.node import Node


class TravelPlanProtocol(Protocol):
    next_path: Path | None
    next_station: Station | None
    node_path: Sequence[Node]

    def get_next_station(self) -> "Station | None": ...

    def increment_next_station(self) -> None: ...
