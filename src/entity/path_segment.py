from __future__ import annotations

import math

import pygame
from shortuuid import uuid  # type: ignore

from src.config import path_order_shift, path_width
from src.entity.segment import Segment
from src.entity.station import Station
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.utils import direction, distance
from src.type import Color


class PathSegment(Segment):
    def __init__(
        self,
        color: Color,
        start_station: Station,
        end_station: Station,
        path_order: int,
    ) -> None:
        super().__init__(color)
        self.id = f"PathSegment-{uuid()}"
        self.start_station = start_station
        self.end_station = end_station
        self.path_order = path_order

        start_point = start_station.position
        end_point = end_station.position
        direct = direction(start_point, end_point)
        buffer_vector = direct * path_order_shift
        buffer_vector = buffer_vector.rotate(90)

        self.segment_start = start_station.position + buffer_vector * self.path_order
        self.segment_end = end_station.position + buffer_vector * self.path_order
        self.line = Line(
            color=self.color,
            start=self.segment_start,
            end=self.segment_end,
            width=path_width,
        )
