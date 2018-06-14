import bpy
import time
import random
import numpy as np

def make_obj():
    if bpy.context.object:
        bpy.ops.object.delete(use_global=False)

    bpy.ops.mesh.primitive_plane_add(radius=10, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.subdivide(smoothness=0)
    bpy.ops.mesh.subdivide(number_cuts=50, smoothness=0)
    bpy.ops.object.editmode_toggle()
        

def displace_sine(_):
    obj = bpy.context.object
    me = obj.data
    
    # Get vert data
    vcount = len(me.vertices)
    block = np.zeros(vcount * 3)
    me.vertices.foreach_get('co', block)
    block.shape = (vcount, 3)
    
    # -- displace with sine wave
    speed = time.time() * 3
    phase = np.ones(vcount) + speed
    
    random.seed(time.time())
    amp = random.randint(1, 5)/10 #(int(time.time()) % 10) / 10#np.random.random()
    
    x_sine = amp * np.sin(block[:, 0] + phase) + np.cos(block[:,1] + phase)
    block[:, 2] = x_sine
    
    # Set vert data back
    me.vertices.foreach_set('co', block.ravel())
    me.update()
    
#make_obj()
#displace_sine()

if bpy.app.handlers.scene_update_pre:
    del bpy.app.handlers.scene_update_pre[-1]

bpy.app.handlers.scene_update_pre.append(displace_sine)

