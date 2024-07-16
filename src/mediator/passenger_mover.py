from __future__ import annotations

from collections.abc import Sequence
from typing import List

from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.mediator.impl import MediatorStatus, TravelPlans, have_same_shape_type
from src.mediator.path_finder import find_next_path_for_passenger_at_station


class PassengerMover:
    def __init__(
        self,
        paths: List[Path],
        passengers: List[Passenger],
        travel_plans: TravelPlans,
        status: MediatorStatus,
    ):
        self._paths = paths
        self._passengers = passengers
        self._travel_plans = travel_plans
        self._status = status

    def move_passengers(self, metro: Metro) -> None:
        current_station = metro.current_station
        assert current_station

        to_remove: List[Passenger] = []
        from_metro_to_station: List[Passenger] = []
        from_station_to_metro: List[Passenger] = []

        # queue
        for passenger in metro.passengers:
            if have_same_shape_type(current_station, passenger):
                to_remove.append(passenger)
            elif self._is_next_planned_station(current_station, passenger):
                from_metro_to_station.append(passenger)

        for passenger in current_station.passengers:
            if self._metro_is_in_next_passenger_path(passenger, metro):
                from_station_to_metro.append(passenger)

        # process
        self._remove_passengers(to_remove, metro)

        self._transfer_passengers_between_metro_and_station(
            metro,
            current_station,
            from_metro_to_station=from_metro_to_station,
            from_station_to_metro=from_station_to_metro,
        )

    def _is_next_planned_station(self, station: Station, passenger: Passenger) -> bool:
        return self._travel_plans[passenger].get_next_station() == station

    def _metro_is_in_next_passenger_path(
        self, passenger: Passenger, metro: Metro
    ) -> bool:
        next_path = self._travel_plans[passenger].next_path
        return (next_path is not None) and (next_path.id == metro.path_id)

    def _remove_passengers(self, to_remove: Sequence[Passenger], metro: Metro) -> None:
        for passenger in to_remove:
            passenger.is_at_destination = True
            metro.remove_passenger(passenger)
            self._passengers.remove(passenger)
            del self._travel_plans[passenger]
            self._status.score += 1

    def _transfer_passengers_between_metro_and_station(
        self,
        metro: Metro,
        station: Station,
        *,
        from_metro_to_station: Sequence[Passenger],
        from_station_to_metro: Sequence[Passenger],
    ) -> None:
        for passenger in from_metro_to_station:
            if station.has_room():
                self._move_passenger_to_current_station(passenger, metro)

        for passenger in from_station_to_metro:
            if metro.has_room():
                station.move_passenger(passenger, metro)

    def _move_passenger_to_current_station(
        self, passenger: Passenger, metro: Metro
    ) -> None:
        current_station = metro.current_station
        assert current_station
        metro.move_passenger(passenger, current_station)
        travel_plan = self._travel_plans[passenger]
        travel_plan.increment_next_station()
        find_next_path_for_passenger_at_station(
            self._paths, travel_plan, current_station
        )
