import random
from typing import Final, Iterable, Mapping, Sequence, TypeVar

from src.config import max_num_metros, max_num_paths
from src.engine.path_being_edited import PathBeingEdited
from src.entity import Metro, Passenger, Path, Station
from src.entity.path_segment import PathSegment
from src.entity.segment import Segment
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.ui import UI
from src.utils import hue_to_rgb

from .game_components import GameComponents
from .path_being_created import PathBeingCreated
from .path_finder import find_next_path_for_passenger_at_station


class PathManager:
    __slots__ = (
        "_components",
        "max_num_paths",
        "_path_colors",
        "_path_to_color",
        "max_num_metros",
        "_ui",
        "path_being_created",
        "path_being_edited",
    )

    def __init__(
        self,
        components: GameComponents,
        ui: UI,
    ):
        self.max_num_paths: Final = max_num_paths
        self._path_to_color: Final[dict[Path, Color]] = {}
        self._path_colors: Final = self._get_initial_path_colors()
        self.max_num_metros: Final = max_num_metros
        self._components: Final = components
        self._ui: Final = ui
        self.path_being_created: PathBeingCreated | None = None
        self.path_being_edited: PathBeingEdited | None = None

    ######################
    ### public methods ###
    ######################

    def start_path_on_station(self, station: Station) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return
        assigned_color = (0, 0, 0)
        for path_color, taken in self._path_colors.items():
            if taken:
                continue
            assigned_color = path_color
            self._path_colors[path_color] = True
            break
        path = Path(assigned_color)
        self._path_to_color[path] = assigned_color
        path.add_station(station)
        path.is_being_created = True
        self.path_being_created = PathBeingCreated(path)
        self._components.paths.append(path)

    def add_station_to_path(self, station: Station) -> None:
        assert self.path_being_created
        self.path_being_created.add_station_to_path(station)
        if self.path_being_created.path.is_looped:
            self._finish_path_creation()

    def end_path_on_station(self, station: Station) -> None:
        assert self.path_being_created
        path = self.path_being_created.path
        # current station de-dupe
        if self.path_being_created.can_end_with(station):
            self._finish_path_creation()
        # loop
        elif self.path_being_created.can_make_loop(station):
            path.set_loop()
            self._finish_path_creation()
        # non-loop
        elif path.stations[0] != station:
            path.add_station(station)
            self._finish_path_creation()
        else:
            self.abort_path_creation()

    def end_path_on_last_station(self) -> None:
        assert self.path_being_created
        last = self.path_being_created.path.stations[-1]
        self.end_path_on_station(last)

    def abort_path_creation(self) -> None:
        assert self.path_being_created
        self._release_color_for_path(self.path_being_created.path)
        self._components.paths.remove(self.path_being_created.path)
        self.path_being_created = None

    def remove_path(self, path: Path) -> None:
        self._ui.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers[:]:
                assert passenger.last_station
                metro.move_passenger(passenger, passenger.last_station)
            assert not metro.passengers
            self._components.metros.remove(metro)
        self._release_color_for_path(path)
        self._components.paths.remove(path)
        self._assign_paths_to_buttons()
        self.find_travel_plan_for_passengers()

    def find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(
            self._components.stations, self._components.paths
        )
        for station in self._components.stations:
            for passenger in station.passengers:
                if self._passenger_has_travel_plan(passenger):
                    continue
                self._find_travel_plan_for_passenger(
                    station_nodes_mapping, station, passenger
                )

    def set_temporary_point(self, position: Point) -> None:
        assert self.path_being_created
        self.path_being_created.path.set_temporary_point(position)

    def try_starting_path_edition(self, position: Point) -> None:
        assert not self.path_being_created
        segment: PathSegment | None = None
        for path in self._components.paths:
            segment = path.get_containing_path_segment(position)
            if segment:
                print("segment selected")
                break
        else:
            print("no segment selected")
            return
        assert segment
        assert path
        if _segment_has_metros(segment, path.metros):
            return
        self.path_being_edited = PathBeingEdited(path, segment)

    def touch(self, station: Station) -> None:
        assert self.path_being_edited
        if station in self.path_being_edited.path.stations:
            self._remove_station(station)
        elif _segment_has_metros(
            self.path_being_edited.segment, self.path_being_edited.path.metros
        ):
            raise NotImplementedError("Segment with metros still can't be edited")
        else:
            self._insert_station(station)

    #######################
    ### private methods ###
    #######################

    def _get_initial_path_colors(self) -> dict[Color, bool]:
        path_colors: Final[dict[Color, bool]] = {}
        for i in range(max_num_paths):
            color = hue_to_rgb(i / (max_num_paths + 1))
            path_colors[color] = False  # not taken
        return path_colors

    def _finish_path_creation(self) -> None:
        assert self.path_being_created
        self.path_being_created.path.is_being_created = False
        self.path_being_created.path.remove_temporary_point()
        if len(self._components.metros) < self.max_num_metros:
            metro = Metro(self._components.mediator)
            self.path_being_created.path.add_metro(metro)
            self._components.metros.append(metro)
        self.path_being_created = None
        self._assign_paths_to_buttons()

    def _assign_paths_to_buttons(self) -> None:
        self._ui.assign_paths_to_buttons(self._components.paths)

    def _release_color_for_path(self, path: Path) -> None:
        self._path_colors[path.color] = False
        del self._path_to_color[path]

    def _passenger_has_travel_plan(self, passenger: Passenger) -> bool:
        return (
            passenger.travel_plan is not None
            and passenger.travel_plan.next_path is not None
        )

    def _find_travel_plan_for_passenger(
        self,
        station_nodes_mapping: Mapping[Station, Node],
        station: Station,
        passenger: Passenger,
    ) -> None:
        possible_dst_stations = self._get_stations_for_shape_type(
            passenger.destination_shape.type
        )

        for possible_dst_station in possible_dst_stations:
            start = station_nodes_mapping[station]
            end = station_nodes_mapping[possible_dst_station]
            node_path = bfs(start, end)
            if len(node_path) == 0:
                continue
            if len(node_path) == 1:
                raise RuntimeError("Trying to eliminate from station")
            else:
                assert len(node_path) > 1
                node_path = skip_stations_on_same_path(node_path)
                passenger.travel_plan = TravelPlan(node_path[1:], passenger.num_id)
                self._find_next_path_for_passenger_at_station(passenger, station)
                break

        else:
            travel_plan = TravelPlan([], passenger.num_id)
            if travel_plan != passenger.travel_plan:
                passenger.travel_plan = travel_plan

    def _get_stations_for_shape_type(self, shape_type: ShapeType) -> list[Station]:
        stations = [
            station
            for station in self._components.stations
            if station.shape.type == shape_type
        ]
        random.shuffle(stations)
        return stations

    def _find_next_path_for_passenger_at_station(
        self, passenger: Passenger, station: Station
    ) -> None:
        assert passenger.travel_plan
        find_next_path_for_passenger_at_station(
            self._components.paths, passenger.travel_plan, station
        )

    def _insert_station(self, station: Station) -> None:
        assert self.path_being_edited
        segment = self.path_being_edited.segment
        path_segments = self.path_being_edited.path.get_path_segments()

        path_segment = _find_equal_segment(segment, path_segments)
        assert path_segment

        index = path_segments.index(path_segment)

        self.path_being_edited.path.stations.insert(index + 1, station)
        _update_metros_segment_idx(
            self.path_being_edited.path.metros, after_index=index, change=1
        )
        self.path_being_edited = None

    def _remove_station(self, station: Station) -> None:
        assert self.path_being_edited
        segment = self.path_being_edited.segment
        path_segments = self.path_being_edited.path.get_path_segments()

        path_segment = _find_equal_segment(segment, path_segments)
        assert path_segment

        index = path_segments.index(path_segment)

        self.path_being_edited.path.stations.remove(station)
        _update_metros_segment_idx(
            self.path_being_edited.path.metros, after_index=index, change=-1
        )

        self.path_being_edited.path.update_segments()
        self.path_being_edited = None


################################
### private module interface ###
################################


def _segment_has_metros(segment: Segment, metros: Sequence[Metro]) -> bool:
    return any(
        metro.current_segment == segment for metro in metros if metro.current_segment
    )


T = TypeVar("T", bound=Segment)


def _find_equal_segment(segment: T, segments: Iterable[T]) -> T | None:
    for s in segments:
        if segment == s:
            return s
    return None


def _update_metros_segment_idx(
    metros: Iterable[Metro], *, after_index: int, change: int
) -> None:
    for metro in metros:
        if metro.current_segment_idx > after_index:
            metro.current_segment_idx += change
