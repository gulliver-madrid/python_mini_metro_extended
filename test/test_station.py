import os
import unittest

from src.entity.station import Station
from src.utils import get_random_position, get_random_station_shape


class TestStation(unittest.TestCase):
    def setUp(self) -> None:
        self.position = get_random_position(width=100, height=100)
        self.shape = get_random_station_shape()

    def test_init(self):
        station = Station(self.shape, self.position)

        self.assertEqual(station.shape, self.shape)
        self.assertEqual(station.position, self.position)


if __name__ == "__main__":
    unittest.main()
