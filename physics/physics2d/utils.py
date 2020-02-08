from .vector import Vector2
from .constants import EPSILON


def equal(a: float, b: float) -> bool:
    return abs(a - b) <= EPSILON


def clamp(t: float, min_: float, max_: float) -> float:
    if (t < min_):
        return min_
    if (t > max_):
        return max_
    return t


def random(l: float, h: float) -> float:
    from random import random as rand
    a = rand()
    a = (h - l) * a + l
    return a


def bias_greater_than(a: float, b: float) -> bool:
    k_biasRelative = 0.95
    k_biasAbsolute = 0.01
    return a >= b * k_biasRelative + a * k_biasAbsolute


def Cross(t: float, v: Vector2) -> Vector2:
    return Vector2(-t * v.y, t * v.x)
