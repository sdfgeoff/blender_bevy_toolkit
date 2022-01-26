""" Creates components from JSON files. This provides an easy
way for adding custom components without mucking around with blenders
API. Of course, for more advanced tools it is necessary to create
more complex UI's, but if you just want a component with a couple twiddleable
numbers, bools and vecs, a JSON component can do it for you.


Warning, this code is meta-programming heavy and probably impossible to
debug. Sorry
"""
import os
import json
import logging
import collections
import functools

import bpy
import mathutils

import utils
from utils import jdict

from .component_base import ComponentRepresentation, register_component

logger = logging.getLogger(__name__)


FieldDefinition = collections.namedtuple(
    "FieldDefinition", ["field", "type", "default", "description"]
)
ComponentDefininition = collections.namedtuple(
    "ComponentDefinition", ["name", "description", "id", "struct", "fields"]
)


# Map from JSON strings to blender property types
TYPE_PROPERTIES = {
    "string": bpy.props.StringProperty,
    "bool": bpy.props.BoolProperty,
    "f64": bpy.props.FloatProperty,
    "f32": bpy.props.FloatProperty,
    "int": bpy.props.IntProperty,
    "vec3": functools.partial(bpy.props.FloatVectorProperty, size=3),
    "vec2": functools.partial(bpy.props.FloatVectorProperty, size=2),
    "u8enum": bpy.props.EnumProperty,
}

# Map from JSON strings to a function/object that the encoder can process
# to serialize the data
TYPE_ENCODERS = {
    "string": str,
    "bool": bool,
    "f64": utils.F64,
    "f32": utils.F32,
    "int": int,
    "vec3": mathutils.Vector,
    "vec2": mathutils.Vector,
    "u8enum": int,
}


def get_component_files(folder):
    component_definitions = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            component_definitions.append(os.path.join(folder, filename))
    return component_definitions


def construct_component_classes(component_filepath):
    # Parse the file from JSON into some python namedtuples
    logging.info(
        jdict(event="construct_json_classes", path=component_filepath, state="start")
    )

    try:
        component = json.load(open(component_filepath))
    except json.decoder.JSONDecodeError as err:
        logging.exception(
            jdict(
                event="construct_json_component_parse_error",
                path=component_filepath,
                error=err,
                exc_info=err,
            )
        )
        return None

    def parse_field(field):
        return FieldDefinition(
            field=field["field"],
            type=field["type"],
            default=field["default"],
            description=field["description"],
        )

    component_def = ComponentDefininition(
        name=component["name"],
        description=component["description"],
        id=component["id"],
        struct=component["struct"],
        fields=[parse_field(f) for f in component["fields"]],
    )
    logging.debug(
        jdict(
            event="construct_json_classes",
            path=component_filepath,
            state="parse_complete",
        )
    )

    # component becomes bpy.types.Object.<<<obj_key>>>
    obj_key = component_def.id

    # Create a class that stores all the internals of the properties in
    # a blender-compatible way.
    properties = type(component["name"] + "Properties", (bpy.types.PropertyGroup,), {})

    # Create bpy.props Properties for each field inside the component
    fields = {}
    for field in component_def.fields:
        prop_type = TYPE_PROPERTIES[field.type]
        args_dict = {
            "name": field.field,
            "description": field.description,
        }
        if prop_type == bpy.props.EnumProperty:
            items = []
            for index, name in enumerate(field.default):
                items.append((str(index), name, ""))
            args_dict["items"] = items
        else:
            args_dict["default"] = field.default

        prop = prop_type(**args_dict)
        fields[field.field] = prop

    fields["present"] = bpy.props.BoolProperty(name="Present", default=False)
    properties.__annotations__ = fields

    logging.debug(
        jdict(
            event="construct_json_classes",
            path=component_filepath,
            state="fields_completed",
        )
    )

    # Create a class to store the data about this component inside the
    # blender object
    component_class = type(
        component["name"],
        (),
        {
            "can_add": lambda _: True,
            "is_present": lambda obj: getattr(obj, obj_key).present,
        },
    )

    # Create a class that will create a UI for the component
    panel = type(
        component_def.name + "Panel",
        (bpy.types.Panel,),
        {
            "bl_idname": "OBJECT_PT_" + component_def.id,
            "bl_label": component_def.name,
            "bl_space_type": "PROPERTIES",
            "bl_region_type": "WINDOW",
            "bl_context": "physics",
        },
    )
    panel.poll = classmethod(
        lambda cls, context: component_class.is_present(context.object)
    )

    def draw(self, context):
        row = self.layout.row()
        row.label(text=component_def.description)
        if len(fields) == 1:
            row = self.layout.row()
            row.label(text="No Options")
        else:
            for field in fields:
                if field == "present":
                    continue
                row = self.layout.row()
                row.prop(getattr(context.object, obj_key), field)

    panel.draw = draw

    logging.debug(
        jdict(
            event="construct_json_classes",
            path=component_filepath,
            state="panel_created",
        )
    )

    # These functions all get put inside the component_class
    def register():
        bpy.utils.register_class(panel)
        bpy.utils.register_class(properties)
        setattr(bpy.types.Object, obj_key, bpy.props.PointerProperty(type=properties))

    def unregister():
        bpy.utils.unregister_class(panel)
        bpy.utils.unregister_class(properties)
        delattr(bpy.types.Object, obj_key)

    def add(obj):
        getattr(obj, obj_key).present = True

    def remove(obj):
        getattr(obj, obj_key).present = False

    def encode(config, obj):
        """Returns a ComponentRepresentation representing this component"""
        component_data = getattr(obj, obj_key)

        def fix_types(field_name, value):
            """Ensure types are properly represented for encoding"""
            field_data = [f for f in component_def.fields if f.field == field_name][0]
            encoder = TYPE_ENCODERS[field_data.type]
            return encoder(value)

        component_values = {
            f: fix_types(f, getattr(component_data, f))
            for f in fields
            if f != "present"
        }
        return ComponentRepresentation(component_def.struct, component_values)

    component_class.register = staticmethod(register)
    component_class.unregister = staticmethod(unregister)
    component_class.add = staticmethod(add)
    component_class.remove = staticmethod(remove)
    component_class.encode = staticmethod(encode)

    logging.debug(
        jdict(event="construct_json_classes", path=component_filepath, state="end")
    )
    return component_class


def load_folder(folder):
    """Scans a folder for json files and loads them as components"""
    logger.info(jdict(event="scan_folder_for_json_components", folder=folder))

    json_files = get_component_files(folder)
    logger.info(
        jdict(
            event="scan_folder_for_json_components",
            folder=folder,
            json_files=json_files,
        )
    )
    classes = [construct_component_classes(c) for c in json_files]
    for cls in classes:
        register_component(cls)
