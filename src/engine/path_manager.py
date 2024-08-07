from typing import Final, Sequence

from src.config import max_num_metros, max_num_paths
from src.entity import Metro, Passenger, Path, Station
from src.entity.segments import PathSegment, Segment
from src.geometry.point import Point
from src.graph.graph_algo import build_station_nodes_dict
from src.tools.setup_logging import configure_logger

from .editing_intermediate import EditingIntermediateStations
from .game_components import GameComponents
from .path_being_created import PathBeingCreatedOrExpanding
from .travel_plan_finder import TravelPlanFinder
from .utils import update_metros_segment_idx

logger = configure_logger(__name__)


class PathManager:
    __slots__ = (
        "_components",
        "max_num_paths",
        "max_num_metros",
        "_path_being_created",
        "editing_intermediate_stations",
        "_travel_plan_finder",
    )

    def __init__(
        self,
        components: GameComponents,
    ):
        self.max_num_paths: Final = max_num_paths
        self.max_num_metros: Final = max_num_metros
        self._components: Final = components
        self._path_being_created: PathBeingCreatedOrExpanding | None = None
        self.editing_intermediate_stations: EditingIntermediateStations | None = None
        self._travel_plan_finder = TravelPlanFinder(components)

    ######################
    ### public methods ###
    ######################

    def start_path_on_station(self, station: Station) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return

        color = self._components.path_color_manager.get_first_path_color_available()
        assert color
        path = Path(color)
        path.is_being_created = True
        path.selected = True
        assert not self.path_being_created
        self.path_being_created = PathBeingCreatedOrExpanding(self._components, path)
        self._components.path_color_manager.assign_color_to_path(color, path)
        self._components.paths.append(path)

        path.add_station(station)

    def start_expanding_path_on_station(self, station: Station, index: int) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return
        path = self.get_paths_with_station(station)[index]
        path.selected = True
        assert not self.path_being_created
        self.path_being_created = PathBeingCreatedOrExpanding(
            self._components, path, station
        )

    def remove_path(self, path: Path) -> None:
        self._components.ui.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers[:]:
                assert passenger.last_station
                metro.move_passenger(passenger, passenger.last_station)
            assert not metro.passengers
            self._components.metros.remove(metro)
        self._components.path_color_manager.release_color_for_path(path)
        self._components.paths.remove(path)
        self._components.ui.assign_paths_to_buttons(self._components.paths)
        self.find_travel_plan_for_passengers()

    def find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(
            self._components.stations, self._components.paths
        )
        for station in self._components.stations:
            for passenger in station.passengers:
                if _passenger_has_travel_plan_with_next_path(passenger):
                    continue
                self._travel_plan_finder.find_travel_plan_for_passenger(
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
        assert self.editing_intermediate_stations
        self.editing_intermediate_stations.path.selected = False
        self.editing_intermediate_stations = None

    def get_paths_with_station(self, station: Station) -> list[Path]:
        return [path for path in self._components.paths if station in path.stations]

    @property
    def path_being_created(self) -> PathBeingCreatedOrExpanding | None:
        return self._path_being_created

    @path_being_created.setter
    def path_being_created(self, value: PathBeingCreatedOrExpanding | None) -> None:
        self._path_being_created = value

    #######################
    ### private methods ###
    #######################

    def _insert_station(self, station: Station) -> None:
        assert self.editing_intermediate_stations
        # get the index before insertion
        path, index = (
            self.editing_intermediate_stations.get_path_and_index_before_insertion()
        )
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
