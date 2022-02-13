import bpy
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit.component_constructor import (
    ComponentDefinition,
    component_from_def,
)


import logging
from blender_bevy_toolkit.utils import jdict
from blender_bevy_toolkit.rust_types import F32, Option, Enum, EnumValue, Map, Bool

logger = logging.getLogger(__name__)


@register_component
class Visibility(ComponentBase):
    """
    Controls for Orthographic Projection Matrix

    {
        "type": "bevy_render::view::visibility::Visibility",
        "struct": {
          "is_visible": {
            "type": "bool",
            "value": true,
          },
        },
      },


    """

    @staticmethod
    def encode(config, obj):
        return Map(
            type="bevy_render::view::visibility::Visibility",
            struct=Map(
                is_visible=Bool(not obj.hide_render),
            ),
        )

    @staticmethod
    def is_present(obj):
        return obj.type in [
            "MESH",
        ]

    @staticmethod
    def register():
        bpy.utils.register_class(VisibilityPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(VisibilityPanel)

    @staticmethod
    def can_add(obj):
        return False


class VisibilityPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_visibility_properties"
    bl_label = "BevyVisibiliity"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return Visibility.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="AUTO: Part of PbrBundle")

        row = self.layout.row()
        row.prop(
            context.object.data, "hide_viewport", text="Visible", invert_checkbox=True
        )


@register_component
class ComputedVisibility(ComponentBase):
    """
    Controls for Orthographic Projection Matrix

    {
        "type": "bevy_render::view::visibility::ComputedVisibility",
        "struct": {
          "is_visible": {
            "type": "bool",
            "value": true,
          },
        },
      },

    """

    @staticmethod
    def encode(config, obj):
        return Map(
            type="bevy_render::view::visibility::ComputedVisibility",
            struct=Map(
                is_visible=Bool(not obj.hide_render),
            ),
        )

    @staticmethod
    def is_present(obj):
        return Visibility.is_present(obj)

    @staticmethod
    def register():
        bpy.utils.register_class(ComputedVisibilityPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(ComputedVisibilityPanel)

    @staticmethod
    def can_add(obj):
        return False


class ComputedVisibilityPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_computed_visibility_properties"
    bl_label = "BevyComputedVisibiliity"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return ComputedVisibility.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="AUTO: Part of PbrBundle")

        row = self.layout.row()
        row.prop(
            context.object.data, "hide_viewport", text="Visible", invert_checkbox=True
        )
