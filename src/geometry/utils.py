import numpy as np

from src.geometry.point import Point


def distance(p1: Point, p2: Point) -> float:
    result: float = np.sqrt((p1.left - p2.left) ** 2 + (p1.top - p2.top) ** 2)
    return result


def direction(p1: Point, p2: Point) -> Point:
    diff = p2 - p1
    diff_magnitude = distance(p1, p2)
    return Point(diff.left / diff_magnitude, diff.top / diff_magnitude)
