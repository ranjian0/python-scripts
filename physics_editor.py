import pyglet as pg
import pymunk as pm
from enum import Enum
from pymunk import pyglet_util as putils

instructions = """
Physics Editor:

Options:
    press G to set gravity; [scroll mousewheel to set value]
    press C to create a new circle shape; [LMB to add circle, mousewheel to set radius]
    press B to create a new  box shape; [LMB to set top-left, drag-release to set bottom-right]
    press S to create static segment shape
    press ENTER to confirm shape
    
    press Space to toggle simulation (ON/OFF)
    press 
"""

COMMAND_MODES = [
    ""
]

class Editor:
    
    def __init__(self, _window):
        self._window = _window
        self.physics_space = pm.Space()
        pg.clock.schedule_interval(self.on_update, 1./60)

        self.object = dict()
        self.COMMANDS = {
            pg.window.key.G : self.set_gravity,
            pg.window.key.C : self.add_circle_shape,
            pg.window.key.B : self.add_box_shape,
            pg.window.key.S : self.add_segment_shape
        }        
        

    def on_draw(self):
        self._window.clear()
        pg.gl.glClearColor(.2, .3, .3, 1)
        
        options = putils.DrawOptions()
        self.physics_space.debug_draw(options)        
        
    def on_update(self, dt):
        for _ in range(10):
            self.physics_space.step(1./60)
            
    def on_key_press(self, symbol, mod):
        command = self.COMMANDS.get(symbol, None)
        if command is not None:
            command()
    
    def on_key_release(self, symbol, mod):
        pass
            
    def on_mouse_press(self, x, y, button, mod):
        if button == pg.window.mouse.LEFT:
            if self.object['type'] == "Circle":
                self.object['body'].position = (x,y)
            elif self.object['type'] == "Segment":
                self.object['start'] = (x,y)

    def on_mouse_release(self, x, y, button, mod):
        pass
        
    def on_mouse_drag(self, x, y, dx, dy, button, mod):
        if button == pg.window.mouse.LEFT:
            if self.object['type'] == "Circle":
                vec = self.object['body'].position - pm.vec2d.Vec2d(x,y)
                self.physics_space.remove(self.object['shape'])
                del self.object['shape']
                
                self.object['shape'] = pm.Circle(self.object['body'], vec.length)
                self.physics_space.add(self.object['shape'])
            elif self.object['type'] == "Segment":
                a, b = self.object['start'], (x,y)
                self.physics_space.remove(self.object['shape'])
                del self.object['shape']
                self.object['shape'] = pm.Segment(self.object['body'], a, b, 5)
                self.physics_space.add(self.object['shape'])
                
        
    def on_mouse_scroll(self, x, y, sx, sy):
        pass
        
    def set_gravity(self):
        if self.physics_space.gravity.length == 0:
            self.physics_space.gravity = (0, -9.8)
        else:
            self.physics_space.gravity = (0, 0)
        
    def add_circle_shape(self):
        self.object.clear()
        self.object['body'] = pm.Body(1, 10)
        self.object['shape'] = pm.Circle(self.object['body'], 0.1)
        self.physics_space.add(*self.object.values())
        self.object['type'] = "Circle"
        print("Entered Circle")
        
    def add_box_shape(self):
        self.mode = "Shape"
        self.current_shape = "Box"
        
    def add_segment_shape(self):
        self.object.clear()
        self.object['type'] = "Segment"
        self.object['body'] = self.physics_space.static_body
        self.object['shape'] = pm.Segment(self.object['body'], (0,0),(0,0),5)
        self.physics_space.add(self.object['shape'])
        print("Entered Segment")
                
        
def main():
    window = pg.window.Window(600, 500, "PhysicsEditor", resizable=True)
    window.push_handlers(Editor(window))
    pg.app.run()
    return 0
    
if __name__ == '__main__':
    import sys
    sys.exit(main())
