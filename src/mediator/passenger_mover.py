from collections.abc import Sequence
from typing import Final

from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.mediator.impl import MediatorStatus, TravelPlans, have_same_shape_type
from src.mediator.path_finder import find_next_path_for_passenger_at_station


class PassengerMover:
    def __init__(
        self,
        paths: list[Path],
        passengers: list[Passenger],
        travel_plans: TravelPlans,
        status: MediatorStatus,
    ):
        self._paths: Final = paths
        self._passengers: Final = passengers
        self._travel_plans: Final = travel_plans
        self._status: Final = status

    # public methods

    def move_passengers(self, metro: Metro) -> None:
        station = metro.current_station
        assert station

        to_remove: list[Passenger] = []
        from_metro_to_station: list[Passenger] = []
        from_station_to_metro: list[Passenger] = []

        # queue
        for passenger in metro.passengers:
            if have_same_shape_type(station, passenger):
                to_remove.append(passenger)
            elif self._is_next_planned_station(station, passenger):
                from_metro_to_station.append(passenger)

        for passenger in station.passengers:
            if self._metro_is_in_next_passenger_path(passenger, metro):
                from_station_to_metro.append(passenger)

        # process
        self._remove_passengers_from_metro(to_remove, metro)
        self._transfer_passengers_from_metro_to_station(
            metro, station, from_metro_to_station
        )
        self._transfer_passengers_from_station_to_metro(
            metro, station, from_station_to_metro
        )

    # private methods

    def _is_next_planned_station(self, station: Station, passenger: Passenger) -> bool:
        travel_plan = self._travel_plans[passenger]
        return travel_plan.get_next_station() == station

    def _metro_is_in_next_passenger_path(
        self, passenger: Passenger, metro: Metro
    ) -> bool:
        travel_plan = self._travel_plans[passenger]
        next_path = travel_plan.next_path
        if not next_path:
            return False
        return next_path.id == metro.path_id

    def _remove_passengers_from_metro(
        self, to_remove: Sequence[Passenger], metro: Metro
    ) -> None:
        for passenger in to_remove:
            passenger.is_at_destination = True
            metro.remove_passenger(passenger)
            self._passengers.remove(passenger)
            del self._travel_plans[passenger]
            self._status.score += 1

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
        travel_plan = self._travel_plans[passenger]
        travel_plan.increment_next_station()
        find_next_path_for_passenger_at_station(self._paths, travel_plan, station)
