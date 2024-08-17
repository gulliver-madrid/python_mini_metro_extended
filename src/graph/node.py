from __future__ import annotations

import weakref
from typing import ClassVar

from shortuuid import uuid

from src.entity.path import Path
from src.entity.station import Station

DEBUG_REFERENCES = False
COUNT_EVERY = 500

action_counter = 0


class Node:
    _weak_references: ClassVar[weakref.WeakSet[Node]] = weakref.WeakSet()

    def __init__(self, station: Station) -> None:
        global action_counter
        self.id = f"Node-{uuid()}"
        self.station = station
        self.neighbors: set[Node] = set()
        self.paths: set[Path] = set()
        self._weak_references.add(self)
        action_counter += 1
        if DEBUG_REFERENCES and action_counter % COUNT_EVERY == 0:
            print(
                f"Creating Node. There are {len(self._weak_references)} Node references"
            )

    def __del__(self) -> None:
        global action_counter
        action_counter += 1
        if DEBUG_REFERENCES and action_counter % COUNT_EVERY == 0:
            print(f"Deleting Node. There are {len(self._weak_references)} references")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.station == other.station

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Node-{repr(self.station)}"
