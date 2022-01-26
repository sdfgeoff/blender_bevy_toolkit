from blender_bevy_toolkit.component_base import (
    ComponentRepresentation,
    register_component,
)


@register_component
class GlobalTransform:
    def encode(config, obj):
        """Returns a ComponentRepresentation representing this component

        {
            "type": "bevy_transform::components::transform::GlobalTransform",
            "struct": {
                "translation": {
                    "type": "glam::vec3::Vec3",
                    "value": (0.0, 0.0, 0.0),
                },
                "rotation": {
                    "type": "glam::quat::Quat",
                    "value": (0.0, 0.0, 0.0, 1.0),
                },
                "scale": {
                    "type": "glam::vec3::Vec3",
                    "value": (1.0, 1.0, 1.0),
                },
        }
        """

        transform = obj.matrix_world

        position, rotation, scale = transform.decompose()
        return ComponentRepresentation(
            "bevy_transform::components::global_transform::GlobalTransform",
            {
                "translation": position,
                "rotation": rotation,
                "scale": scale,
            },
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return hasattr(obj, "matrix_world")

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
