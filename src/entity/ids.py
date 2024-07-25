from typing import NewType

from shortuuid import uuid

from src.geometry.type import ShapeType

EntityId = NewType("EntityId", str)
EntityNumId = NewType("EntityNumId", int)


def create_new_passenger_id() -> EntityId:
    return _create_new_entity_id(label="Passenger")


def create_new_path_id() -> EntityId:
    return _create_new_entity_id(label="Path")


def create_new_path_segment_id() -> EntityId:
    return _create_new_entity_id(label="PathSegment")


def create_new_padding_segment_id() -> EntityId:
    return _create_new_entity_id(label="PaddingSegment")


def create_new_metro_id() -> EntityId:
    return _create_new_entity_id(label="Metro")


def create_new_station_id(shape_type: ShapeType) -> EntityId:
    return EntityId(f"Station-{uuid()}-{shape_type}")


def _create_new_entity_id(*, label: str) -> EntityId:
    return EntityId(f"{label}-{uuid()}")
