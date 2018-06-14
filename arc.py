from math import pi, sin, radians
import turtle as t

start = (-100, 0)
end = (100, 0)
dst = 200
def make_points(count=3):
    res = []
    res.append(start)

    off = dst / (count-1)
    for i in range(count-2):
        p = start[0] + ((i+1)*off), start[1]
        res.append(p)
    res.append(end)
    return res

def arc_points(points):
    ag = pi / (len(points)-1)
    for idx, p in enumerate(points):
        off = sin(ag*idx) * 100
        p = (p[0], p[1] + off)
        points[idx] = p

def draw_points(points):

    for p in points:
        t.pu()
        t.goto(p)
        t.pd()
        t.circle(5)

pts = make_points(5)
arc_points(pts)
draw_points(pts)

t.exitonclick()
