import unittest
from unittest.mock import Mock

from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.station import Station
from src.exceptions import GameException
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.passengers_mediator import PassengersMediator


class TestMediators(unittest.TestCase):
    def test_raises_err_if_passenger_in_two_holders(self) -> None:
        passenger = Mock(spec=Passenger)
        mediator = PassengersMediator()
        station = Station(Mock(spec=Shape), Mock(spec=Point), mediator)
        station.add_new_passenger(passenger)
        metro = Metro(mediator)
        with self.assertRaises(GameException):
            metro.add_new_passenger(passenger)


if __name__ == "__main__":
    unittest.main()
