from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit import rust_types


@register_component
class Label(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component"""
        return rust_types.Map(
            type="blender_bevy_toolkit::blend_label::BlendLabel", 
            struct=rust_types.Map(
                name=rust_types.Str(obj.name)
            )
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return hasattr(obj, "name")

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
