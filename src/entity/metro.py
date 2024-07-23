from src.config import (
    metro_capacity,
    metro_color,
    metro_passengers_per_row,
    metro_size,
    metro_speed_per_ms,
)
from src.geometry.rect import Rect

from .holder import Holder
from .ids import EntityId, create_new_metro_id
from .segment import Segment
from .station import Station


class Metro(Holder):
    __slots__ = (
        "current_station",
        "current_segment",
        "current_segment_idx",
        "path_id",
        "game_speed",
        "is_forward",
    )

    def __init__(self) -> None:
        self.size = metro_size
        metro_shape = Rect(color=metro_color, width=2 * self.size, height=self.size)
        super().__init__(
            shape=metro_shape,
            capacity=metro_capacity,
            id=create_new_metro_id(),
        )
        self.current_station: Station | None = None
        self.current_segment: Segment | None = None
        self.current_segment_idx = 0
        self.path_id: EntityId | None = None
        self.game_speed = metro_speed_per_ms
        self.is_forward = True
        self.passengers_per_row = metro_passengers_per_row
