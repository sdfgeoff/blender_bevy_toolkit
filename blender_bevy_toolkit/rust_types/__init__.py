""" Handles encoding types (vectors, floats) from blender formats into
bevy-reflected formats serialized with RON """
import mathutils
from . import ron
from .ron import Str, Int, EnumValue, Map, List, Base


def reflect(type_path, processor):
    """Bevy reflects structs as maps. Create a map
    for the specified type, using the passed in "processor" function
    to pre-process the value"""

    class ReflectedType(Base):
        """Bevy reflects structs as maps"""

        def __init__(self, value):
            self.value = value

        def to_str(self, indent):
            return ron.encode(
                ron.Map(type=type_path, value=processor(self.value)), indent
            )

    return ReflectedType


Quat = reflect(
    "glam::quat::Quat", lambda quat: ron.Tuple(quat.x, quat.y, quat.z, quat.w)
)
Vec2 = reflect("glam::vec2::Vec2", lambda vec: ron.Tuple(vec[0], vec[1]))
Vec3 = reflect("glam::vec3::Vec3", lambda vec: ron.Tuple(vec[0], vec[1], vec[2]))
Vec4 = reflect("glam::vec4::Vec4", lambda vec: ron.Tuple(vec.x, vec.y, vec.z, vec.w))
BoolVec3 = reflect(
    "glam::vec3::IVec3", lambda vec: ron.Tuple(int(vec[0]), int(vec[1]), int(vec[2]))
)
F32 = reflect("f32", ron.Float)
F64 = reflect("f64", ron.Float)
Bool = reflect("bool", ron.Bool)
RgbaLinear = reflect(
    "bevy_render::color::Color",
    lambda col: ron.EnumValue(
        "RgbaLinear", ron.Struct(red=col.r, green=col.g, blue=col.b, alpha=1.0)
    ),
)
Entity = reflect("bevy_ecs::entity::Entity", lambda x: x)


class Enum(Base):
    """Reflected Enum that describes both type and value"""

    def __init__(self, contained_type, value):
        self.contained_type = contained_type
        self.value = value

    def to_str(self, indent):
        return ron.encode(
            ron.Map(
                type=self.contained_type,
                value=self.value,
            ),
            indent,
        )


class Option(Base):
    """Reflected Rust option. None or Some(value)"""

    def __init__(self, contained_type, value):
        self.contained_type = contained_type
        self.value = value

    def to_str(self, indent):
        return ron.encode(
            ron.Map(
                type=f"core::option::Option<{self.contained_type}>",
                value=ron.EnumValue("None")
                if self.value is None
                else ron.EnumValue("Some", ron.Tuple(self.value)),
            ),
            indent,
        )
