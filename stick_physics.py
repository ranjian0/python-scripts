import math
import operator
import pyglet as pg
import itertools as it
from pyglet.gl import *

DAMPING = 0.01
TIME_STEP = 0.5 * 0.5
CONSTRAINT_ITERATIONS = 5


class Vec3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def zero(cls):
        return cls(0, 0, 0)

    @classmethod
    def one(cls):
        return cls(1, 1, 1)

    def __iter__(self):
        return iter([self.x, self.y, self.z])

    def tuple(self):
        return self.x, self.y, self.z

    def length(self):
        return math.sqrt(sum(map(operator.mul, self, self)))

    def normalized(self):
        l = self.length()
        if l > 0.0:
            return Vec3(self.x/l, self.y/l, self.z/l)
        return self

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def __iadd__(self, other):
        return Vec3(*tuple(map(operator.iadd, self, other)))

    def __add__(self, other):
        return Vec3(*tuple(map(operator.add, self, other)))

    def __sub__(self, other):
        return Vec3(*tuple(map(operator.sub, self, other)))

    def __mul__(self, other):
        if isinstance(other, (int,float)):
            return Vec3(self.x*other, self.y*other, self.z*other)
        elif isinstance(other, Vec3):
            return Vec3(*tuple(map(operator.mul, self, other)))

    def __truediv__(self, other):
        if isinstance(other, (int,float)):
            return Vec3(self.x/other, self.y/other, self.z/other)
        elif isinstance(other, Vec3):
            return Vec3(*tuple(map(operator.truediv, self, other)))

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y and self.z < other.z

    def __neg__(self):
        return Vec3(*tuple(map(operator.neg, self)))

    def dot(self, other):
        return sum(map(operator.mul, self, other))

    def cross(self, other):
        return Vec3(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x
        )

def clamp(x, _min, _max):
    return max(_min, min(_max, x))


class Particle:

    def __init__(self, position):
        self.position = position
        self.old_pos = position

        self.mass = 1
        self.acceleration = Vec3.zero()

    def add_force(self, force):
        self.acceleration += force / self.mass

    def step(self):
        current = self.position
        self.position = (
                self.position
                + (self.position - self.old_pos) * (1-DAMPING)
                + self.acceleration * TIME_STEP
            )

        self.old_pos = current
        self.acceleration = Vec3.zero()

class Constraint:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.rest_distance = (p1.position - p2.position).length()

    def satisfy(self):
        p1_to_p2 = self.p2.position - self.p1.position
        current_distance = p1_to_p2.length()

        correction_vector = p1_to_p2*(1 - self.rest_distance/current_distance)
        self.p1.position +=  correction_vector*0.5
        self.p2.position += -correction_vector*0.5

class Box:

    def __init__(self, top, w, h):
        self.top = top
        self.w = w
        self.h = h

        self.particles, self.constraints = self._make()

        self.resolution = Vec3.zero()

    def _make(self):
        top, w, h = self.top, self.w, self.h

        p1, p2, p3, p4 = (
            Particle(top),                    # Top right
            Particle(top + Vec3(w, 0, 0)),    # Top Left
            Particle(top + Vec3(w, h, 0)),    # Bottom Left
            Particle(top + Vec3(0, h, 0))     # Bottom right
        )

        constraints = (
            Constraint(p1, p2),
            Constraint(p2, p3),
            Constraint(p3, p4),
            Constraint(p4, p1),
            Constraint(p1, p3)
        )

        return [p1, p2, p3, p4], constraints

    def update(self):
        for p in self.particles:
            p.step()

            # -- world clamping
            p.position.x = clamp(p.position.x, 3, 497)
            p.position.y = clamp(p.position.y, 3, 497)

        for s in self.constraints:
            s.satisfy()

        self.top = self.particles[0].position

    def add_force(self, f):
        for p in self.particles:
            p.add_force(f)

    def draw(self):
        verts = list(it.chain.from_iterable(p.position.tuple() for p in self.particles))
        glLineWidth(2)
        pg.graphics.draw(4, GL_LINE_LOOP,
            ('v3f', verts),
            ('c4B', (255, 255, 255, 255)*4)
            )


class Circle:

    def __init__(self, pos, radius):
        self.position = pos
        self.radius = radius

        self.particle = Particle(pos)

    def update(self):
        self.particle.step()
        if self.particle.position.y < self.radius+3:
            self.particle.position.y = self.radius+3

    def add_force(self, f):
        self.particle.add_force(f)

    def draw(self):
        x,y,z = self.particle.position
        resolution = 64
        arc = (2*math.pi) / resolution

        verts = []
        for r in range(resolution):
            angle = r*arc
            verts.extend([x + math.cos(r*arc)*self.radius, y + math.sin(r*arc)*self.radius])

        count = len(verts)//2
        pg.graphics.draw(count, GL_LINE_LOOP,
            ('v2f', verts),
            ('c4B', (255, 255, 255, 255)*count))


window = pg.window.Window(500, 500, "Stick Physics")

objects = []
positions = [
    (100, 100),
    (140, 200),
    (300, 300)
]
boxes = [Box(Vec3(*p, 0), 50, 50) for p in positions]
circles = [Circle(Vec3(x+70,y+100, 0), 25) for x,y in positions]
objects.extend(boxes + circles)

@window.event
def on_draw():
    window.clear()
    glClearColor(.2, .3, .3, 1)

    for obj in objects:
        obj.draw()

def on_update(dt):
    for obj in objects:
        obj.add_force(Vec3(0, -.9, 0))
        obj.update()

def main():
    pg.clock.schedule_interval(on_update, 1/60)
    pg.app.run()

if __name__ == '__main__':
    main()