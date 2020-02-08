from __future__ import annotations

import sys
import math

from .vector import Vector2
from .constants import EPSILON

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .body import Body
    from .manifold import Manifold


def CircletoCircle(m: Manifold, a: Body, b: Body):
    A = a.shape
    B = b.shape

    normal = b.position - a.position
    dist_sqr = normal.length_sqr
    radius = A.radius + B.radius

    # -- no contact
    if dist_sqr >= radius**2:
        m.contact_count = 0
        return

    distance = math.sqrt(dist_sqr)
    m.contact_count = 1

    if distance == 0.0:
        m.penetration = A.radius
        m.normal = Vector2(1.0, 0.0)
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
