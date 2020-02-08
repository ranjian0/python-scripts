import sys
import math
import pygame as pg
import OpenGL.GL as gl
import OpenGL.GLU as glu

from physics2d.utils import random
from physics2d.constants import MAXPOLY_VERTEXCOUNT
from physics2d import Scene, Circle, Polygon, Vector2


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


def on_mouse(scene: Scene, event):
    x, y = event.pos
    x /= 10.0
    y /= 10.0

    if event.button == 1:  # == LEFT
        poly = Polygon()
        count = int(random(3, MAXPOLY_VERTEXCOUNT))

        vertices = list()
        e = random(5, 10)
        for i in range(count):
            vertices.append(Vector2(random(-e, e), random(-e, e)))
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
