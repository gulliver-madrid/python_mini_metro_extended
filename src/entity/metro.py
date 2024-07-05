import pygame
from shortuuid import uuid  # type: ignore

from src.config import (
    metro_capacity,
    metro_color,
    metro_passengers_per_row,
    metro_size,
    metro_speed_per_ms,
)
from src.entity.holder import Holder
from src.entity.segment import Segment
from src.entity.station import Station
from src.geometry.rect import Rect


class Metro(Holder):
    def __init__(self) -> None:
        self.size = metro_size
        metro_shape = Rect(color=metro_color, width=2 * self.size, height=self.size)
        super().__init__(
            shape=metro_shape,
            capacity=metro_capacity,
            id=f"Metro-{uuid()}",
        )
        self.current_station: Station | None = None
        self.current_segment: Segment | None = None
        self.current_segment_idx = 0
        self.path_id = ""
        self.speed = metro_speed_per_ms
        self.is_forward = True
        self.passengers_per_row = metro_passengers_per_row
