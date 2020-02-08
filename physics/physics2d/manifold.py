import math
from . import dispatcher
from .body import Body
from .vector import Vector2
from .utils import equal, Cross
from .constants import DT, EPSILON, GRAVITY


class Manifold:
    def __init__(self, a: Body, b: Body):
        self.A = a
        self.B = b

        self.penetration = 0.0
        self.normal = Vector2()
        self.contacts = [Vector2(), Vector2()]
        self.contact_count = 0

        # -- restitution, dynamic and statuc friction
        self.e = 0.0
        self.df = 0.0
        self.sf = 0.0

    def solve(self):
        type_A = self.A.shape.get_type().value
        type_B = self.B.shape.get_type().value
        dispatcher.Dispatch[type_A][type_B](self, self.A, self.B)

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
            if rv.length_sqr < (DT * GRAVITY).length_sqr + EPSILON:
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
        self.A.velocity = Vector2()
        self.B.velocity = Vector2()
