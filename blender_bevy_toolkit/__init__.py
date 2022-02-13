"""
Bevy is a game engine written in RUST, but it crrently lacks any sort of
scene editor. Blender is a 3D graphics program that seems like it would
be a good fit. This exporter converts from a blender file into a .scn file
that can be loaded into bevy.
"""
import os
import sys
import logging

import bpy
from bpy.app.handlers import persistent  # pylint: disable=E0401
from bpy_extras.io_utils import ExportHelper


from .utils import jdict
from . import components
from . import operators
from . import component_base
from . import export

logger = logging.getLogger(__name__)

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

    def draw(self, _context):
        """Create the UI for the panel"""
        row = self.layout.row()
        row.operator("object.add_bevy_component")
        row.operator("object.remove_bevy_component")


def register():
    """Blender needs to know about all our classes and UI panels
    so that it can draw/store things"""
    logger.info(jdict(event="registering_bevy_addon", state="start"))
    bpy.utils.register_class(BevyComponentsPanel)
    bpy.utils.register_class(operators.RemoveBevyComponent)
    bpy.utils.register_class(operators.AddBevyComponent)
    bpy.utils.register_class(ExportBevy)

    bpy.app.handlers.load_post.append(load_handler)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    logger.info(jdict(event="registering_bevy_addon", state="end"))


def unregister():
    """When closing blender or uninstalling the addon we should leave
    things nice and clean...."""
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


def menu_func(self, _context):
    """Add export operation to the menu"""
    self.layout.operator(ExportBevy.bl_idname, text="Bevy Engine (.scn)")


class ExportBevy(bpy.types.Operator, ExportHelper):
    """Selection to Godot"""

    bl_idname = "export_bevy.scn"
    bl_label = "Export to Bevy"
    bl_options = {"PRESET"}

    filename_ext = ".scn"
    filter_glob: bpy.props.StringProperty(default="*.scn", options={"HIDDEN"})

    def execute(self, _context):
        """Begin the export"""

        if not self.filepath:
            raise Exception("filepath not set")

        do_export(
            {
                "output_filepath": self.filepath,
                "mesh_output_folder": "meshes",
                "material_output_folder": "materials",
                "make_duplicates_real": False,
            }
        )

        return {"FINISHED"}


def do_export(config):
    """Start the export. This is a global function to ensure it can be called
    both from the operator and from external scripts"""
    export.export_all(config)
