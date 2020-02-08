import OpenGL.GL as gl
from typing import List

from .body import Body
from .shape import Shape
from .vector import Vector2
from .manifold import Manifold
from .constants import GRAVITY


def IntegrateForces(b: Body, dt: float):
    if b.inv_mass == 0.0:
        return

    b.velocity += (b.force * b.inv_mass + GRAVITY) * (dt / 2.0)
    b.angular_velocity += b.torque * b.inv_moment * (dt / 2.0)


def IntegrateVelocity(b: Body, dt: float):
    if b.inv_mass == 0.0:
        return

    b.position += b.velocity * dt
    b.orientation += b.angular_velocity * dt
    b.set_orient(b.orientation)
    IntegrateForces(b, dt)


class Scene:
    def __init__(self, dt: float, iterations: int):
        self.dt = dt
        self.iterations = iterations
        self.bodies: List[Body] = list()
        self.contacts: List[Manifold] = list()

    def step(self):
        # -- generate collision info
        self.contacts.clear()
        for i in range(len(self.bodies)):
            A = self.bodies[i]

            for j in range(i+1, len(self.bodies)):
                B = self.bodies[j]

                if A.inv_mass == 0.0 and B.inv_mass == 0.0:
                    continue

                m = Manifold(A, B)
                m.solve()
                if m.contact_count:
                    self.contacts.append(m)

        # -- integrate forces
        for b in self.bodies:
            IntegrateForces(b, self.dt)

        # -- initialize collision
        for c in self.contacts:
            c.initialize()

        # -- solve collision
        for _ in range(self.iterations):
            for c in self.contacts:
                c.apply_impulse()

        # -- integrate velocities
        for b in self.bodies:
            IntegrateVelocity(b, self.dt)

        # -- correct positions
        for c in self.contacts:
            c.positional_correction()

        # -- clear all forces
        for b in self.bodies:
            b.velocity = Vector2()
            b.torque = 0

    def render(self):
        for b in self.bodies:
            b.shape.draw()

        gl.glPointSize(4.0)
        gl.glBegin(gl.GL_POINTS)
        gl.glColor3f(1.0, 0.0, 0.0)
        for c in self.contacts:
            for i in range(c.contact_count):
                cp = c.contacts[i]
                gl.glVertex2f(cp.x, cp.y)

        gl.glEnd()
        gl.glPointSize(1.0)

        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(0.0, 1.0, 0.0)
        for c in self.contacts:
            n = c.normal
            for i in range(c.contact_count):
                cp = c.contacts[i]
                gl.glVertex2f(cp.x, cp.y)
                n *= .75
                cp += n
                gl.glVertex2f(cp.x, cp.y)
        gl.glEnd()

    def add(self, shape: Shape, x: int, y: int):
        b = Body(shape, x, y)
        self.bodies.append(b)
        return b
