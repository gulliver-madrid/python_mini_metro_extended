import random
from typing import Final, Mapping, Sequence

from src.config import max_num_metros, max_num_paths
from src.entity import Metro, Passenger, Path, Station
from src.entity.segments import PathSegment, Segment
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.tools.setup_logging import configure_logger
from src.travel_plan import TravelPlan
from src.ui.ui import UI

from .editing_intermediate import EditingIntermediateStations
from .game_components import GameComponents
from .path_being_created import PathBeingCreatedOrExpanding
from .path_color_manager import PathColorManager
from .path_finder import find_next_path_for_passenger_at_station
from .utils import update_metros_segment_idx

logger = configure_logger(__name__)


class PathManager:
    __slots__ = (
        "_components",
        "max_num_paths",
        "max_num_metros",
        "_ui",
        "_path_being_created",
        "editing_intermediate_stations",
        "_path_color_manager",
    )

    def __init__(
        self,
        components: GameComponents,
        ui: UI,
    ):
        self.max_num_paths: Final = max_num_paths
        self.max_num_metros: Final = max_num_metros
        self._components: Final = components
        self._ui: Final = ui
        self._path_being_created: PathBeingCreatedOrExpanding | None = None
        self.editing_intermediate_stations: EditingIntermediateStations | None = None
        self._path_color_manager: Final = PathColorManager()

    ######################
    ### public methods ###
    ######################

    def start_path_on_station(self, station: Station) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return

        color = self._path_color_manager.get_first_path_color_available()
        assert color
        path = Path(color)
        path.is_being_created = True
        path.selected = True
        assert not self.path_being_created
        self.path_being_created = PathBeingCreatedOrExpanding(path)
        self._path_color_manager.assign_color_to_path(color, path)
        self._components.paths.append(path)

        path.add_station(station)

    def start_expanding_path_on_station(self, station: Station, index: int) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return
        path = self.get_paths_with_station(station)[index]
        path.selected = True
        assert not self.path_being_created
        self.path_being_created = PathBeingCreatedOrExpanding(path, station)

    def add_station_to_path(self, station: Station) -> None:
        assert self.path_being_created
        if self.path_being_created.is_expanding:
            if station not in self.path_being_created.path.stations:
                should_insert = self.path_being_created.add_station_to_path(station)
                if should_insert:
                    self._insert_station(station, 0)
                assert self.path_being_created
                assert self.path_being_created.is_expanding
                self.path_being_created.path.remove_temporary_point()
                self._stop_creating_or_expanding()
                # TODO: allow adding more than one station when expanding
            return
        self.path_being_created.add_station_to_path(station)
        if self.path_being_created.path.is_looped:
            self._finish_path_creation()

    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        assert self.path_being_created
        path = self.path_being_created.path
        assert (
            station in path.stations
        ), "The logic should have been executed when the mouse moved into the station."
        if self.path_being_created.is_expanding:
            self._stop_creating_or_expanding()
            return

        # the loop should have been detected in `add_station_to_path` method
        assert not self.path_being_created.can_make_loop(station)

        assert self.path_being_created._is_last_station(
            station
        )  # TODO: fix private access  # test
        if self.path_being_created.can_end_with(station):
            self._finish_path_creation()
        else:
            self.abort_path_creation_or_expanding()

    def try_to_end_path_on_last_station(self) -> None:
        assert self.path_being_created
        last = self.path_being_created.path.stations[-1]
        self.try_to_end_path_on_station(last)

    def abort_path_creation_or_expanding(self) -> None:
        assert self.path_being_created
        if not self.path_being_created.is_expanding:
            self._path_color_manager.release_color_for_path(
                self.path_being_created.path
            )
            self._components.paths.remove(self.path_being_created.path)
        self._stop_creating_or_expanding()

    def remove_path(self, path: Path) -> None:
        self._ui.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers[:]:
                assert passenger.last_station
                metro.move_passenger(passenger, passenger.last_station)
            assert not metro.passengers
            self._components.metros.remove(metro)
        self._path_color_manager.release_color_for_path(path)
        self._components.paths.remove(path)
        self._assign_paths_to_buttons()
        self.find_travel_plan_for_passengers()

    def find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(
            self._components.stations, self._components.paths
        )
        for station in self._components.stations:
            for passenger in station.passengers:
                if _passenger_has_travel_plan_with_next_path(passenger):
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
        self.editing_intermediate_stations = EditingIntermediateStations(path, segment)
        path.selected = True

    def touch(self, station: Station) -> None:
        assert self.editing_intermediate_stations
        if station in self.editing_intermediate_stations.path.stations:
            self._remove_station(station)
        elif _segment_has_metros(
            self.editing_intermediate_stations.segment,
            self.editing_intermediate_stations.path.metros,
        ):
            raise NotImplementedError("Segment with metros still can't be edited")
        else:
            self._insert_station(station)

    def stop_edition(self) -> None:
        if self.editing_intermediate_stations:
            self.editing_intermediate_stations.path.selected = False
            self.editing_intermediate_stations = None
        else:
            assert self.path_being_created
            assert self.path_being_created.is_expanding
            pass

    def get_paths_with_station(self, station: Station) -> list[Path]:
        return [path for path in self._components.paths if station in path.stations]

    @property
    def path_being_created(self) -> PathBeingCreatedOrExpanding | None:
        return self._path_being_created

    @path_being_created.setter
    def path_being_created(self, value: PathBeingCreatedOrExpanding | None) -> None:
        self._path_being_created = value
        repr_value = (
            None
            if self.path_being_created is None
            else (
                "PathBeingCreated with path"
                + str(self.path_being_created.path)
                + " and id:"
                + str(id(self.path_being_created))
            )
        )
        logger.info(f"path_being_created: {repr_value}")

    #######################
    ### private methods ###
    #######################

    def _finish_path_creation(self) -> None:
        assert self.path_being_created
        self.path_being_created.path.is_being_created = False
        self.path_being_created.path.remove_temporary_point()
        if len(self._components.metros) < self.max_num_metros:
            metro = Metro(self._components.passengers_mediator)
            self.path_being_created.path.add_metro(metro)
            self._components.metros.append(metro)
        self._stop_creating_or_expanding()
        self._assign_paths_to_buttons()

    def _stop_creating_or_expanding(self) -> None:
        assert self.path_being_created
        self.path_being_created.path.selected = False
        self.path_being_created = None

    def _assign_paths_to_buttons(self) -> None:
        self._ui.assign_paths_to_buttons(self._components.paths)

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

            assert len(node_path) > 1, "The passenger should have already arrived"
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

    def _insert_station(self, station: Station, index: int | None = None) -> None:
        if index is None:
            assert self.editing_intermediate_stations
            # get index before insertion
            path, index = (
                self.editing_intermediate_stations.get_path_and_index_before_insertion()
            )
        else:
            assert self.path_being_created
            assert self.path_being_created.is_expanding
            path = self.path_being_created.path
            index = index - 1

        # we insert the station *after* that index
        path.stations.insert(index + 1, station)
        update_metros_segment_idx(path.metros, after_index=index, change=1)
        self.stop_edition()

    def _remove_station(self, station: Station) -> None:
        assert self.editing_intermediate_stations
        self.editing_intermediate_stations.remove_station(station)
        self.stop_edition()


################################
### private module interface ###
################################


def _segment_has_metros(segment: Segment, metros: Sequence[Metro]) -> bool:
    return any(
        metro.current_segment == segment for metro in metros if metro.current_segment
    )


def _passenger_has_travel_plan_with_next_path(passenger: Passenger) -> bool:
    return (
        passenger.travel_plan is not None
        and passenger.travel_plan.next_path is not None
    )
