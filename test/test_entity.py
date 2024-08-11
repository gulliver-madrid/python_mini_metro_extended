import unittest
from unittest.mock import Mock

from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.passengers_mediator import PassengersMediator


class TestEntity(unittest.TestCase):
    def test_holders_add_and_move(self) -> None:
        """Tests the methods `add_new_passenger` and `move_passenger` of Holder"""
        mock_mediator = Mock(spec=PassengersMediator)
        mock_mediator.any_holder_has.side_effect = [False]
        metro = Metro(mock_mediator)
        station = Station(
            shape=Mock(spec=Shape),
            position=Mock(spec=Point),
            passengers_mediator=mock_mediator,
        )
        passenger = Passenger(Mock(spec=Shape))
        station.add_new_passenger(passenger)
        station.move_passenger(passenger, station)
        self.assertEqual(len(metro.passengers), 0)
        self.assertEqual(len(station.passengers), 1)
        mock_mediator.on_passenger_exit.assert_called_once_with(station, passenger)


if __name__ == "__main__":
    unittest.main()
