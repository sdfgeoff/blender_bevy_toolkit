""" Converts from blender objects into a scene description """
import os
import bpy
from . import utils, component_base


class Entity:
    """In an ECS, an entity is an opaque ID that is referenced by (or references)
    a set of components. This class represents an entity and as such ... contains
    a lit of components. The ID field should be unique in the scene"""

    def __init__(self, entity_id, comp):
        self.id = entity_id
        self.components = comp

    def to_str(self):
        """Convert into a ... string!"""
        return "(\n    entity: {},\n    components:{}\n)".format(
            utils.encode(self.id),
            utils.iterable_to_string(
                self.components, "[\n        ", "\n    ]", ",\n        "
            ),
        )


def export_entity(config, obj, entity_id):
    """Compile all the data about an object into an entity with components"""
    entity = Entity(entity_id, [])

    for component in component_base.COMPONENTS:
        if component.is_present(obj):
            new_component = component.encode(config, obj)
            assert isinstance(
                new_component, component_base.ComponentRepresentation
            ), f"Component {component} did not return ComponentDefinition"
            entity.components.append(new_component)

    return entity


def export_all(config):
    """Exports everything from this bend file"""
    output_folder = os.path.dirname(config["output_filepath"])

    if config["make_duplicates_real"]:
        # Make all collections into their real objects. Ideally one day this
        # will be subbed for actually using proper instancing of collections
        # but I couldn't get this to work in bevy :(
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=False)

    config["mesh_output_folder"] = os.path.join(
        output_folder, config["mesh_output_folder"]
    )
    if not os.path.exists(config["mesh_output_folder"]):
        os.makedirs(config["mesh_output_folder"])

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    scene = bpy.context.scene

    config["output_folder"] = output_folder
    config["scene"] = bpy.context.scene

    entities = [export_entity(config, o, i) for i, o in enumerate(scene.objects)]

    with open(config["output_filepath"], "w", encoding="utf-8") as outfile:
        outfile.write(utils.encode(entities))
