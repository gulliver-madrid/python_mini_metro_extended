from dataclasses import dataclass, field

import pygame

from src.color import reduce_saturation
from src.engine.utils import update_metros_segment_idx
from src.entity.path import Path
from src.entity.segments import PathSegment, find_equal_segment
from src.entity.station import Station
from src.geometry.line import Line
from src.geometry.point import Point


@dataclass
class EditingIntermediateStations:
    path: Path
    segment: PathSegment
    temp_point: Point | None = field(default=None)

    def set_temporary_point(self, temp_point: Point) -> None:
        self.temp_point = temp_point

    def get_path_and_index_before_insertion(self) -> tuple[Path, int]:
        segment = self.segment
        path_segments = self.path.get_path_segments()

        path_segment = find_equal_segment(segment, path_segments)
        assert path_segment

        index = path_segments.index(path_segment)
        path = self.path
        return (path, index)

    def remove_station(self, station: Station) -> None:
        segment = self.segment
        path_segments = self.path.get_path_segments()

        path_segment = find_equal_segment(segment, path_segments)
        assert path_segment

        index = path_segments.index(path_segment)

        self.path.stations.remove(station)
        update_metros_segment_idx(self.path.metros, after_index=index, change=-1)

        self.path.update_segments()

    def draw(self, surface: pygame.surface.Surface) -> None:
        color = reduce_saturation(self.path.color)
        if self.temp_point:
            temp_line1 = Line(
                color=color,
                start=self.segment.start,
                end=self.temp_point,
                width=10,
            )
            temp_line1.draw(surface)
            temp_line2 = Line(
                color=color,
                start=self.temp_point,
                end=self.segment.end,
                width=10,
            )
            temp_line2.draw(surface)
