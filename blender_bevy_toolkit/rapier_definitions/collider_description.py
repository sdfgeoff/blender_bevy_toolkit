from blender_bevy_toolkit.component_base import ComponentRepresentation, register_component
import bpy
import utils
import struct

# TODO:
# Instead of using obj.dimensions, use obj.bound_box
# This allows setting the offset WRT parent

def encode_sphere_collider_data(obj):
    if obj.type == "EMPTY":
        radius = obj.empty_display_size
    elif obj.type == "MESH":
        radius = max(
            obj.dimensions.x,
            obj.dimensions.y,
            obj.dimensions.z
        ) / 2.0
    else:
        print("Unable to figure out radius for {}", obj.name)
        radius = 1.0
    

    return struct.pack("<f", radius)


def encode_capsule_collider_data(obj):
    if obj.type == "MESH":
        radius = max(obj.dimensions.x, obj.dimensions.y) / 2.0
        half_height = max(obj.dimensions.z - radius, 0.0) / 2.0
    else:
        print("Unable to figure out capsule dimensions for {}", obj.name)
        radius = 1.0
        half_height = 1.0
    return struct.pack("<ff", half_height, radius)


# Physics shapes and a function to encode that shape provided an object
# Be cautious about inserting to the beginning/middle of this list or 
# removing an item as it will break existing blend files.
COLLIDER_SHAPES = [
    ("Sphere", encode_sphere_collider_data),
    ("Capsule", encode_capsule_collider_data),
]
    

@register_component
class ColliderDescription:
    def encode(config, obj):
        """ Returns a ComponentRepresentation representing this component
        """

        field_converters = [
            ("friction", utils.F32),
            ("restitution", utils.F32),
            ("is_sensor", bool),
            ("density", utils.F32),
        ]

        field_dict = {}
        for field_name, converter in field_converters:
            field_dict[field_name] = converter(getattr(obj.rapier_collider_description, field_name))

        # The collider_data field is dependant on the collider_shape, so we have to do some
        # derivation here
        collider_shape = int(obj.rapier_collider_description.collider_shape)

        encode_function = COLLIDER_SHAPES[collider_shape][1]
        raw_data = encode_function(obj)
        
        data = list(raw_data)


        field_dict["collider_shape"] = collider_shape
        field_dict["collider_shape_data"] = {
            "type": "smallvec::SmallVec<[u8; {}]>".format(len(data)),
            "list": data
        }

        return ComponentRepresentation(
            "blender_bevy_toolkit::rapier_physics::ColliderDescription",
            field_dict
        )
        
        
    def is_present(obj):
        """ Returns true if the supplied object has this component """
        return obj.rapier_collider_description.present
    
    def can_add(obj):
        return True

    @staticmethod
    def add(obj):
        obj.rapier_collider_description.present = True

    @staticmethod
    def remove(obj):
        obj.rapier_collider_description.present = False
    
    @staticmethod
    def register():
        bpy.utils.register_class(ColliderDescriptionPanel)
        bpy.utils.register_class(ColliderDescriptionProperties)
        bpy.types.Object.rapier_collider_description = bpy.props.PointerProperty(type=ColliderDescriptionProperties)


    @staticmethod
    def unregister():
        bpy.utils.unregister_class(ColliderDescriptionPanel)
        bpy.utils.unregister_class(ColliderDescriptionProperties)
        del bpy.types.Object.rapier_collider_description


class ColliderDescriptionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_rapier_collider_description"
    bl_label = "ColliderDescription"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return ColliderDescription.is_present(context.object)
    
    def draw(self, context):
        row = self.layout.row()
        row.label(text="A collider so this object can collide with things (when coupled with a rigidbody somewhere)")

        fields = ["friction", "restitution", "is_sensor", "density", "collider_shape"]

        for field in fields:
            row = self.layout.row()
            row.prop(context.object.rapier_collider_description, field)



class ColliderDescriptionProperties(bpy.types.PropertyGroup):
    present: bpy.props.BoolProperty(name="Present", default=False)

    friction: bpy.props.FloatProperty(name="friction", default=0.5)
    restitution: bpy.props.FloatProperty(name="restitution", default=0.5)
    is_sensor: bpy.props.BoolProperty(name="is_sensor", default=False)
    
    density: bpy.props.FloatProperty(name="density", default=0.5)

    shape_items = [(str(i), s[0], "") for i, s in enumerate(COLLIDER_SHAPES)]

    collider_shape: bpy.props.EnumProperty(name="collider_shape", default=0, items=shape_items)
