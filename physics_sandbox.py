import math
import pyglet as pg
import pymunk as pm
import itertools as it
from pymunk import pyglet_util as putils

def test(space):
    space.gravity = (0, -9.8)
    
    player = pm.Body(1,10)
    player.position = (100, 300)
    player_shape = pm.Circle(player, 30)
    player_shape.friction = .5
    space.add(player, player_shape)
    
    shape = pm.Poly.create_box(space.static_body, size=(500, 10))
    shape.body.position = (260, 50)
    shape.body.angle = -.1
    shape.friction = .1
    space.add(shape)
    
def player_movement(space):
    
    player = pm.Body(1,10)
    player.position = (100, 300)
    player_shape = pm.Circle(player, 30)
    player_shape.friction = .5
    space.add(player, player_shape)
    
    sx, sy = Window.instance.get_size()
    walls = [
        # position -- size
        [(0 , sy/2), (10, sy)], # Left
        [(sx, sy/2), (10, sy)], # Right
        [(sx/2 ,sy), (sx, 10)], # Top
        [(sx/2 , 0), (sx, 10)], # Left
    ]
    for wall in walls:
        pos, size = wall
        shape = pm.Poly.create_box(space.static_body, size=size)
        shape.body.position = pos
        shape.friction = .1
        space.add(shape)
    
    speed = 25
    def on_key_press(symbol, mod):
        vx, vy = player.velocity
        if symbol == pg.window.key.W:
            vy = speed
        if symbol == pg.window.key.S:
            vy = -speed
        if symbol == pg.window.key.A:
            vx = -speed
        if symbol == pg.window.key.D:
            vx = speed
        player.velocity = (vx, vy)
                    
    def on_key_release(symbol, mod):
        vx, vy = player.velocity
        if symbol == pg.window.key.W:
            vy = 0
        if symbol == pg.window.key.S:
            vy = 0
        if symbol == pg.window.key.A:
            vx = 0
        if symbol == pg.window.key.D:
            vx = 0
        player.velocity = (vx, vy)
        
    def on_mouse_motion(x, y, dx, dy):
        px, py = player.position
        lx, ly = x -px, y - py 
        player.angle = math.atan2(ly, lx)
            
    Window.instance.push_handlers(on_key_press, on_key_release, on_mouse_motion)
    
def projectiles(space):
    
    player = pm.Body(100,10)
    player.position = (100, 300)
    player_shape = pm.Circle(player, 30)
    player_shape.friction = .5
    space.add(player, player_shape)
    
    sx, sy = Window.instance.get_size()
    walls = [
        # position -- size
        [(0 , sy/2), (10, sy)], # Left
        [(sx, sy/2), (10, sy)], # Right
        [(sx/2 ,sy), (sx, 10)], # Top
        [(sx/2 , 0), (sx, 10)], # Left
    ]
    for wall in walls:
        pos, size = wall
        shape = pm.Poly.create_box(space.static_body, size=size)
        shape.body.position = pos
        shape.friction = .1
        space.add(shape)
        
    def shoot():
        dx, dy = math.cos(player.angle), math.sin(player.angle)
        
        projectile = pm.Body(1,10)
        projectile.friction = .9
        projectile_shape = pm.Circle(projectile, 10)
        projectile_shape.elasticity = .5
        
        projectile.position = (
            player.position + pm.vec2d.Vec2d(dx, dy)*(player_shape.radius+projectile_shape.radius+5))
        space.add(projectile, projectile_shape)
        projectile.velocity = pm.vec2d.Vec2d(dx, dy) * 100
    
    speed = 25
    def on_key_press(symbol, mod):
        vx, vy = player.velocity
        if symbol == pg.window.key.W:
            vy = speed
        if symbol == pg.window.key.S:
            vy = -speed
        if symbol == pg.window.key.A:
            vx = -speed
        if symbol == pg.window.key.D:
            vx = speed
        player.velocity = (vx, vy)
        
        if symbol == pg.window.key.SPACE:
            shoot()
            
                    
    def on_key_release(symbol, mod):
        vx, vy = player.velocity
        if symbol == pg.window.key.W:
            vy = 0
        if symbol == pg.window.key.S:
            vy = 0
        if symbol == pg.window.key.A:
            vx = 0
        if symbol == pg.window.key.D:
            vx = 0
        player.velocity = (vx, vy)
        
    def on_mouse_motion(x, y, dx, dy):
        px, py = player.position
        lx, ly = x -px, y - py 
        player.angle = math.atan2(ly, lx)
            
    Window.instance.push_handlers(on_key_press, on_key_release, on_mouse_motion)
    
def map_gen(space):
    from pymunk.autogeometry import march_hard, march_soft
    img = [
    "xxxxxxxxxxxxxxx",
    "x             x",
    "x             x",
    "x xxxxx       x",
    "x x           x",
    "x x           x",
    "x             x",
    "xxxxxxxxxxxxxxx"]
    
    verts = []
    def segment_func(v0, v1):
        px = (v0 * 50) + pm.vec2d.Vec2d(100, 100)
        py = (v1 * 50) + pm.vec2d.Vec2d(100, 100)
        verts.extend([px, py])
        
    def sample_func(point):
        x = int(point.x)
        y = int(point.y)
        return 1.0 if img[y][x] == "x" else 0.0
        
    march_hard(pm.BB(0,0,14,7), 15, 8, .1, segment_func, sample_func)
    
    p = pm.Poly(space.static_body, verts, radius=50)
    space.add(p)    
        
def car(space):
    import pymunk
    from pymunk.vec2d import Vec2d
    space.gravity = 0, -9.8
    pos = Vec2d(300,200)

    wheel_color = 52,219,119
    shovel_color = 219,119,52
    mass = 100
    radius = 25
    moment = pymunk.moment_for_circle(mass, 20, radius)
    wheel1_b = pymunk.Body(mass, moment)
    wheel1_s = pymunk.Circle(wheel1_b, radius)
    wheel1_s.friction = 1.5
    wheel1_s.color = wheel_color
    space.add(wheel1_b, wheel1_s)

    mass = 100
    radius = 25
    moment = pymunk.moment_for_circle(mass, 20, radius)
    wheel2_b = pymunk.Body(mass, moment)
    wheel2_s = pymunk.Circle(wheel2_b, radius)
    wheel2_s.friction = 1.5
    wheel2_s.color = wheel_color
    space.add(wheel2_b, wheel2_s)

    mass = 100
    size = (50,30)
    moment = pymunk.moment_for_box(mass, size)
    chassi_b = pymunk.Body(mass, moment)
    chassi_s = pymunk.Poly.create_box(chassi_b, size)
    space.add(chassi_b, chassi_s)

    vs = [(0,0),(25,-45),(0,-45)]
    shovel_s = pymunk.Poly(chassi_b, vs, transform = pymunk.Transform(tx=85))
    shovel_s.friction = 0.5
    shovel_s.color = shovel_color
    space.add(shovel_s)

    wheel1_b.position = pos - (55,0)
    wheel2_b.position = pos + (55,0)
    chassi_b.position = pos + (0,25)

    space.add(
        pymunk.PinJoint(wheel1_b, chassi_b, (0,0), (-25,-15)),
        pymunk.PinJoint(wheel1_b, chassi_b, (0,0), (-25, 15)),
        pymunk.PinJoint(wheel2_b, chassi_b, (0,0), (25,-15)),
        pymunk.PinJoint(wheel2_b, chassi_b, (0,0), (25, 15))
        )
    
    speed = 4
    space.add(
        pymunk.SimpleMotor(wheel1_b, chassi_b, speed),
        pymunk.SimpleMotor(wheel2_b, chassi_b, speed))
        
    floor = pymunk.Segment(space.static_body, (-100,100),(1000,100),5)
    floor.friction = 1.0
    space.add(floor)
        


class Sandbox:
    
    def __init__(self):
        self.space = pm.Space()
        
        # Simple gravity/roll physics test
        # test(space)
        
        # Player movement
        # -- 8-dir move, look at mouse, bounding walls
        # player_movement(self.space)
        
        # Projectile shooting
        # -- Player movement, projectile shooting
        # projectiles(self.space)
        
        # Map Creation
        map_gen(self.space)
        
        # Car
        # car(self.space)
        
    def on_draw(self):
        Window.instance.clear()
        pg.gl.glClearColor(.2, .3, .3, 1)

        options = putils.DrawOptions()
        self.space.debug_draw(options)        
        
    def on_update(self, dt):
        for _ in it.repeat(None, 10):
            self.space.step(dt)
            

class Window(pg.window.Window):
    
    # -- singleton
    instance = None
    def __new__(cls, *args, **kwargs):
        if Window.instance is None:
            Window.instance = object.__new__(cls)
        return Window.instance
        
    def __init__(self, *args, **kwargs):
        pg.window.Window.__init__(self, *args, **kwargs)

def main():
    window = Window(1000, 600, "Physics Sandbox")
    
    sandbox = Sandbox()
    window.push_handlers(sandbox)
    pg.clock.schedule_interval(sandbox.on_update, 1/60.0)
    pg.app.run()
    
if __name__ == '__main__':
    main()
