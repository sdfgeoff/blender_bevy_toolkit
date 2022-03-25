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
from blender_bevy_toolkit.rust_types import F32, Bool, RgbaLinear, Map, Enum, EnumValue

logger = logging.getLogger(__name__)


@register_component
class DirectionalLight(ComponentBase):
    @staticmethod
    def encode(config, obj):
        assert DirectionalLight.is_present(obj)

        return Map(
            type="bevy_pbr::light::DirectionalLight",
            struct=Map(
                color=RgbaLinear(obj.data.color),
                illuminance=F32(obj.data.energy),
                shadows_enabled=Bool(obj.data.use_shadow),
                shadow_projection=Map(
                    type="bevy_render::camera::projection::OrthographicProjection",
                    struct=Map(
                        left=F32(obj.bevy_directional_light_properties.left),
                        right=F32(obj.bevy_directional_light_properties.right),
                        bottom=F32(obj.bevy_directional_light_properties.bottom),
                        top=F32(obj.bevy_directional_light_properties.top),
                        near=F32(obj.bevy_directional_light_properties.near),
                        far=F32(obj.bevy_directional_light_properties.far),
                        window_origin=Enum(
                            "bevy_render::camera::projection::WindowOrigin",
                            EnumValue("Center"),
                        ),
                        scaling_mode=Enum(
                            "bevy_render::camera::projection::ScalingMode",
                            EnumValue("FixedVertical"),
                        ),
                        scale=F32(obj.bevy_directional_light_properties.scale),
                        depth_calculation=Enum(
                            "bevy_render::camera::camera::DepthCalculation",
                            EnumValue("Distance"),
                        ),
                    ),
                ),
                shadow_depth_bias=F32(obj.data.shadow_buffer_bias),
                shadow_normal_bias=F32(
                    obj.bevy_directional_light_properties.shadow_normal_bias
                ),
            ),
        )

    @staticmethod
    def can_add(obj):
        False

    @staticmethod
    def is_present(obj):
        return obj.type == "LIGHT" and obj.data.type == "SUN"

    @staticmethod
    def register():
        bpy.utils.register_class(DirectionalLightPanel)
        bpy.utils.register_class(DirectionalLightProperties)
        bpy.types.Object.bevy_directional_light_properties = bpy.props.PointerProperty(
            type=DirectionalLightProperties
        )

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(DirectionalLightPanel)
        bpy.utils.unregister_class(DirectionalLightProperties)
        del bpy.types.Object.bevy_directional_light_properties


class DirectionalLightPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_directional_light_properties"
    bl_label = "BevyDirectionalLight"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return DirectionalLight.is_present(context.object)

    @staticmethod
    def draw(self, context):
        row = self.layout.row()
        row.label(text="Provider of directional illumination")

        row = self.layout.row()
        row.prop(context.object.data, "color")
        row = self.layout.row()
        row.prop(context.object.data, "energy", text="Illuminance")
        row = self.layout.row()
        row.prop(context.object.data, "use_shadow", text="Enable Shadow")

        shadow_enabled = context.object.data.use_shadow
        row = self.layout.row()
        row.active = shadow_enabled
        row.prop(context.object.data, "shadow_buffer_bias")  # Bevy Depth Bias
        row = self.layout.row()
        row.active = shadow_enabled
        row.prop(context.object.bevy_directional_light_properties, "shadow_normal_bias")

        box = self.layout.box()
        box.active = shadow_enabled
        box.label(text="Shadow Projection")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "left")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "right")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "bottom")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "top")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "near")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "far")
        row = box.row()
        row.prop(context.object.bevy_directional_light_properties, "scale")


class DirectionalLightProperties(bpy.types.PropertyGroup):
    shadow_normal_bias: bpy.props.FloatProperty(name="Shadow Normal Bias", default=0.0)

    # Shadow Orthographic Projection properties
    left: bpy.props.FloatProperty(name="left", default=-100.0)
    right: bpy.props.FloatProperty(name="right", default=100.0)
    bottom: bpy.props.FloatProperty(name="bottom", default=-100.0)
    top: bpy.props.FloatProperty(name="top", default=100.0)
    near: bpy.props.FloatProperty(name="near", default=-100.0)
    far: bpy.props.FloatProperty(name="far", default=100.0)
    scale: bpy.props.FloatProperty(name="scale", default=1.0)
    # Missing window_origin, scaling_mode, depth_calculation


register_component(
    component_from_def(
        ComponentDefinition(
            name="VisibleEntities",
            description="AUTO: Used by directional light sources",
            id="visible_entities",
            struct="bevy_render::view::visibility::VisibleEntities",
            fields=[],
        ),
        is_present_function=DirectionalLight.is_present,
    )
)

register_component(
    component_from_def(
        ComponentDefinition(
            name="Frusta",
            description="AUTO: Used by directional light sources",
            id="frustra",
            struct="bevy_render::primitives::Frustum",
            fields=[],
        ),
        is_present_function=DirectionalLight.is_present,
    )
)
