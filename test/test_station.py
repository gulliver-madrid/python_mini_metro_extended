import unittest

from src.entity.station import Station
from src.passengers_mediator import PassengersMediator
from src.utils import get_random_position, get_random_station_shape

from test.base_test import FixedRandomSeedTestCase


class TestStation(FixedRandomSeedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.position = get_random_position(width=100, height=100)
        self.shape = get_random_station_shape()
        self.passengers_mediator = PassengersMediator()

    def test_init(self) -> None:
        station = Station(self.shape, self.position, self.passengers_mediator)

        self.assertEqual(station.shape, self.shape)
        self.assertEqual(station.position, self.position)


if __name__ == "__main__":
    unittest.main()
