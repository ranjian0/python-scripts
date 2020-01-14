import glfw
import OpenGL.GL as gl


def main():
    if not glfw.init():
        raise ValueError("Failed to initialize glfw")

    glfw.window_hint(glfw.CONTEXT_CREATION_API, glfw.NATIVE_CONTEXT_API)
    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.RESIZABLE, True)
    glfw.window_hint(glfw.DOUBLEBUFFER, True)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(1260, 720, "Python GL", None, None)
    if not window:
        glfw.terminate()
        raise ValueError("Failed to create window")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_event_callback)
    glfw.set_cursor_pos_callback(window, mouse_event_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_window_size_callback(window, window_resize_callback)

    while not glfw.window_should_close(window):

        on_input(window)
        on_draw()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


def key_event_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def mouse_event_callback(window, xpos, ypos):
    pass


def mouse_button_callback(window, button, action, mods):
    pass


def window_resize_callback(window, width, height):
    pass


def on_draw():
    gl.glClearColor(.2, .3, .3, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)


def on_input(window):
    pass


if __name__ == '__main__':
    main()
