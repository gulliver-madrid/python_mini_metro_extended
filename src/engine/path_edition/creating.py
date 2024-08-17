from typing_extensions import override

from src.config import Config, max_num_metros
from src.engine.game_components import GameComponents
from src.entity.metro import Metro
from src.entity.path import Path
from src.entity.station import Station

from .creating_or_expanding_base import CreatingOrExpandingPathBase


class CreatingPath(CreatingOrExpandingPathBase):
    """Creating"""

    __slots__ = ()

    def __init__(self, components: GameComponents, path: Path):
        super().__init__(components, path)
        assert not self.is_expanding
        assert self._from_end

    ######################
    ### public methods ###
    ######################

    @override
    def add_station_to_path(self, station: Station) -> None:
        assert self.is_active

        self._add_station_to_path(station)
        if self.path.is_looped:
            self._finish_path_creation()

    @override
    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        assert self.is_active
        path = self.path
        if station not in path.stations:
            self.abort_path_creation_or_expanding()
            return

        # the loop should have been detected in `add_station_to_path` method
        assert not self._can_make_loop(station)

        assert self._is_last_station(station)  # test
        if self._can_end_with(station):
            self._finish_path_creation()
        else:
            self.abort_path_creation_or_expanding()

    @override
    def abort_path_creation_or_expanding(self) -> None:
        assert self.is_active
        self._remove_path_from_network()
        self._stop_creating_or_expanding()

    #######################
    ### private methods ###
    #######################

    @override
    def _add_station_to_path(self, station: Station) -> None:
        self._add_station_to_path_from_end(station)

    def _can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def _can_add_metro(self) -> bool:
        return len(self._components.metros) < max_num_metros

    def _add_new_metro(self) -> None:
        metro = Metro(self._components.passengers_mediator)
        self.path.add_metro(metro)
        self._components.metros.append(metro)
        if Config.debug_path_and_metros:
            print(f"Added item to metros. Total metros: {len(self._components.metros)}")

    def _finish_path_creation(self) -> None:
        assert self.is_active
        self.path.is_being_created = False
        if self._can_add_metro():
            self._add_new_metro()
        self._stop_creating_or_expanding()
        self._components.ui.assign_paths_to_buttons(self._components.paths)

    def _remove_path_from_network(self) -> None:
        self._components.path_color_manager.release_color_for_path(self.path)
        self._components.paths.remove(self.path)
