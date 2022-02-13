from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit import rust_types


@register_component
class Parent(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component"""

        collection_objs = list(config["scene"].objects)

        parent_id = collection_objs.index(obj.parent)

        return rust_types.Map(
            type="bevy_transform::components::parent::Parent",
            tuple_struct=rust_types.List(
                rust_types.Entity(parent_id),
            ),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return obj.parent is not None

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
