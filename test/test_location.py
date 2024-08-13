import unittest

from src.entity.segments.location import LocationService
from src.entity.segments.padding_segment import GroupOfThreeStations
from src.entity.segments.path_segment import StationPair
from src.entity.station import Station
from src.geometry.circle import Circle
from src.geometry.point import Point
from src.passengers_mediator import PassengersMediator


def get_circle() -> Circle:
    return Circle((0, 0, 0), 10)


class TestLocation(unittest.TestCase):
    def _create_stations(
        self, mediator: PassengersMediator
    ) -> tuple[Station, Station, Station]:
        station_1 = Station(get_circle(), Point(100, 100), mediator)
        station_2 = Station(get_circle(), Point(200, 50), mediator)
        station_3 = Station(get_circle(), Point(300, 100), mediator)
        return (station_1, station_2, station_3)

    def test_location(self) -> None:
        """No conflict with points between different segments (different segments share some points without conflict)"""
        for path_order in (0, 1, -1, 2, -2):
            with self.subTest(path_order=path_order):
                LocationService.clear()
                passenger_mediator = PassengersMediator()
                station_1, station_2, station_3 = self._create_stations(
                    passenger_mediator
                )

                first_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_1, station_2), path_order
                )
                second_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_2, station_3), path_order
                )
                group = GroupOfThreeStations(station_1, station_2, station_3)
                padding_edges = LocationService.get_padding_segment_edges(
                    group, path_order
                )

                self.assertEqual(first_path_segment_edges.end, padding_edges.start)
                self.assertEqual(second_path_segment_edges.start, padding_edges.end)

                first_path_segment_reversed_edges = (
                    LocationService.get_path_segment_edges(
                        StationPair(station_2, station_1), path_order
                    )
                )
                self.assertEqual(
                    first_path_segment_reversed_edges.start,
                    first_path_segment_edges.end,
                )
                self.assertEqual(
                    first_path_segment_reversed_edges.end,
                    first_path_segment_edges.start,
                )

    def test_location_reverse_id_2_stations(self) -> None:
        """Test that reversing order in stations does not affect. It can be removed when there is no logic comparing Station.num_index order"""
        for path_order in (0, 1, -1, 2, -2):
            with self.subTest(path_order=path_order):
                LocationService.clear()
                passenger_mediator = PassengersMediator()
                station_1, station_2, station_3 = self._create_stations(
                    passenger_mediator
                )

                # reverse the order
                station_1, station_2 = station_2, station_1

                first_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_1, station_2), path_order
                )
                second_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_2, station_3), path_order
                )
                group = GroupOfThreeStations(station_1, station_2, station_3)
                padding_edges = LocationService.get_padding_segment_edges(
                    group, path_order
                )
                self.assertEqual(first_path_segment_edges.end, padding_edges.start)
                self.assertEqual(second_path_segment_edges.start, padding_edges.end)

    def test_location_reverse_id_3_stations(self) -> None:
        """Another reversing option. Same that previous"""
        for path_order in (0, 1, -1, 2, -2):
            with self.subTest(path_order=path_order):
                LocationService.clear()
                passenger_mediator = PassengersMediator()
                station_1, station_2, station_3 = self._create_stations(
                    passenger_mediator
                )

                # reverse the order
                station_1, station_2, station_3 = station_3, station_2, station_1

                first_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_1, station_2), path_order
                )
                second_path_segment_edges = LocationService.get_path_segment_edges(
                    StationPair(station_2, station_3), path_order
                )
                group = GroupOfThreeStations(station_1, station_2, station_3)
                padding_edges = LocationService.get_padding_segment_edges(
                    group, path_order
                )
                self.assertEqual(first_path_segment_edges.end, padding_edges.start)
                self.assertEqual(second_path_segment_edges.start, padding_edges.end)

    def test_location_different(self) -> None:
        """Test there is no overlapping"""

        LocationService.clear()
        path_order_1 = 1
        path_order_2 = -1

        passenger_mediator = PassengersMediator()
        station_1, station_2, _ = self._create_stations(passenger_mediator)

        first_path_segment_edges = LocationService.get_path_segment_edges(
            StationPair(station_1, station_2), path_order_1
        )
        second_path_segment_edges = LocationService.get_path_segment_edges(
            StationPair(station_1, station_2), path_order_2
        )
        third_path_segment_edges = LocationService.get_path_segment_edges(
            StationPair(station_2, station_1), path_order_2
        )

        assert first_path_segment_edges.start != second_path_segment_edges.start
        assert first_path_segment_edges.end != second_path_segment_edges.end
        assert first_path_segment_edges.end != third_path_segment_edges.start
        assert first_path_segment_edges.end != third_path_segment_edges.end


if __name__ == "__main__":
    unittest.main()
