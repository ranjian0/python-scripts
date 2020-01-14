import pyglet as pg 

class Signal(pg.event.EventDispatcher):
    
    def __init__(self, name):
        super().__init__()
        self._name = name
        Signal.register_event_type(name)
        
    def emit(self, *args):
        self.dispatch_event(self._name, *args)
        
    def connect(self, meth):
        kw = {self._name : meth}
        self.push_handlers(**kw)
        
def do_clicked(*args):
    print(*args)
    print("Did clicked")

clicked = Signal("button_clicked")
clicked.connect(do_clicked)
clicked.emit('hello')

