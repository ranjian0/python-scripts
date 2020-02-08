import sys
import math
import pygame as pg
import OpenGL.GL as gl
import OpenGL.GLU as glu
from enum import Enum
from typing import Union, List, Any

DT = 1.0 / 60.0
EPSILON = 0.0001
GRAVITY_SCALE = 5.0


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


class Vec2:
    __slots__ = ['x', 'y']

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)

    def __add__(self, other) -> "Vec2":
        if isinstance(other, Vec2):
            return Vec2(self.x+other.x, self.y+other.y)
        return Vec2(self.x+other, self.y+other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x-other.x, self.y-other.y)

    def __isub__(self, other: "Vec2"):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, t: float) -> "Vec2":
        return Vec2(self.x*t, self.y*t)

    def __imul__(self, t: float):
        self.x *= t
        self.y *= t
        return self

    def __rmul__(self, t: float) -> "Vec2":
        return Vec2(t * self.x, t * self.y)

    def __truediv__(self, t: float):
        return Vec2(self.x/t, self.y/t)

    def max(self, other: "Vec2") -> "Vec2":
        return Vec2(max(self.x, other.x), max(self.y, other.y))

    def min(self, other: "Vec2") -> "Vec2":
        return Vec2(min(self.x, other.x), min(self.y, other.y))

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Union["Vec2", float]) -> Union["Vec2", float]:
        if isinstance(other, Vec2):
            return self.x * other.y - self.y * other.x
        return Vec2(other * self.y, -other * self.x)

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def length_sqr(self) -> float:
        return self.x**2 + self.y**2

    def distance(self, other: "Vec2") -> float:
        return (self - other).length()

    def distance_sqr(self, other: "Vec2") -> float:
        return (self - other).length_sqr()

    def rotate(self, radians: float):
        c = math.cos(radians)
        s = math.sin(radians)
        xp = self.x * c - self.y * s
        yp = self.x * s + self.y * c
        self.x = xp
        self.y = yp

    def normalize(self):
        ln = self.length()
        if ln > EPSILON:
            invLen = 1.0 / ln
            self.x *= invLen
            self.y *= invLen


GRAVITY = Vec2(0, 10.0 * GRAVITY_SCALE)


def Cross(t: float, v: Vec2) -> Vec2:
    return Vec2(-t * v.y, t * v.x)


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

    def axis_x(self) -> Vec2:
        return Vec2(self.m00, self.m10)

    def axis_y(self) -> Vec2:
        return Vec2(self.m01, self.m11)

    def transpose(self) -> "Mat2":
        return Mat2(self.m00, self.m10, self.m01, self.m11)

    def __mul__(self, other: Union[Vec2, "Mat2"]) -> Union[Vec2, "Mat2"]:
        if isinstance(other, Vec2):
            return Vec2(
                self.m00 * other.x + self.m01 * other.y,
                self.m10 * other.x + self.m11 * other.y
            )
        return Mat2(
            self.m00 * other.m00 + self.m01 * other.m10,
            self.m00 * other.m01 + self.m01 * other.m11,
            self.m10 * other.m00 + self.m11 * other.m10,
            self.m10 * other.m01 + self.m11 * other.m11
        )


class ShapeType(Enum):
    Circle = 0
    Poly = 1
    Count = 2


class Shape:
    def __init__(self):
        self.body = None
        self.radius = 0.0
        self.u = Mat2()

    def clone(self) -> "Shape":
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()

    def compute_mass(self, density: float):
        raise NotImplementedError()

    def set_orient(self, radians: float):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()

    def get_type(self) -> ShapeType:
        raise NotImplementedError()


class Circle(Shape):
    def __init__(self, r: float):
        Shape.__init__(self)
        self.radius = r

    def clone(self):
        return Circle(self.radius)

    def initialize(self):
        self.compute_mass(1.0)

    def compute_mass(self, density: float):
        self.body.mass = math.pi * self.radius**2 * density
        self.body.inv_mass = 1.0 / self.body.mass if self.body.mass else 0.0

        self.body.moment = self.body.mass * self.radius**2
        self.body.inv_moment = 1.0 / self.body.moment if self.body.moment else 0.0

    def set_orient(self, radians: float):
        pass

    def draw(self):
        segments = 20

        # -- draw circle with lines
        gl.glColor3f(self.body.r, self.body.g, self.body.b)
        gl.glBegin(gl.GL_LINE_LOOP)

        theta = self.body.orientation
        inc = math.pi * 2.0 / segments
        for i in range(segments):
            theta += inc
            p = Vec2(math.cos(theta), math.sin(theta))
            p *= self.radius
            p += self.body.position
            gl.glVertex2f(p.x, p.y)

        gl.glEnd()

        # -- draw line within circle so orientation is visible
        gl.glBegin(gl.GL_LINE_STRIP)

        c = math.cos(self.body.orientation)
        s = math.sin(self.body.orientation)
        r = Vec2(0.0, 1.0)
        r.x = r.x * c - r.y * s
        r.y = r.x * s + r.y * c
        r *= self.radius
        r = r + self.body.position
        gl.glVertex2f(self.body.position.x, self.body.position.y)
        gl.glVertex2f(r.x, r.y)
        gl.glEnd()

    def get_type(self) -> ShapeType:
        return ShapeType.Circle


MAXPOLY_VERTEXCOUNT = 64


class Polygon(Shape):
    def __init__(self):
        Shape.__init__(self)

        self.vertex_count = 0
        self.vertices = [Vec2() for _ in range(MAXPOLY_VERTEXCOUNT)]
        self.normals = [Vec2() for _ in range(MAXPOLY_VERTEXCOUNT)]

    def initialize(self):
        self.compute_mass(1.0)

    def clone(self):
        poly = Polygon()
        poly.u = self.u
        for i in range(self.vertex_count):
            poly.vertices[i] = self.vertices[i]
            poly.normals[i] = self.normals[i]
        poly.vertex_count = self.vertex_count
        return poly

    def compute_mass(self, density: float):
        c = Vec2()
        area = 0.0
        I = 0.0
        k_inv3 = 1.0 / 3.0

        for i in range(self.vertex_count):
            p1 = self.vertices[i]
            i2 = i + i if i + 1 < self.vertex_count else 0
            p2 = self.vertices[i2]

            D = p1.cross(p2)
            triangle_area = 0.5 * D
            area += triangle_area

            c += triangle_area * k_inv3 * (p1 + p2)
            intx2 = p1.x * p1.x + p2.x * p1.x + p2.x * p2.x
            inty2 = p1.y * p1.y + p2.y * p1.y + p2.y * p2.y
            I += (0.25 * k_inv3 * D) * (intx2 + inty2)

        c *= 1.0 / area

        for j in range(self.vertex_count):
            self.vertices[j] -= c

        self.body.mass = density * area
        self.body.inv_mass = 1.0 / self.body.mass if self.body.mass else 0.0
        self.body.moment = I * density
        self.body.inv_moment = 1.0 / self.body.moment if self.body.moment else 0.0

    def set_orient(self, radians: float):
        self.u = Mat2.from_angle(radians)

    def draw(self):
        gl.glColor3f(self.body.r, self.body.g, self.body.b)
        gl.glBegin(gl.GL_LINE_LOOP)
        for i in range(self.vertex_count):
            v = self.body.position + (self.u * self.vertices[i])
            gl.glVertex2f(v.x, v.y)
        gl.glEnd()

    def get_type(self) -> ShapeType:
        return ShapeType.Poly

    def set_box(self, hw: float, hh: float):
        self.vertex_count = 4
        self.vertices[0] = Vec2(-hw, -hh)
        self.vertices[1] = Vec2(+hw, -hh)
        self.vertices[2] = Vec2(+hw, +hh)
        self.vertices[3] = Vec2(-hw, +hh)

        self.normals[0] = Vec2(+0.0, -1.0)
        self.normals[1] = Vec2(+1.0,  0.0)
        self.normals[2] = Vec2(+0.0,  1.0)
        self.normals[3] = Vec2(-1.0,  0.0)

    def set(self, vertices: List[Vec2], count: int):
        assert count > 2 and count < MAXPOLY_VERTEXCOUNT
        count = min(count, MAXPOLY_VERTEXCOUNT)

        rightmost = 0
        highest_xcoord = vertices[0].x
        for i in range(count):
            x = vertices[i].x
            if x > highest_xcoord:
                highest_xcoord = x
                rightmost = i
            elif x == highest_xcoord:
                if vertices[i].y < vertices[rightmost].y:
                    rightmost = i

        hull = [0 for _ in range(MAXPOLY_VERTEXCOUNT)]
        outcount = 0
        indexhull = rightmost

        while True:
            hull[outcount] = indexhull

            nexthull_index = 0
            for j in range(count):
                if nexthull_index == indexhull:
                    nexthull_index = i
                    continue

                e1 = vertices[nexthull_index] - vertices[hull[outcount]]
                e2 = vertices[j] - vertices[hull[outcount]]
                c = e1.cross(e2)
                if c < 0.0:
                    nexthull_index = j

                if c == 0.0 and e2.length_sqr() > e1.length_sqr():
                    nexthull_index - j

            outcount += 1
            indexhull = nexthull_index

            if nexthull_index == rightmost:
                self.vertex_count = outcount
                break

        for i in range(self.vertex_count):
            self.vertices[i] = vertices[hull[i]]

        for k in range(self.vertex_count):
            i2 = k + 1 if k + 1 < self.vertex_count else 0
            face = self.vertices[i2] - self.vertices[k]

            assert(face.length_sqr() > EPSILON**2)

            self.normals[k] = Vec2(face.y, -face.x)
            self.normals[k].normalize()

    def get_support(self, dir_: Vec2) -> Vec2:
        best_projection = -sys.float_info.max
        best_vertex = Vec2()

        for i in range(self.vertex_count):
            v = self.vertices[i]
            projection = v.dot(dir_)

            if projection > best_projection:
                best_vertex = v
                best_projection = projection

        return best_vertex


class Body:
    def __init__(self, shape: Shape, x: int, y: int):
        self.shape = shape.clone()
        self.shape.body = self

        self.velocity = Vec2()
        self.position = Vec2(x, y)

        self.torque = 0.0
        self.force = Vec2()
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

    def apply_force(self, f: Vec2):
        self.force += f

    def apply_impulse(self, impulse: Vec2, contactVec: Vec2):
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


def list2d(dimx: int, dimy: int, item: Any = None):
    result = []
    for _ in range(dimy):
        inner = [item for _ in range(dimx)]
        result.append(inner)
    return result


Dispatch = list2d(
    ShapeType.Count.value, ShapeType.Count.value,
    lambda m, A, B: None
)


class Manifold:
    def __init__(self, a: Body, b: Body):
        self.A = a
        self.B = b

        self.penetration = 0.0
        self.normal = Vec2()
        self.contacts = [Vec2(), Vec2()]
        self.contact_count = 0

        # -- restitution, dynamic and statuc friction
        self.e = 0.0
        self.df = 0.0
        self.sf = 0.0

    def solve(self):
        Dispatch[self.A.shape.get_type().value][self.B.shape.get_type().value](self, self.A, self.B)

    def initialize(self):
        self.e = min(self.A.restitution, self.B.restitution)
        self.sf = math.sqrt(self.A.static_friction * self.B.static_friction)
        self.df = math.sqrt(self.A.dynamic_friction * self.B.dynamic_friction)

        for i in range(self.contact_count):
            ra = self.contacts[i] - self.A.position
            rb = self.contacts[i] - self.B.position

            rv = (
                self.B.velocity + Cross(self.B.angular_velocity, rb) -
                self.A.velocity - Cross(self.A.angular_velocity, ra)
            )
            if rv.length_sqr() < (DT * GRAVITY).length_sqr() + EPSILON:
                self.e = 0.0

    def apply_impulse(self):
        if equal(self.A.inv_mass + self.B.inv_mass, 0.0):
            self.infinite_mass_correction()
            return

        for i in range(self.contact_count):
            ra = self.contacts[i] - self.A.position
            rb = self.contacts[i] - self.B.position

            rv = (
                self.B.velocity + Cross(self.B.angular_velocity, rb) -
                self.A.velocity - Cross(self.A.angular_velocity, ra)
            )

            contactVel = rv.dot(self.normal)
            if contactVel > 0.0:
                return

            raCrossN = ra.cross(self.normal)
            rbCrossN = rb.cross(self.normal)
            inv_mass_sum = (
                self.A.inv_mass + self.B.inv_mass +
                raCrossN**2 * self.A.inv_moment +
                rbCrossN**2 * self.B.inv_moment
            )

            # -- calc impulse scalar
            j = -(1.0 + self.e) * contactVel
            j /= inv_mass_sum
            j /= float(self.contact_count)

            # -- apply impulse
            impulse = self.normal * j
            self.A.apply_impulse(-impulse, ra)
            self.B.apply_impulse(impulse, rb)

            # -- friction impuls
            rv = (
                self.B.velocity + Cross(self.B.angular_velocity, rb) -
                self.A.velocity - Cross(self.A.angular_velocity, ra)
            )

            t = rv - (self.normal * rv.dot(self.normal))
            t.normalize()

            # -- tangent magnitude
            jt = -rv.dot(t)
            jt /= inv_mass_sum
            jt /= float(self.contact_count)

            # -- dont apply tiny friction impulses
            if equal(jt, 0.0):
                return

            tangent_impulse = t * -j * self.df
            if abs(jt) < j * self.sf:
                tangent_impulse = t * jt

            # -- apply friction impulse
            self.A.apply_impulse(-tangent_impulse, ra)
            self.B.apply_impulse(tangent_impulse, rb)

    def positional_correction(self):
        slop = 0.05
        percent = 0.4
        correction = max(self.penetration - slop, 0.0) / (self.A.inv_mass + self.B.inv_mass) * self.normal * percent
        self.A.position -= correction * self.A.inv_mass
        self.B.position += correction * self.B.inv_mass

    def infinite_mass_correction(self):
        self.A.velocity = Vec2()
        self.B.velocity = Vec2()


def CircletoCircle(m: Manifold, a: Body, b: Body):
    A = a.shape
    B = b.shape

    normal = b.position - a.position
    dist_sqr = normal.length_sqr()
    radius = A.radius + B.radius

    # -- no contact
    if dist_sqr >= radius**2:
        m.contact_count = 0
        return

    distance = math.sqrt(dist_sqr)
    m.contact_count = 1

    if distance == 0.0:
        m.penetration = A.radius
        m.normal = Vec2(1.0, 0.0)
        m.contacts[0] = a.position
    else:
        m.penetration = radius - distance
        m.normal = normal / distance
        m.contacts[0] = m.normal * A.radius + a.position


def CircletoPolygon(m: Manifold, a: Body, b: Body):
    A = a.shape
    B = b.shape

    m.contact_count = 0

    # -- transform circle center to polygon model space
    center = a.position
    center = B.u.transpose() * (center - b.position)

    # -- find edge with minimum penetration
    separation = -sys.float_info.max
    face_normal = 0
    for i in range(B.vertex_count):
        s = B.normals[i].dot(B.vertices[i])
        if s > A.radius:
            return

        if s > separation:
            separation = s
            face_normal = i

    # -- grab face vertices
    v1 = B.vertices[face_normal]
    i2 = face_normal + 1 if face_normal + 1 < B.vertex_count else 0
    v2 = B.vertices[i2]

    # -- check if center within polygon
    if separation < EPSILON:
        m.contact_count = 1
        m.normal = -(B.u * B.normals[face_normal])
        m.contacts[0] = m.normal * A.radius + a.position
        m.penetration = A.radius
        return

    # -- determine which voronoi region circle lies within
    dot1 = (center - v1).dot(v2 - v1)
    dot2 = (center - v2).dot(v1 - v2)
    m.penetration = A.radius - separation

    if dot1 <= 0.0:
        if center.distance_sqr(v1) > A.radius**2:
            return

        m.contact_count = 1
        n = v1 - center
        n = B.u * n
        n.normalize()
        m.normal = n

        v1 = B.u * v1 + b.position
        m.contacts[0] = v1

    elif dot2 <= 0.0:
        if center.distance_sqr(v2) > A.radius**2:
            return

        m.contact_count = 1
        n = v2 - center
        n = B.u * n
        n.normalize()
        m.normal = n

        v2 = B.u * v2 + b.position
        m.contacts[0] = v2

    else:
        n = B.normals[face_normal]
        if (center - v1).dot(n) > A.radius:
            return

        n = B.u * n
        m.normal = -n
        m.contacts[0] = m.normal * A.radius + a.position
        m.contact_count = 1


def PolygontoCircle(m: Manifold, a: Body, b: Body):
    CircletoPolygon(m, b, a)
    m.normal = -m.normal


def PolygontoPolygon(m: Manifold, a: Body, b: Body):
    pass


Dispatch = [
    [CircletoCircle, CircletoPolygon],
    [PolygontoCircle, PolygontoPolygon]
]


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
            b.velocity = Vec2()
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


def init_gl():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, 80, 60, 0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()


def init_scene(scene):
    c = Circle(5.0)
    b = scene.add(c, 40, 40)
    b.set_static()

    p = Polygon()
    p.set_box(30.0, 1.0)
    b = scene.add(p, 40, 55)
    b.set_orient(0.0)
    b.set_static()


def on_mouse(scene, event):
    x, y = event.pos
    x /= 10.0
    y /= 10.0

    if event.button == 1:  # == LEFT
        poly = Polygon()
        count = int(random(3, MAXPOLY_VERTEXCOUNT))

        vertices = list()
        e = random(5, 10)
        for i in range(count):
            vertices.append(Vec2(random(-e, e), random(-e, e)))
        poly.set(vertices, count)
        b = scene.add(poly, x, y)
        b.set_orient(random(-math.pi, math.pi))
        b.restitution = 0.2
        b.dynamic_friction = 0.2
        b.static_friction = 0.4
        del vertices

    elif event.button == 3:  # == RIGHT
        c = Circle(random(1.0, 3.0))
        b = scene.add(c, x, y)


def main():
    pg.init()
    pg.display.set_caption("Physics Sandbox")

    scene = Scene(1.0 / 15.0, 10)
    screen = pg.display.set_mode(
        (800, 600),
        pg.OPENGL | pg.RESIZABLE | pg.DOUBLEBUF
    )

    init_gl()
    init_scene(scene)

    while True:
        for event in pg.event.get():
            should_exit = (
                event.type == pg.QUIT or
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            )
            if should_exit:
                pg.quit(); sys.exit()
            if event.type == pg.VIDEORESIZE:
                gl.glViewport(0, 0, *event.size)
                screen = pg.display.set_mode(
                    event.size, pg.OPENGL | pg.RESIZABLE | pg.DOUBLEBUF
                )
            if event.type == pg.MOUSEBUTTONDOWN:
                on_mouse(scene, event)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClearColor(.2, .2, .2, 1.0)
        scene.step()
        scene.render()
        pg.display.flip()


if __name__ == '__main__':
    main()