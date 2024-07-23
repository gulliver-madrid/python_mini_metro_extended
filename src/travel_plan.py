from typing import Sequence

from src.entity import Path, Station
from src.graph.node import Node


class TravelPlan:
    __slots__ = (
        "next_path",
        "next_station",
        "node_path",
        "next_station_idx",
        "_passenger_num_id",
    )

    def __init__(self, node_path: Sequence[Node], passenger_num_id: int) -> None:
        self.next_path: Path | None = None
        self.next_station: Station | None = None
        self.node_path = node_path
        self.next_station_idx = 0
        self._passenger_num_id = passenger_num_id

    def get_next_station(self) -> Station | None:
        if len(self.node_path) > 0:
            next_node = self.node_path[self.next_station_idx]
            next_station = next_node.station
            self.next_station = next_station
            return next_station
        return None

    def increment_next_station(self) -> None:
        self.next_station_idx += 1

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, type(self)):
            return False
        return self.next_path == value.next_path

    def __repr__(self) -> str:
        return f"TravelPlan(passenger_num_id={self._passenger_num_id}, node_path=({self.node_path})"

    def __str__(self) -> str:
        return f"TravelPlan (passenger {self._passenger_num_id}) = get on {self.next_path}, then get off at {self.next_station}"
