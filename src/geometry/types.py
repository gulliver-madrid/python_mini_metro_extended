import math
from typing import NewType


Degrees = NewType("Degrees", float)


def create_degrees(value: int | float) -> Degrees:
    if math.isnan(value):
        raise ValueError()
    return Degrees(value)


def radians_to_degrees(radians: float) -> Degrees:
    degrees = math.degrees(radians)
    if math.isnan(degrees):
        raise ValueError()
    return Degrees(degrees)
