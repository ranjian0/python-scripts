# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Catmull-Clark Smoothing",
    "author": "Rafael Navega 2017",
    "description": "Applies Catmull-Clark surface smoothing to the selected vertices.",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "View3D > Specials > Catmull-Clark Smooth ",
    "warning": "",
    "category": "Mesh",
}


import bpy
from bpy.props import (FloatProperty, IntProperty)
import bmesh
from mathutils import Vector

def calc_median(*args):
    return sum(args, Vector()) / len(args)

def smooth_mesh(context, factor):
    source = context.active_object.data

    bm = bmesh.from_edit_mesh(source)

    #Collect all selected vertices,

    selected_vertices = list(filter(lambda v: v.select, bm.verts))

    #If no vertices are selected, use all.

    if len(selected_vertices) == 0:
        selected_vertices = bm.verts

    #Compute the "face points" of all faces connected to selected vertices, indexed by their BMesh indexes.

    face_points = [None] * len(bm.faces)

    for vertex in selected_vertices:
        for face in vertex.link_faces:
            face_points[face.index] = face.calc_center_median()

    #Compute the "edge midpoints" of all edges connected to the selected vertices, indexed by their BMesh indexes.

    edge_midpoints = [None] * len(bm.edges)

    for vertex in selected_vertices:
        for edge in vertex.link_edges:
            if edge_midpoints[edge.index] == None:
                edge_midpoints[edge.index] = calc_median(edge.verts[0].co, edge.verts[1].co)

    #Go through each vertex and compute their smoothed position.

    for vertex in selected_vertices:
        if not vertex.is_boundary:
            n = len(vertex.link_faces)
            P = vertex.co
            F = sum((face_points[face.index] for face in vertex.link_faces), Vector()) / n
            R = sum((edge_midpoints[edge.index] for edge in vertex.link_edges), Vector()) / n
            new_co = (F + 2*R + (n - 3)*P) / n
        else:
            boundary_edges = filter(lambda e: e.is_boundary, vertex.link_edges)
            boundary_midpoints = map(lambda e: edge_midpoints[e.index], boundary_edges)
            new_co = 0.5 * vertex.co + 0.25 * sum(boundary_midpoints, Vector())

        vertex.co = vertex.co + factor*(new_co - vertex.co)

    #Update the user mesh.

    bm.normal_update()
    bmesh.update_edit_mesh(source, tessface=True, destructive=False)

class CCSmooth(bpy.types.Operator):
    bl_idname = 'mesh.catmull_clark_smooth'
    bl_label = 'Catmull-Clark Smooth'
    bl_options = {'REGISTER', 'UNDO'}

    smooth_amount = FloatProperty(name="Smooth Amount",
                description="Amount of smoothing to apply", default=0.5, min=0, max=1, step=0.5, precision=3)
    iteration_amount = IntProperty(name="Iterations",
                description="Number of times to repeat the smoothing", default=1, min=1, max=40, step=1)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.mode == 'EDIT' and obj.type == 'MESH')

    def execute(self, context):
        for i in range(self.properties.iteration_amount):
            smooth_mesh(context, self.properties.smooth_amount)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CCSmooth.bl_idname, text="C-C Smooth")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func) # Specials (W) menu.

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
    register()