from blender_bevy_toolkit.component_base import (
    ComponentRepresentation,
    register_component,
    ComponentBase,
)


@register_component
class Parent(ComponentBase):
    def encode(config, obj):
        """Returns a ComponentRepresentation representing this component"""

        collection_objs = list(config["scene"].objects)

        parent_id = collection_objs.index(obj.parent)

        return ComponentRepresentation(
            "bevy_transform::components::parent::Parent",
            [
                {
                    "type": "bevy_ecs::entity::Entity",
                    "value": parent_id,
                },
            ],
            type_override="tuple_struct",
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
