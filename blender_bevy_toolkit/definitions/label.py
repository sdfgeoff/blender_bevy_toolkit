from blender_bevy_toolkit.component_base import (
    ComponentRepresentation,
    register_component,
    ComponentBase,
)


@register_component
class Label(ComponentBase):
    def encode(config, obj):
        """Returns a ComponentRepresentation representing this component"""
        return ComponentRepresentation(
            "blender_bevy_toolkit::blend_label::BlendLabel", {"name": obj.name}
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
