import os

import bpy
import struct
import hashlib


from . import utils, components, component_base


class Entity:
    def __init__(self, id, comp):
        self.id = id
        self.components = comp

    def to_str(self):
        return "(\n    entity: {},\n    components:{}\n)".format(
            utils.encode(self.id),
            utils.iterable_to_string(
                self.components, "[\n        ", "\n    ]", ",\n        "
            ),
        )


def export_entity(config, obj, id):
    entity = Entity(id, list())

    for component in component_base.COMPONENTS:
        if component.is_present(obj):
            new_component = component.encode(config, obj)
            assert isinstance(
                new_component, component_base.ComponentRepresentation
            ), "Component {} did not return ComponentDefinition".format(component)
            entity.components.append(new_component)

    return entity


def export_all(config):
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

    objects = [o for o in scene.objects]
    entities = [export_entity(config, o, i) for i, o in enumerate(objects)]
    collection_data = entities

    open(config["output_filepath"], "w").write(utils.encode(entities))
