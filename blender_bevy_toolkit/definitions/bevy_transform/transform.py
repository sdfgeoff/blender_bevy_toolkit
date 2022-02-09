from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
    rust_types,
)


@register_component
class Transform(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component

        {
            "type": "bevy_transform::components::transform::Transform",
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

        if obj.parent is None:
            transform = obj.matrix_world
        else:
            transform = obj.matrix_local

        position, rotation, scale = transform.decompose()
        return rust_types.Map(
            type="bevy_transform::components::transform::Transform",
            struct=rust_types.Map(
                translation=rust_types.Vec3(position),
                rotation=rust_types.Quat(rotation),
                scale=rust_types.Vec3(scale),
            ),
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
