import pyglet as pg
from pyglet.gl import *
from math import pi, cos, sin, sqrt, radians

class Shape:

    def __init__(self, batch=None):
        self.batch = batch or pg.graphics.Batch()
        self.group = pg.graphics.OrderedGroup(0)
        self._vertex_lists = {}
        self._child_shapes = {}

    def add(self, name, *args):
        vl = self.batch.add(*args)
        self._vertex_lists[name] = vl

    def add_shape(self, name, shape):
        self._child_shapes[name] = shape

    def remove(self, name):
        child = self._child_shapes.pop(name, None)
        vl = self._vertex_lists.pop(name, None)
        if vl:
            vl.delete()

    def translate(self, dx, dy, name=None):
        for _, child in self._child_shapes.items():
            child.translate(dx, dy, name)

        for n, vl in self._vertex_lists.items():
            vts = vl.vertices
            if name and n == name:
                vl.vertices = sum([[vx+dx, vy+dy] for vx, vy in zip(vts[::2], vts[1::2])], [])
                break
            elif not name:
                vl.vertices = sum([[vx+dx, vy+dy] for vx, vy in zip(vts[::2], vts[1::2])], [])

    def rotate(self, angle, name=None):
        for _, child in self._child_shapes.items():
            child.rotate(angle, name)

        angle = radians(angle)
        rot = lambda x,y : [x*cos(angle)-y*sin(angle), x*sin(angle)+y*cos(angle)]
        add = lambda o,p : [o[0]+p[0], o[1]+p[1]]
        def center(verts):
            return sum(verts[::2])/len(verts[::2]), sum(verts[1::2])/len(verts[1::2])

        for n, vl in self._vertex_lists.items():
            vts = vl.vertices
            cx, cy = center(vts)
            if name and n == name:
                vl.vertices = sum([add(rot(vx-cx,vy-cy), (cx, cy)) for vx, vy in zip(vts[::2], vts[1::2])], [])
                break
            elif not name:
                vl.vertices = sum([add(rot(vx-cx,vy-cy), (cx, cy)) for vx, vy in zip(vts[::2], vts[1::2])], [])

    def set_color(self, name, col):
        size = len(self._vertex_lists[name])
        vl = self._vertex_lists[name]
        vl.colors = col * ln

    def hit_test(self, x, y):
        return NotImplementedError

    def draw(self):
        self.batch.draw()
        for _,child in self._child_shapes.items():
            child.draw()

class RectangleShape(Shape):

    def __init__(self, x, y, w, h, color, radius=0, border=False, border_color=[120, 120, 120, 255],
                    fill=True, shadow=False, flat_bottom=False):
        Shape.__init__(self)
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.color = color

        if radius == 0:
            x1, y1 = x, y
            x2, y2 = x + w, y - h

            if not fill: pg.gl.glLineWidth(2)
            mode = pg.gl.GL_QUADS if fill else pg.gl.GL_LINE_LOOP

            self.add("background",
                        4, mode, pg.graphics.OrderedGroup(1),
                         ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                         ('c4B', color * 4))

            if border:
                pg.gl.glLineWidth(2)
                self.add("border",
                            4, pg.gl.GL_LINE_LOOP, pg.graphics.OrderedGroup(2),
                             ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                             ('c4B', border_color * 4))

            if shadow and fill:
                self.add("shadow",
                            4, pg.gl.GL_QUADS, pg.graphics.OrderedGroup(0),
                             ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
                             ('c4B', [10, 10, 10, 80] * 4))
                self.translate(3, -3, "shadow")

        else:
            # -- create circle vertices
            resolution = 32
            arc = (2*pi) / resolution if not flat_bottom else pi / resolution
            x += radius
            y -= radius
            w -= radius*2
            h -= radius*2

            transform = [
                (x+w, y),   # - top right
                (x,   y),   # - top left
                (x,   y-h), # - bottom left
                (x+w, y-h), # - bottom right
            ]

            tindex = 0
            circle = []
            if not flat_bottom: # -- full circle
                for r in range(resolution):
                    angle = r*arc
                    if r > resolution//4:
                        tindex = 1
                    if r > resolution//2:
                        tindex = 2
                    if r > resolution*.75:
                        tindex = 3
                    tx, ty = transform[tindex]
                    circle.extend([tx + cos(angle)*radius, ty + sin(angle)*radius])
            else: # -- semi circle
                for r in range(resolution+1):
                    angle = r*arc
                    if r > resolution//2:
                        tindex = 1
                    tx, ty = transform[tindex]
                    circle.extend([tx + cos(angle)*radius, ty + sin(angle)*radius])

                circle[1] -= h+radius
                circle[len(circle)-1] -= h+radius

            if not fill: pg.gl.glLineWidth(2)
            mode = pg.gl.GL_POLYGON if fill else pg.gl.GL_LINE_LOOP

            self.add("background",
                        len(circle)//2, mode, pg.graphics.OrderedGroup(1),
                         ('v2f', circle),
                         ('c4B', color * (len(circle)//2)))

            if shadow and fill:
                self.add("shadow",
                            len(circle)//2, pg.gl.GL_POLYGON, pg.graphics.OrderedGroup(0),
                             ('v2f', circle),
                             ('c4B', [10, 10, 10, 80] * (len(circle)//2)))
                self.translate(3, -3, "shadow")

    def hit_test(self, x, y):
        return (self.x < x < self.x+self.w and self.y-self.h < y < self.y)

class CircleShape(Shape):

    def __init__(self, x, y, radius, color, fill=True, shadow=False):
        Shape.__init__(self)
        self.x, self.y = x, y
        self.radius = radius
        self.color = color

        resolution = 64
        arc = (2*pi) / resolution

        circle = []
        for r in range(resolution):
            angle = r*arc
            circle.extend([x + cos(r*arc)*radius, y + sin(r*arc)*radius])


        if not fill: pg.gl.glLineWidth(2)
        mode = pg.gl.GL_POLYGON if fill else pg.gl.GL_LINE_LOOP

        self.add("background",
                    len(circle)//2, mode, pg.graphics.OrderedGroup(1),
                     ('v2f', circle),
                     ('c4B', color * (len(circle)//2)))

        if shadow and fill:
            self.add("shadow",
                        len(circle)//2, pg.gl.GL_POLYGON, pg.graphics.OrderedGroup(0),
                         ('v2f', circle),
                         ('c4B', (10, 10, 10, 80) * (len(circle)//2)))
            self.translate(3, -3, "shadow")

    def hit_test(self, x, y):
        p1, p2 = x-self.x, y-self.y
        return p1**2 + p2**2 <= self.radius**2

class Decorators:

    @classmethod
    def tria_left(cls, x, y, size=12, color=[25, 25, 25, 255]):
        tri_left = Shape()
        tri_left.add("shape", 3, pg.gl.GL_TRIANGLES, pg.graphics.OrderedGroup(0),
                            ('v2f', [0,size,size,size/2,0,0]),
                            ('c4B', color*3))
        tri_left.translate(x, y-size/2)
        return tri_left

    @classmethod
    def tria_down(cls, x, y, size=12, color=[25, 25, 25, 255]):
        tri_down = Shape()
        tri_down.add("shape", 3, pg.gl.GL_TRIANGLES, pg.graphics.OrderedGroup(0),
                            ('v2f', [0,size,size,size,size/2,0]),
                            ('c4B', color*3))
        tri_down.translate(x, y-size/2)
        return tri_down



if __name__ == '__main__':
    r1 = RectangleShape(20, 200, 100, 100, (100, 100, 100, 255))
    r2 = RectangleShape(200, 200, 100, 45, (100, 100, 100, 255), 10)
    r3 = RectangleShape(200, 150, 100, 45, (100, 100, 100, 255), 10, flat_bottom=True)


    c1 = CircleShape(400, 150, 40, (100, 100, 100, 255), False)
    c2 = CircleShape(400, 150, 35, (100, 100, 100, 255))


    d1 = Decorators.tria_left(10, 10)
    d2 = Decorators.tria_down(25, 10)

    def on_draw():
        base.window.clear()
        c1.draw()
        c2.draw()

        r1.draw()
        r2.draw()
        r3.draw()

        d1.draw()
        d2.draw()

    def on_mouse_motion(x, y, *args):
        pass
        # print(c1.hit_test(x, y), "--",x, y)

    base.push_handler(on_draw)
    base.push_handler(on_mouse_motion)
    base.run()

