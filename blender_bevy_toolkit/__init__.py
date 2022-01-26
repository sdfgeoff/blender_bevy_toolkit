import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from utils import jdict

logger = logging.getLogger(__name__)


import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper

from . import components
from . import operators
from . import component_base
from . import export

bl_info = {
    "name": "Bevy Game Engine Toolkit",
    "blender": (2, 90, 0),
    "category": "Game",
}


class BevyComponentsPanel(bpy.types.Panel):
    """The panel in which buttons that add/remove components are shown"""

    bl_idname = "OBJECT_PT_bevy_components_panel"
    bl_label = "Bevy Components"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, context):
        row = self.layout.row()
        row.operator("object.add_bevy_component")
        row.operator("object.remove_bevy_component")


def register():
    logger.info(jdict(event="registering_bevy_addon", state="start"))
    bpy.utils.register_class(BevyComponentsPanel)
    bpy.utils.register_class(operators.RemoveBevyComponent)
    bpy.utils.register_class(operators.AddBevyComponent)
    bpy.utils.register_class(ExportBevy)

    bpy.app.handlers.load_post.append(load_handler)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    logger.info(jdict(event="registering_bevy_addon", state="end"))


def unregister():
    logger.info(jdict(event="unregistering_bevy_addon", state="start"))
    bpy.utils.unregister_class(BevyComponentsPanel)
    bpy.utils.unregister_class(operators.RemoveBevyComponent)
    bpy.utils.unregister_class(operators.AddBevyComponent)
    bpy.utils.unregister_class(ExportBevy)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    bpy.app.handlers.load_post.remove(load_handler)

    for component in component_base.COMPONENTS:
        logger.info(jdict(event="unregistering_component", component=str(component)))
        component.unregister()
    logger.info(jdict(event="unregistering_bevy_addon", state="end"))


@persistent
def load_handler(_dummy):
    """Scan the folder of the blend file for components to add"""
    for component in component_base.COMPONENTS:
        component.unregister()

    components.generate_component_list()
    operators.update_all_component_list()

    for component in component_base.COMPONENTS:
        logger.info(jdict(event="registering_component", component=str(component)))
        component.register()


def menu_func(self, context):
    """Add export operation to the menu"""
    self.layout.operator(ExportBevy.bl_idname, text="Bevy Engine (.scn)")


class ExportBevy(bpy.types.Operator, ExportHelper):
    """Selection to Godot"""

    bl_idname = "export_bevy.scn"
    bl_label = "Export to Bevy"
    bl_options = {"PRESET"}

    filename_ext = ".scn"
    filter_glob: bpy.props.StringProperty(default="*.scn", options={"HIDDEN"})

    def execute(self, context):
        """Begin the export"""

        if not self.filepath:
            raise Exception("filepath not set")

        do_export(
            {
                "output_filepath": self.filepath,
                "mesh_output_folder": "meshes",
                "make_duplicates_real": False,
            }
        )

        return {"FINISHED"}


def do_export(config):
    export.export_all(config)
