""" Converts from blender objects into a scene description """
import os
import logging
import bpy
from . import component_base, rust_types, jdict


logger = logging.getLogger(__name__)


class Entity:
    """In an ECS, an entity is an opaque ID that is referenced by (or references)
    a set of components. This class represents an entity and as such ... contains
    a lit of components. The ID field should be unique in the scene"""

    def __init__(self, entity_id, comp):
        self.entity_id = entity_id
        self.components = comp

    def to_str(self, indent):
        """Convert into a ... string!"""
        return rust_types.ron.encode(
            rust_types.ron.Struct(
                entity=rust_types.Int(self.entity_id),
                components=rust_types.List(*self.components),
            ),
            indent,
        )


def export_entity(config, obj, entity_id):
    """Compile all the data about an object into an entity with components"""
    logger.debug(
        jdict(event="serializing_entity", obj_name=obj.name, entity_id=entity_id)
    )
    entity = Entity(entity_id, [])

    for component in component_base.COMPONENTS:
        if component.is_present(obj):
            new_component = component.encode(config, obj)
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
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)

        # Rigid bodies can often being parented to other objects as a result of
        # making duplicates real,, which Rapier doesn't deal with
        # nicely. So let's forceably remove the parent before exporting.
        for obj in bpy.context.scene.objects:
            if hasattr(obj, "rapier_rigid_body") and obj.rapier_rigid_body.present:
                transform_bak = obj.matrix_world.copy()
                obj.parent = None
                obj.matrix_world = transform_bak

    config["mesh_output_folder"] = os.path.join(
        output_folder, config["mesh_output_folder"]
    )
    if not os.path.exists(config["mesh_output_folder"]):
        os.makedirs(config["mesh_output_folder"])

    config["material_output_folder"] = os.path.join(
        output_folder, config["material_output_folder"]
    )
    if not os.path.exists(config["material_output_folder"]):
        os.makedirs(config["material_output_folder"])

    config["texture_output_folder"] = os.path.join(
        output_folder, config["texture_output_folder"]
    )
    if not os.path.exists(config["texture_output_folder"]):
        os.makedirs(config["texture_output_folder"])

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    scene = bpy.context.scene

    config["output_folder"] = output_folder
    config["scene"] = bpy.context.scene

    entities = [export_entity(config, o, i) for i, o in enumerate(scene.objects)]

    with open(config["output_filepath"], "w", encoding="utf-8") as outfile:
        outfile.write(rust_types.ron.encode(rust_types.ron.List(*entities)))
