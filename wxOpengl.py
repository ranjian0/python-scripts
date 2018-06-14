"""
A simple opengl application
    Purpose:
        - Create reusable app framework for wx and opengl
        - Implement basic opengl features
        - Showcase simple use opengl api

"""

import wx
import sys
from wx.glcanvas import *
from OpenGL.GL import *
from OpenGL.GLU import *


def test_draw():
    """
    Draw some points on the GL Viewport
    """

    glPointSize(5.0)
    glColor3f(1, 0, 0)

    glBegin(GL_POINTS)
    glVertex3f(.5, .5, 0)
    glEnd()


class Viewport(GLCanvas):
    ''' Implements opengl scene '''

    def __init__(self, parent, attribs=None, id=wx.ID_ANY):
        """
        Initialize opengl viewport
        """
        if not attribs:
            attribs = [WX_GL_RGBA, WX_GL_DOUBLEBUFFER, WX_GL_DEPTH_SIZE, 24]
        GLCanvas.__init__(self, parent, id, attribList=attribs)

        self.init_variables()
        self.bind_events()

    def log_opengl_info(self):
        """
        Print to the console information about opengl
        """
        print("OPENGL VERSION: ", glGetString(GL_VERSION))
        print("OPENGL VENDOR: ", glGetString(GL_VENDOR))
        print("OPENGL RENDERER: ", glGetString(GL_RENDERER))
        print("OPENGL GLSL VERSION: ", glGetString(GL_SHADING_LANGUAGE_VERSION))

    def init_variables(self):
        """
        Initialize varianbles
        """
        self.init = False
        self.width, self.height = 0, 0
        self.size = None

        parent = self.GetParent()
        self.parentsize = parent.GetSize()

    def bind_events(self):
        """
        Bind functions to all events
        """

        # Display Event handlers
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # Keyboard Event handler
        self.Bind(wx.EVT_KEY_DOWN, self.key_down)
        self.Bind(wx.EVT_KEY_UP, self.key_up)

        # Mouse Event Handlers
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_mouse_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_mouse_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_mouse_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_middle_mouse_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_middle_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)

    #   Keyboard Events
    #   ===============
    def key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.GetParent().Close()

        self.Refresh(True)

    def key_up(self, event):
        pass

    # Mouse Events
    # ============
    def on_scroll(self, event):
        delta = 0
        if event.GetWheelRotation() > 0:
            delta = 1
        else:
            delta = -1
        self.Refresh(True)

    def on_left_mouse_down(self, evt):
        self.SetFocus()
        self.CaptureMouse()

        x, y = evt.GetPosition()

    def on_left_mouse_up(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse()

    def on_middle_mouse_down(self, evt):
        self.SetFocus()
        self.CaptureMouse()

        x, y = evt.GetPosition()

    def on_middle_mouse_up(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse()

        x, y = evt.GetPosition()

    def on_right_mouse_down(self, evt):
        self.SetFocus()
        self.CaptureMouse()

        x, y = evt.GetPosition()

    def on_right_mouse_up(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse()

    def on_mouse_motion(self, evt):
        x, y = evt.GetPosition()
        self.Refresh(False)

    #   WxCanvas Events
    #   ===============
    def on_paint(self, event):

        # Set the OpenGL context
        dc = wx.PaintDC(self)
        context = GLContext(self)
        self.SetCurrent(context)

        # Initialize OpenGL if not initialized
        if not self.init:
            self.init_gl()

        self.clear()
        self.set_projection()
        self.set_viewpoint()

        # Do Draw
        self.on_draw()

        # Refresh the current buffer with the one in memory
        self.SwapBuffers()

    def on_size(self, event):
        # Note these are ints, not floats, for glViewport
        self.width, self.height = self.GetSize()

    def on_erase_background(self, event):
        pass

    #   OpenGL Misc Functions
    #   ================
    def init_gl(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)
        self.init = True

        self.log_opengl_info()

    def clear(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        try:
            gluPerspective(60.0, float(self.width)/float(self.height),
                           0.1, 1000.0)
        except ZeroDivisionError:
            print('Error Occured')
        glMatrixMode(GL_MODELVIEW)

    def set_viewpoint(self):
        glLoadIdentity()
        gluLookAt(5.0, 15.0, -30.0,
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)

    def on_draw(self):

        glPushMatrix()
        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        w = max(w, 1.0)
        h = max(h, 1.0)

        glPopMatrix()

        test_draw()


class MainFrame(wx.Frame):
    """
    Create main application window
    """

    def __init__(self, parent, caption):
        """
        Initialize the main application window
        """
        wx.Frame.__init__(self, parent, wx.ID_ANY, caption)

        self.sizer = wx.BoxSizer()
        self.viewport = Viewport(self)
        self.sizer.Add(self.viewport, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(self.sizer)
        self.Show()


def main(argv):
    """
    Driver function for application
    """

    app = wx.App()
    MainFrame(None, "Simple WxOpenGL App")
    app.MainLoop()


if __name__ == '__main__':
    main(sys.argv)
