""" Creates components from a component definitions. This provides an easy
way for adding custom components without mucking around with blenders
API too much. Of course, for more advanced tools it is necessary to create
more complex UI's, but if you just want a component with a couple twiddleable
numbers, bools and vecs, this can go a long way towards automating it.

Supports:
 - Common field types such as string, bool, int
 - Passing in a custom "is_present" function


Warning, this code is meta-programming heavy and probably impossible to
debug. Sorry
"""

import logging
import collections
import functools
import abc

import bpy

from .utils import jdict
from . import rust_types

from .component_base import ComponentBase

logger = logging.getLogger(__name__)


FieldDefinition = collections.namedtuple(
    "FieldDefinition", ["field", "type", "default", "description"]
)
ComponentDefinition = collections.namedtuple(
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
    "bool_vec3": functools.partial(bpy.props.BoolVectorProperty, size=3, subtype="XYZ"),
    "u8enum": bpy.props.EnumProperty,
}

# Map from JSON strings to a function/object that the encoder can process
# to serialize the data
TYPE_ENCODERS = {
    "string": rust_types.Str,
    "bool": rust_types.Bool,
    "f64": rust_types.F64,
    "f32": rust_types.F32,
    "int": rust_types.Int,
    "vec3": rust_types.Vec3,
    "vec2": rust_types.Vec2,
    "u8enum": rust_types.Int,
    "bool_vec3": rust_types.BoolVec3,
}


def create_ui_panel(component_def, component_class, fields):
    """Create a class that will create a UI for the component"""
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
                row.prop(getattr(context.object, component_def.id), field)

    panel.draw = draw

    logging.debug(
        jdict(
            event="construct_json_classes",
            component=component_def.name,
            state="panel_created",
        )
    )

    return panel


# pylint: disable=too-many-arguments
def insert_class_methods(
    component_class, component_def, panel, properties, fields, is_present_function=None
):
    """The class representing this component needs some functions (eg to detect if
    the component exists on a blender object). These functions are generated and
    added to the class here"""
    # These functions all get put inside the component_class
    def register():
        bpy.utils.register_class(panel)
        bpy.utils.register_class(properties)
        setattr(
            bpy.types.Object,
            component_def.id,
            bpy.props.PointerProperty(type=properties),
        )

    def unregister():
        bpy.utils.unregister_class(panel)
        bpy.utils.unregister_class(properties)
        delattr(bpy.types.Object, component_def.id)

    def remove(obj):
        getattr(obj, component_def.id).present = False

    def encode(_config, obj):
        """Returns a Component representing this component"""
        component_data = getattr(obj, component_def.id)

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
        return rust_types.Map(
            type=component_def.struct, struct=rust_types.Map(**component_values)
        )

    component_class.register = staticmethod(register)
    component_class.unregister = staticmethod(unregister)
    component_class.remove = staticmethod(remove)
    component_class.encode = staticmethod(encode)

    if is_present_function is None:

        def can_add(_obj):
            return True

        def add(obj):
            getattr(obj, component_def.id).present = True

        def is_present(obj):
            return getattr(obj, component_def.id).present

    else:

        def can_add(_obj):
            return False

        def add(_obj):
            pass

        is_present = is_present_function

    component_class.add = staticmethod(add)
    component_class.can_add = staticmethod(can_add)
    component_class.is_present = staticmethod(is_present)


def create_fields(component_def):
    """Create bpy.props Properties for each field inside the component"""
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
    return fields


def component_from_def(component_def, is_present_function=None):
    """Create a class that stores all the internals of the properties in
    a blender-compatible way.

    The major parameters is a component definition which describes all
    the internals of the component.

    The second parameters is a function that can be used to override the deteciton
    of if the component is present. If this function does not exist, then the
    user has to add the component manually. If a function is provided then it is
    executed to determine if the component is present in an object.
    """
    logging.debug(
        jdict(
            event="construct_class_from_def",
            definition=component_def,
            state="start",
        )
    )

    properties = type(f"{component_def.name}Properties", (bpy.types.PropertyGroup,), {})
    fields = create_fields(component_def)
    properties.__annotations__ = fields

    # Create a class to store the data about this component inside the
    # blender object
    component_class = type(
        component_def.name,
        (),
        {},
    )

    panel = create_ui_panel(component_def, component_class, fields)

    insert_class_methods(
        component_class,
        component_def,
        panel,
        properties,
        fields,
        is_present_function=is_present_function,
    )
    abc.ABCMeta.register(ComponentBase, component_class)

    logging.debug(
        jdict(event="construct_class_from_def", definition=component_def, state="end")
    )
    return component_class
