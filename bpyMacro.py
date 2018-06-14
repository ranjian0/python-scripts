import bpy
from bpy.types import Operator, Macro


# Our finalizing operator, shall run after transform
class Finalize(Operator):
    bl_idname = "test.finalize"
    bl_label = "Finalize"

    def execute(self, context):
        print("DONE!")
        return {'FINISHED'}


# Macro operator to concatenate transform and our finalization
class Test(Macro):
    bl_idname = "TEST_OT_Test"
    bl_label = "Test"


# Note that we have to register classes first before populating
# the Macro operator    
bpy.utils.register_class(Finalize)
bpy.utils.register_class(Test)


# The important bit: populate the macro operator with a sequence
# of existing other operators
Test.define("transform.translate")
Test.define("test.finalize")
