import math

from typing import Union
from .vector import Vector2


class Mat2:
    def __init__(self, a: float = 0.0, b: float = 0.0, c: float = 0.0, d: float = 0.0):
        self.m00, self.m01, self.m10, self.m11 = (
            a, b, c, d
        )

    @classmethod
    def from_angle(cls, radians: float) -> "Mat2":
        c = math.cos(radians)
        s = math.sin(radians)
        return Mat2(c, -s, s, c)

    def __abs__(self) -> "Mat2":
        return Mat2(
            abs(self.m00), abs(self.m01), abs(self.m10), abs(self.m11)
        )

    def axis_x(self) -> Vector2:
        return Vector2(self.m00, self.m10)

    def axis_y(self) -> Vector2:
        return Vector2(self.m01, self.m11)

    def transpose(self) -> "Mat2":
        return Mat2(self.m00, self.m10, self.m01, self.m11)

    def __mul__(self, other: Union[Vector2, "Mat2"]) -> Union[Vector2, "Mat2"]:
        if isinstance(other, Vector2):
            return Vector2(
                self.m00 * other.x + self.m01 * other.y,
                self.m10 * other.x + self.m11 * other.y
            )
        return Mat2(
            self.m00 * other.m00 + self.m01 * other.m10,
            self.m00 * other.m01 + self.m01 * other.m11,
            self.m10 * other.m00 + self.m11 * other.m10,
            self.m10 * other.m01 + self.m11 * other.m11
        )
