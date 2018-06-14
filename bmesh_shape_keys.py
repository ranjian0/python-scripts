import bpy
import bmesh
import mathutils


def main():
    """
    Example of bmesh and shape keys
    """
    # Add basis shape
    bpy.ops.object.shape_key_add(from_mix=False)

    # Get the active mesh
    me = bpy.context.object.data

    # Get a BMesh representation
    bm = bmesh.new() 
    bm.from_mesh(me)

    # Get basis shape key
    lay_shape_basis = bm.verts.layers.shape['Basis']

    # Create new shape key
    lay_my_shape = bm.verts.layers.shape.new('MyShape')

    # Modify new shape key
    for vert in bm.verts:
        vert[lay_my_shape] = vert.co + mathutils.Vector((1.0, 0.0, 0.0))

    # Frite bmesh back to mesh
    bm.to_mesh(me)

if __name__ == '__main__':
    main()