from typing import NewType

from shortuuid import uuid

from src.geometry.type import ShapeType

EntityId = NewType("EntityId", str)


def create_new_passenger_id() -> EntityId:
    return _create_new_entity_id_with_label("Passenger")


def create_new_path_id() -> EntityId:
    return _create_new_entity_id_with_label("Path")


def create_new_path_segment_id() -> EntityId:
    return _create_new_entity_id_with_label("PathSegment")


def create_new_padding_segment_id() -> EntityId:
    return _create_new_entity_id_with_label("PaddingSegment")


def create_new_metro_id() -> EntityId:
    return _create_new_entity_id_with_label("Metro")


def create_new_station_id(shape_type: ShapeType) -> EntityId:
    return EntityId(f"Station-{uuid()}-{shape_type}")


def _create_new_entity_id_with_label(label: str) -> EntityId:
    return EntityId(f"{label}-{uuid()}")
