import math
import operator
import numpy as np
from ctypes import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

## PHYSICS CONSTANTS ##
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

    def length(self):
        return math.sqrt(sum(map(operator.mul, self, self)))

    def normalized(self):
        l = self.length()
        return Vec3(self.x/l, self.y/l, self.z/l)

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

class Particle:
# array = np.array(
#   [0, 0, 0] -- pos
#   [0, 0, 0] -- oldpos
#   [0, 0, 0] -- acceleration
# )

    def __init__(self, position):
        self.pos = position
        self.old_pos = position

        self.mass= 1.0 
        self.movable = True
        self.acceleration = Vec3.zero()
        self.accumulated_normal = Vec3.zero()

    def add_force(self, f):
        self.acceleration += f/self.mass

    def time_step(self):
        if self.movable:
            tmp = self.pos 
            self.pos = (
                self.pos 
                + (self.pos-self.old_pos)*(1.0-DAMPING)
                + self.acceleration*TIME_STEP)

            self.old_pos = tmp
            self.acceleration = Vec3.zero()

    def get_pos(self):
        return self.pos 

    def reset_acceleration(self):
        self.acceleration = Vec3.zero()

    def offset_pos(self, v):
        if self.movable:
            self.pos += v 

    def make_unmovable(self):
        self.movable = False

    def add_to_normal(self, n):
        self.accumulated_normal += n.normalized()

    def get_normal(self):
        return self.accumulated_normal

    def reset_normal(self):
        self.accumulated_normal = Vec3.zero()

class Constraint:

    def __init__(self, _p1, _p2):
        self.p1 = _p1 
        self.p2 = _p2 

        v = _p1.get_pos() - _p2.get_pos()
        self._rest_distance = v.length()


    def satisfy_constraint(self):

        p1_to_p2 = self.p2.get_pos() - self.p1.get_pos()
        current_distance = p1_to_p2.length()

        correction_vector = p1_to_p2*(1 - self._rest_distance/current_distance)
        correction_vector_half = correction_vector*0.5

        self.p1.offset_pos(correction_vector_half)
        self.p2.offset_pos(-correction_vector_half)

class Cloth:

    def __init__(self, width, height, 
                    num_particles_width,
                    num_particles_height):

        self._particles = []
        self._constraints = []

        self._num_particles_width = num_particles_width
        self._num_particles_height = num_particles_height

        #-- create particles in a grid (0, 0, 0) to (width, -height, 0)
        self._data = np.ones((num_particles_width, num_particles_height, 10))
        for x in range(num_particles_width):
            for y in range(num_particles_height):

                pos = Vec3(width * (x/num_particles_width),
                            -height * (y/num_particles_height),
                            0)
                self._data[x, y, :] = np.array([
                    width * (x/num_particles_width),
                    -height * (y/num_particles_height),
                    0,
                    0, 0, 0, # Normal
                    0, 0, 0, # Acceleration
                    1        # Mass
                ])
                self._particles.append(Particle(pos))

        #-- connecting immediate neighbour particles with constaints
        for x in range(num_particles_width):
            for y in range(num_particles_height):
                if x < num_particles_width-1:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x+1, y)
                    self._make_constraint(p1, p2)


                if y < num_particles_height-1:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x, y+1)
                    self._make_constraint(p1, p2)

                if x < num_particles_width-1 and y < num_particles_height-1:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x+1, y+1)
                    self._make_constraint(p1, p2)

                if x < num_particles_width-1 and y < num_particles_height-1:
                    p1, p2 = self._get_particle(x+1,y), self._get_particle(x, y+1)
                    self._make_constraint(p1, p2)

        #-- connecting secondary neighbour particles with constaints
        for x in range(num_particles_width):
            for y in range(num_particles_height):
                if x < num_particles_width-2:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x+2, y)
                    self._make_constraint(p1, p2)

                if y < num_particles_height-2:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x, y+2)
                    self._make_constraint(p1, p2)

                if x < num_particles_width-2 and y < num_particles_height-2:
                    p1, p2 = self._get_particle(x,y), self._get_particle(x+2, y+2)
                    self._make_constraint(p1, p2)

                if x < num_particles_width-2 and y < num_particles_height-2:
                    p1, p2 = self._get_particle(x+2,y), self._get_particle(x, y+2)
                    self._make_constraint(p1, p2)

        # -- making upper left most three and right most three unmovable
        for i in range(3):
            self._get_particle(0+i, 0).offset_pos(Vec3(0.5, 0, 0))
            self._get_particle(0+i, 0).make_unmovable()

            self._get_particle(0+i, 0).offset_pos(Vec3(-0.5, 0, 0))
            self._get_particle(self._num_particles_width-1-i, 0).make_unmovable()


    def _get_particle(self, x, y):
        return self._particles[y*self._num_particles_width + x]

    def _make_constraint(self, p1, p2):
        self._constraints.append(Constraint(p1, p2))

    def calc_tri_normal(self, p1, p2, p3):
        pos1, pos2, pos3 = (
            p1.get_pos(),
            p2.get_pos(),
            p3.get_pos()
        )

        v1 = pos2-pos1
        v2 = pos3-pos1 
        return v1.cross(v2)

    def add_wind_forces_for_tri(self, p1, p2, p3, direction):

        normal = self.calc_tri_normal(p1, p2, p3)
        d = normal.normalized()
        force = normal * (d.dot(direction))
        p1.add_force(force)
        p2.add_force(force)
        p3.add_force(force)

    def draw_tri(self, p1, p2, p3, color):
        arr = c_float * 3
        varr = lambda vec: arr(*tuple(vec))

        glColor3fv(varr(color))

        glNormal3fv(varr((p1.get_normal().normalized())))
        glVertex3fv(varr(p1.get_pos()))

        glNormal3fv(varr(p2.get_normal().normalized() ))
        glVertex3fv(varr(p2.get_pos() ))

        glNormal3fv(varr(p3.get_normal().normalized() ))
        glVertex3fv(varr(p3.get_pos() ))

    def draw_shaded(self):
        # reset normals 
        for p in self._particles:
            p.reset_normal()

        # make smooth per particle normals
        for x in range(self._num_particles_width-1):
            for y in range(self._num_particles_height-1):
                p1, p2, p3 = (
                    self._get_particle(x+1, y),
                    self._get_particle(x, y),
                    self._get_particle(x, y+1)
                )

                n = self.calc_tri_normal(p1, p2, p3)
                p1.add_to_normal(n)
                p2.add_to_normal(n)
                p3.add_to_normal(n)

                p1, p2, p3 = (
                    self._get_particle(x+1, y+1),
                    self._get_particle(x+1, y),
                    self._get_particle(x, y+1)
                )

                n = self.calc_tri_normal(p1, p2, p3)
                p1.add_to_normal(n)
                p2.add_to_normal(n)
                p3.add_to_normal(n)

        glBegin(GL_TRIANGLES)
        for x in range(self._num_particles_width-1):
            for y in range(self._num_particles_height-1):

                color = Vec3(.6, .2, .2) if x%2 else Vec3.one()
                self.draw_tri(
                    self._get_particle(x+1, y),
                    self._get_particle(x, y),
                    self._get_particle(x, y+1),
                    color
                )

                self.draw_tri(
                    self._get_particle(x+1, y+1),
                    self._get_particle(x+1, y),
                    self._get_particle(x, y+1),
                    color
                )
        glEnd()

    def time_step(self):

        for _ in range(CONSTRAINT_ITERATIONS):
            for c in self._constraints:
                c.satisfy_constraint()

        for p in self._particles:
            p.time_step()

    def add_force(self, direction):
        # use to add gravity and other forces to all particles
        for p in self._particles:
            p.add_force(direction)


    def wind_force(self, direction):
        # add wind force to all particles
        for x in range(self._num_particles_width-1):
            for y in range(self._num_particles_height-1):
                self.add_wind_forces_for_tri(
                    self._get_particle(x+1, y),
                    self._get_particle(x,y),
                    self._get_particle(x, y+1),
                    direction
                )

                self.add_wind_forces_for_tri(
                    self._get_particle(x+1, y+1),
                    self._get_particle(x+1,y),
                    self._get_particle(x, y+1),
                    direction
                )

    def ball_collision(self, center, radius):
        for p in self._particles:
            v = p.get_pos() - center 
            l = v.length()
            if l < radius:
                p.offset_pos(v.normalized()*(radius-l))
    

cloth = Cloth(10, 10, 10, 10)
ball_pos = Vec3(7, -5, 0)
ball_radius = 2

ball_time = 0

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.2, 0.2, 0.4, 0.5)				
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_COLOR_MATERIAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    arr = c_float * 4
    lightPos = arr(-1.0,1.0,0.5,0.0)
    glLightfv(GL_LIGHT0,GL_POSITION, lightPos)

    glEnable(GL_LIGHT1)

    lightAmbient1 = arr(0.0,0.0,0.0,0.0)
    lightPos1 = arr(1.0,0.0,-0.2,0.0)
    lightDiffuse1 = arr(0.5,0.5,0.3,0.0)

    glLightfv(GL_LIGHT1,GL_POSITION, lightPos1)
    glLightfv(GL_LIGHT1,GL_AMBIENT, lightAmbient1)
    glLightfv(GL_LIGHT1,GL_DIFFUSE, lightDiffuse1)

    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,GL_TRUE)


def display():
    global ball_time

    ball_time += 1
    ball_pos.z = math.cos(ball_time/50)*7


    cloth.add_force(Vec3(0, -0.2, 0) * TIME_STEP)
    cloth.wind_force(Vec3(0.5, 0, 0.2) * TIME_STEP)
    cloth.time_step()
    cloth.ball_collision(ball_pos, ball_radius)


    # -- drawing
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    ## Smooth shaded background
    glDisable(GL_LIGHTING)
    glBegin(GL_POLYGON)
    glColor3f(0.8,0.8,1.0)
    glVertex3f(-200.0,-100.0,-100.0)
    glVertex3f(200.0,-100.0,-100.0)
    glColor3f(0.4,0.4,0.8)	
    glVertex3f(200.0,100.0,-100.0)
    glVertex3f(-200.0,100.0,-100.0)
    glEnd()
    glEnable(GL_LIGHTING)

    glTranslatef(-6.5, 6, -9.0)
    glRotatef(25, 0, 1, 0)
    cloth.draw_shaded()

    glPushMatrix()
    glTranslatef(*tuple(ball_pos))
    glColor3f(.4, .8, .5)
    glutSolidSphere(ball_radius-.1, 50, 50)
    glPopMatrix()

    glutSwapBuffers()
    glutPostRedisplay()


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    if h==0:
        gluPerspective(80, w, 1.0, 5000.0)
    else:
        gluPerspective(80, w/h, 1.0, 5000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()



if __name__ == '__main__':
    glutInit()
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1000, 600)

    glutCreateWindow("Cloth Simulation")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)

    glutMainLoop()
