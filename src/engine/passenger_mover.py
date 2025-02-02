from collections.abc import Sequence
from typing import Final

from src.entity import Metro, Passenger, Station

from .game_components import GameComponents
from .path_finder import find_next_path_for_passenger_at_station


class PassengerMover:
    __slots__ = ("_components",)

    def __init__(self, components: GameComponents):
        self._components: Final = components

    # public methods

    def move_passengers(self, metro: Metro) -> None:
        station = metro.current_station
        assert station

        to_arrive: list[Passenger] = []
        from_metro_to_station: list[Passenger] = []
        from_station_to_metro: list[Passenger] = []

        # queue
        for passenger in metro.passengers:
            if have_same_shape_type(station, passenger):
                to_arrive.append(passenger)
            elif self._is_next_planned_station(station, passenger):
                from_metro_to_station.append(passenger)

        for passenger in station.passengers:
            if self._metro_is_in_passenger_next_path(passenger, metro):
                from_station_to_metro.append(passenger)

        # process
        self._make_passengers_arrive(to_arrive, metro)
        self._transfer_passengers_from_metro_to_station(
            metro, station, from_metro_to_station
        )
        self._transfer_passengers_from_station_to_metro(
            metro, station, from_station_to_metro
        )

    # private methods

    def _is_next_planned_station(self, station: Station, passenger: Passenger) -> bool:
        travel_plan = passenger.travel_plan
        assert travel_plan
        return travel_plan.get_next_station() == station

    def _metro_is_in_passenger_next_path(
        self, passenger: Passenger, metro: Metro
    ) -> bool:
        travel_plan = passenger.travel_plan
        assert travel_plan
        next_path = travel_plan.next_path
        if not next_path:
            return False
        return next_path.id == metro.path_id

    def _make_passengers_arrive(
        self, to_arrive: Sequence[Passenger], metro: Metro
    ) -> None:
        for passenger in to_arrive:
            passenger.is_at_destination = True
            metro.passenger_arrives(passenger)
            passenger.travel_plan = None
            self._components.status.score += 1

    def _transfer_passengers_from_metro_to_station(
        self,
        metro: Metro,
        station: Station,
        from_metro_to_station: Sequence[Passenger],
    ) -> None:
        for passenger in from_metro_to_station:
            if station.has_room():
                self._move_passenger_to_station(passenger, metro, station)

    def _transfer_passengers_from_station_to_metro(
        self,
        metro: Metro,
        station: Station,
        from_station_to_metro: Sequence[Passenger],
    ) -> None:
        for passenger in from_station_to_metro:
            if metro.has_room():
                station.move_passenger(passenger, metro)

    def _move_passenger_to_station(
        self,
        passenger: Passenger,
        metro: Metro,
        station: Station,
    ) -> None:
        metro.move_passenger(passenger, station)
        travel_plan = passenger.travel_plan
        assert travel_plan
        travel_plan.increment_next_station()
        find_next_path_for_passenger_at_station(
            self._components.paths, travel_plan, station
        )


def have_same_shape_type(station: Station, passenger: Passenger) -> bool:
    return station.shape.type == passenger.destination_shape.type
