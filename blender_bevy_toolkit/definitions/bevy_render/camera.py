import bpy
from blender_bevy_toolkit.component_base import (
    ComponentRepresentation,
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit.component_constructor import (
    ComponentDefinition,
    component_from_def,
)


import logging
from blender_bevy_toolkit import jdict, utils

logger = logging.getLogger(__name__)


@register_component
class Camera(ComponentBase):
    @staticmethod
    def encode(config, obj):
        """
        {
            "type": "bevy_render::camera::camera::Camera",
            "struct": {
            "projection_matrix": {
                "type": "glam::mat4::Mat4",
                "value": (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
            },
            "name": {
                "type": "core::option::Option<alloc::string::String>",
                "value": Some("camera_3d"),
            },
            "near": {
                "type": "f32",
                "value": 0.1,
            },
            "far": {
                "type": "f32",
                "value": 1000.0,
            },
            },
        },
        """
        return ComponentRepresentation(
            "bevy_render::camera::camera::Camera",
            {
                # "projection_matrix", # Auto-computed from projection component (I hope)
                "near": utils.F32(obj.data.clip_start),
                "far": utils.F32(obj.data.clip_end),
                "name": utils.Option("alloc::string::String", "camera_3d"),
            },
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        bpy.utils.register_class(CameraPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(CameraPanel)

    @staticmethod
    def can_add(obj):
        return False


class CameraPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_camera_properties"
    bl_label = "BevyCamera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return Camera.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Renders the scene")

        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")
        row = self.layout.row()
        row.prop(context.object.data, "clip_end", text="Far")


register_component(
    component_from_def(
        ComponentDefinition(
            name="VisibleEntities",
            description="AUTO: Used by camera",
            id="camera_visible_entities",
            struct="bevy_render::view::visibility::VisibleEntities",
            fields=[],
        ),
        is_present_function=Camera.is_present,
    )
)

register_component(
    component_from_def(
        ComponentDefinition(
            name="Frustum",
            description="AUTO: Used by camera",
            id="camera_frustrum",
            struct="bevy_render::primitives::Frustum",
            fields=[],
        ),
        is_present_function=Camera.is_present,
    )
)


@register_component
class PerspectiveProjection(ComponentBase):
    """
    Controls for Perspective projection matrix
    """

    @staticmethod
    def encode(config, obj):
        return ComponentRepresentation(
            "bevy_render::camera::projection::PerspectiveProjection",
            {
                "near": utils.F32(obj.data.clip_start),
                "far": utils.F32(obj.data.clip_end),
                "fov": utils.F32(obj.data.angle),
            },
        )

    @staticmethod
    def is_present(obj):
        return Camera.is_present(obj) and obj.data.type == "PERSP"

    @staticmethod
    def register():
        bpy.utils.register_class(PerspectiveProjectionPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(PerspectiveProjectionPanel)

    @staticmethod
    def can_add(obj):
        return False


class PerspectiveProjectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_projection_properties"
    bl_label = "BevyPerspectiveProjectionMatrix"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return PerspectiveProjection.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Computes a projection matrix from a set of properties")

        row = self.layout.row()
        row.prop(context.object.data, "angle", text="FOV")
        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")
        row = self.layout.row()
        row.prop(context.object.data, "clip_end", text="Far")

        if context.object.data.sensor_fit != "VERTICAL":
            row = self.layout.row()
            row.label(text="Camera sensor fit should be vertical:", icon="ERROR")
            row = self.layout.row()
            row.prop(context.object.data, "sensor_fit")


@register_component
class OrthographicProjection(ComponentBase):
    """
    Controls for Orthographic Projection Matrix

        "struct": {
          "left": {
            "type": "f32",
            "value": -1.0,
          },
          "right": {
            "type": "f32",
            "value": 1.0,
          },
          "bottom": {
            "type": "f32",
            "value": -1.0,
          },
          "top": {
            "type": "f32",
            "value": 1.0,
          },
          "near": {
            "type": "f32",
            "value": 0.0,
          },
          "far": {
            "type": "f32",
            "value": 1000.0,
          },
          "window_origin": {
            "type": "bevy_render::camera::projection::WindowOrigin",
            "value": Center,
          },
          "scaling_mode": {
            "type": "bevy_render::camera::projection::ScalingMode",
            "value": FixedVertical,
          },
          "scale": {
            "type": "f32",
            "value": 1.0,
          },
          "depth_calculation": {
            "type": "bevy_render::camera::camera::DepthCalculation",
            "value": Distance,
          },
    """

    @staticmethod
    def encode(config, obj):
        return ComponentRepresentation(
            "bevy_render::camera::projection::OrthographicProjection",
            {
                "left": utils.F32(-1.0),
                "right": utils.F32(1.0),
                "bottom": utils.F32(-1.0),
                "top": utils.F32(1.0),
                "near": utils.F32(obj.data.clip_start),
                "far": utils.F32(obj.data.clip_end),
                "window_origin": utils.Enum(
                    "bevy_render::camera::projection::WindowOrigin",
                    utils.EnumValue("Center"),
                ),
                "scaling_mode": utils.Enum(
                    "bevy_render::camera::projection::ScalingMode",
                    utils.EnumValue("FixedVertical"),
                ),
                "scale": utils.F32(obj.data.ortho_scale / 2.0),
                "depth_calculation": utils.Enum(
                    "bevy_render::camera::camera::DepthCalculation",
                    utils.EnumValue("Distance"),
                ),
            },
        )

    @staticmethod
    def is_present(obj):
        return Camera.is_present(obj) and obj.data.type == "ORTHO"

    @staticmethod
    def register():
        bpy.utils.register_class(OrthographicProjectionPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(OrthographicProjectionPanel)

    @staticmethod
    def can_add(obj):
        return False


class OrthographicProjectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_orthographic_projection_properties"
    bl_label = "BevyOrthographicProjectionMatrix"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return OrthographicProjection.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Computes a projection matrix from a set of properties")

        row = self.layout.row()
        row.prop(context.object.data, "ortho_scale", text="Scale")
        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")
        row = self.layout.row()
        row.prop(context.object.data, "clip_end", text="Far")

        if context.object.data.sensor_fit != "VERTICAL":
            # Technically not required, but then I'd need to implement both enum options
            # in the OrthographicProjection.encode() function
            row = self.layout.row()
            row.label(text="Camera sensor fit should be vertical:", icon="ERROR")
            row = self.layout.row()
            row.prop(context.object.data, "sensor_fit")
