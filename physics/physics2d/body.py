import math

from .shape import Shape
from .utils import random
from .vector import Vector2


class Body:
    def __init__(self, shape: Shape, x: int, y: int):
        self.shape = shape.clone()
        self.shape.body = self

        self.velocity = Vector2()
        self.position = Vector2(x, y)

        self.torque = 0.0
        self.force = Vector2()
        self.angular_velocity = 0.0
        self.orientation = random(-math.pi, math.pi)

        self.restitution = 0.2
        self.static_friction = 0.5
        self.dynamic_friction = 0.3

        self.r, self.g, self.b = (
            random(.2, 1.0),
            random(.2, 1.0),
            random(.2, 1.0)
        )
        self.mass = 0.0
        self.inv_mass = 0.0

        self.moment = 0.0
        self.inv_moment = 0.0
        self.shape.initialize()

    def apply_force(self, f: Vector2):
        self.force += f

    def apply_impulse(self, impulse: Vector2, contactVec: Vector2):
        self.velocity += self.inv_mass * impulse
        self.angular_velocity += self.inv_moment * contactVec.cross(impulse)

    def set_static(self):
        self.mass = 0.0
        self.inv_mass = 0.0

        self.moment = 0.0
        self.inv_moment = 0.0

    def set_orient(self, radians: float):
        self.orientation = radians
        self.shape.set_orient(radians)
