from blender_bevy_toolkit.component_base import (
    ComponentBase,
    register_component,
    rust_types,
)
import bpy
import struct
import collections

# Used to define the different bounds. Each bound
# has a name (displayed in teh enum), a function
# that turns an object into bytes
# and draw_type defines how bounds are drawn in the viewport.
BoundsType = collections.namedtuple("BoundsType", ["name", "encoder", "draw_type"])


def encode_sphere_collider_data(obj):
    if obj.type == "EMPTY":
        radius = obj.empty_display_size
    elif obj.type == "MESH":
        radius = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z) / 2.0
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


def encode_box_collider_data(obj):
    if obj.type == "MESH":
        dims = [obj.dimensions.x / 2.0, obj.dimensions.y / 2.0, obj.dimensions.z / 2.0]
    else:
        print("Unable to figure out box dimensions for {}", obj.name)
        dims = [1.0, 1.0, 1.0]
    return struct.pack("<fff", *dims)


# Physics shapes and a function to encode that shape provided an object
# Be cautious about inserting to the beginning/middle of this list or
# removing an item as it will break existing blend files.
COLLIDER_SHAPES = [
    BoundsType(name="Sphere", encoder=encode_sphere_collider_data, draw_type="SPHERE"),
    BoundsType(
        name="Capsule", encoder=encode_capsule_collider_data, draw_type="CAPSULE"
    ),
    BoundsType(name="Box", encoder=encode_box_collider_data, draw_type="BOX"),
]


@register_component
class ColliderDescription(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component"""

        # The collider_data field is dependant on the collider_shape, so we have to do some
        # derivation here
        collider_shape = int(obj.rapier_collider_description.collider_shape)

        encode_function = COLLIDER_SHAPES[collider_shape].encoder
        raw_data = encode_function(obj)
        data = list(raw_data)

        field_dict = {}
        field_dict["collider_shape"] = collider_shape
        field_dict["collider_shape_data"] = rust_types.Map(
            type="smallvec::SmallVec<[u8; {}]>".format(len(data)),
            list=rust_types.List(*data),
        )

        minx, miny, minz = 9e9, 9e9, 9e9
        maxx, maxy, maxz = (
            -9e9,
            -9e9,
            -9e9,
        )
        for x, y, z in obj.bound_box:
            minx = min(minx, x)
            miny = min(miny, y)
            minz = min(minz, z)

            maxx = max(maxx, x)
            maxy = max(maxy, y)
            maxz = max(maxz, z)

        centroid_translation = [
            minx + (maxx - minx) / 2,
            miny + (maxy - miny) / 2,
            minz + (maxz - minz) / 2,
        ]

        return rust_types.Map(
            type="blender_bevy_toolkit::rapier_physics::ColliderDescription",
            struct=rust_types.Map(
                friction=rust_types.F32(obj.rapier_collider_description.friction),
                restitution=rust_types.F32(obj.rapier_collider_description.restitution),
                is_sensor=rust_types.Bool(obj.rapier_collider_description.is_sensor),
                centroid_translation=rust_types.Vec3(centroid_translation),
                density=rust_types.F32(obj.rapier_collider_description.density),
                **field_dict
            ),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return obj.rapier_collider_description.present

    def can_add(obj):
        return True

    @staticmethod
    def add(obj):
        obj.rapier_collider_description.present = True
        update_draw_bounds(obj)

    @staticmethod
    def remove(obj):
        obj.rapier_collider_description.present = False
        update_draw_bounds(obj)

    @staticmethod
    def register():
        bpy.utils.register_class(ColliderDescriptionPanel)
        bpy.utils.register_class(ColliderDescriptionProperties)
        bpy.types.Object.rapier_collider_description = bpy.props.PointerProperty(
            type=ColliderDescriptionProperties
        )

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(ColliderDescriptionPanel)
        bpy.utils.unregister_class(ColliderDescriptionProperties)
        del bpy.types.Object.rapier_collider_description


class ColliderDescriptionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_rapier_collider_description"
    bl_label = "ColliderDescription"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return ColliderDescription.is_present(context.object)

    def draw(self, context):
        row = self.layout.row()
        row.label(
            text="A collider so this object can collide with things (when coupled with a rigidbody somewhere)"
        )

        fields = ["friction", "restitution", "is_sensor", "density", "collider_shape"]

        for field in fields:
            row = self.layout.row()
            row.prop(context.object.rapier_collider_description, field)


def update_draw_bounds(obj):
    """Changes how the object is shown in the viewport in order to
    display the bounds to the user"""
    if ColliderDescription.is_present(obj):
        collider_type_id = int(obj.rapier_collider_description.collider_shape)
        collider_type_data = COLLIDER_SHAPES[collider_type_id].draw_type

        obj.show_bounds = True
        obj.display_bounds_type = collider_type_data

    else:
        obj.show_bounds = False


def collider_shape_changed(_, context):
    """Runs when the enum selecting the shape is changed"""
    update_draw_bounds(context.object)


class ColliderDescriptionProperties(bpy.types.PropertyGroup):
    present: bpy.props.BoolProperty(name="Present", default=False)

    friction: bpy.props.FloatProperty(name="friction", default=0.5)
    restitution: bpy.props.FloatProperty(name="restitution", default=0.5)
    is_sensor: bpy.props.BoolProperty(name="is_sensor", default=False)

    density: bpy.props.FloatProperty(name="density", default=0.5)

    shape_items = [(str(i), s.name, "") for i, s in enumerate(COLLIDER_SHAPES)]

    collider_shape: bpy.props.EnumProperty(
        name="collider_shape",
        default=0,
        items=shape_items,
        update=collider_shape_changed,
    )
