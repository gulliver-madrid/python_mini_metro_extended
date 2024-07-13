from typing import NewType

from shortuuid import uuid

from src.geometry.type import ShapeType

EntityId = NewType("EntityId", str)


def create_new_passenger_id() -> EntityId:
    return EntityId(f"Passenger-{uuid()}")


def create_new_path_id() -> EntityId:
    return EntityId(f"Path-{uuid()}")


def create_new_path_segment_id() -> EntityId:
    return EntityId(f"PathSegment-{uuid()}")


def create_new_padding_segment_id() -> EntityId:
    return EntityId(f"PaddingSegment-{uuid()}")


def create_new_station_id(shape_type: ShapeType) -> EntityId:
    return EntityId(f"Station-{uuid()}-{shape_type}")


def create_new_metro_id() -> EntityId:
    return EntityId(f"Metro-{uuid()}")
