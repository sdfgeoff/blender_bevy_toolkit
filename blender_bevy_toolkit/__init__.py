import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import bpy
from bpy.app.handlers import persistent

from . import components
from . import operators
from . import component_base

bl_info = {
    "name": "Bevy Game Engine Toolkit",
    "blender": (2, 90, 0),
    "category": "Game",
}



class BevyComponentsPanel(bpy.types.Panel):
    """ The panel in which buttons that add/remove components are shown """
    bl_idname = "OBJECT_PT_bevy_components_panel"
    bl_label = "Bevy Components"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"


    def draw(self, context):
        row = self.layout.row()
        row.operator('object.add_bevy_component')
        row.operator('object.remove_bevy_component')


def register():
    bpy.utils.register_class(BevyComponentsPanel)
    bpy.utils.register_class(operators.RemoveBevyComponent)
    bpy.utils.register_class(operators.AddBevyComponent)
    
    bpy.app.handlers.load_post.append(load_handler)
    
    
def unregister():
    bpy.utils.unregister_class(BevyComponentsPanel)
    bpy.utils.unregister_class(operators.RemoveBevyComponent)
    bpy.utils.unregister_class(operators.AddBevyComponent)
    
    bpy.app.handlers.load_post.remove(load_handler)
    
    for component in component_base.COMPONENTS:
        component.unregister()


@persistent
def load_handler(dummy):
    """ Scan the folder of the blend file for components to add """
    for component in component_base.COMPONENTS:
        component.unregister()
    
    components.generate_component_list()
    operators.update_all_component_list()
    
    for component in component_base.COMPONENTS:
        component.register()
    
    

