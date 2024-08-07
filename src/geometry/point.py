from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from shortuuid import uuid

from src.geometry.types import Degrees

FloatOrInt = (int, float)


def create_point_id() -> str:
    return f"Point-{uuid()}"


@dataclass(frozen=True, slots=True)
class Point:
    left: float
    top: float
    id: str = field(
        init=False,
        default_factory=create_point_id,
        compare=False,
        repr=False,
    )

    def __add__(self, other: Point | float) -> Point:
        if isinstance(other, Point):
            return Point(self.left + other.left, self.top + other.top)
        else:
            assert isinstance(other, FloatOrInt)
            return Point(self.left + other, self.top + other)

    def __radd__(self, other: Point | float) -> Point:
        return self.__add__(other)

    def __sub__(self, other: Point | float) -> Point:
        if isinstance(other, Point):
            return Point(self.left - other.left, self.top - other.top)
        else:
            assert isinstance(other, FloatOrInt)
            return Point(self.left - other, self.top - other)

    def __rsub__(self, other: Point | float) -> Point:
        if isinstance(other, Point):
            return Point(other.left - self.left, other.top - self.top)
        else:
            assert isinstance(other, FloatOrInt)
            return Point(other - self.left, other - self.top)

    def __mul__(self, other: float) -> Point:
        assert isinstance(other, FloatOrInt)
        return Point(other * self.left, other * self.top)

    def __rmul__(self, other: float) -> Point:
        return self.__mul__(other)

    def __deepcopy__(self, memo: Any) -> "Point":
        return Point(self.left, self.top)

    def rotate(self, degrees: Degrees) -> Point:
        """Returns a point result of rotate this around the origin. Note: a point is also a vector from the origin."""
        radians = math.radians(degrees)
        sin = math.sin(radians)
        cos = math.cos(radians)
        x = self.left
        y = self.top
        try:
            new_left = round(x * cos - y * sin)
            new_top = round(x * sin + y * cos)
        except ValueError as err:
            raise RuntimeError(
                f"radians: {radians}, x: {x}, y: {y}, cos: {cos}, sen: {sin}"
            ) from err

        return Point(new_left, new_top)

    def to_tuple(self) -> tuple[float, float]:
        return (self.left, self.top)
