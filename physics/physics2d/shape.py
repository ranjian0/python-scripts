import sys
import math
import OpenGL.GL as gl

from enum import Enum
from typing import List
from .matrix import Mat2
from .vector import Vector2
from .constants import EPSILON


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
            p = Vector2(math.cos(theta), math.sin(theta))
            p *= self.radius
            p += self.body.position
            gl.glVertex2f(p.x, p.y)

        gl.glEnd()

        # -- draw line within circle so orientation is visible
        gl.glBegin(gl.GL_LINE_STRIP)

        c = math.cos(self.body.orientation)
        s = math.sin(self.body.orientation)
        r = Vector2(0.0, 1.0)
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
        self.vertices = [Vector2() for _ in range(MAXPOLY_VERTEXCOUNT)]
        self.normals = [Vector2() for _ in range(MAXPOLY_VERTEXCOUNT)]

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
        c = Vector2()
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
        self.vertices[0] = Vector2(-hw, -hh)
        self.vertices[1] = Vector2(+hw, -hh)
        self.vertices[2] = Vector2(+hw, +hh)
        self.vertices[3] = Vector2(-hw, +hh)

        self.normals[0] = Vector2(+0.0, -1.0)
        self.normals[1] = Vector2(+1.0,  0.0)
        self.normals[2] = Vector2(+0.0,  1.0)
        self.normals[3] = Vector2(-1.0,  0.0)

    def set(self, vertices: List[Vector2], count: int):
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

                if c == 0.0 and e2.length_sqr > e1.length_sqr:
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

            assert(face.length_sqr > EPSILON**2)

            self.normals[k] = Vector2(face.y, -face.x)
            self.normals[k].normalize()

    def get_support(self, dir_: Vector2) -> Vector2:
        best_projection = -sys.float_info.max
        best_vertex = Vector2()

        for i in range(self.vertex_count):
            v = self.vertices[i]
            projection = v.dot(dir_)

            if projection > best_projection:
                best_vertex = v
                best_projection = projection

        return best_vertex
