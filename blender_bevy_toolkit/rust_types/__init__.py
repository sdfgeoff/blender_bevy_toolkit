""" Handles encoding types (vectors, floats) from blender formats into
bevy-reflected formats serialized with RON """
import mathutils
from . import ron
from .ron import Str, Int, EnumValue, Map, List


def reflect(type_path, processor):
    class ReflectedType:
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
Vec2 = reflect("glam::vec2::Vec2", lambda vec: ron.Tuple(vec.x, vec.y))
Vec3 = reflect("glam::vec3::Vec3", lambda vec: ron.Tuple(vec.x, vec.y, vec.z))
Vec4 = reflect("glam::vec4::Vec4", lambda vec: ron.Tuple(vec.x, vec.y, vec.z, vec.w))
F32 = reflect("f32", lambda f: ron.Float(f))
F64 = reflect("f64", lambda f: ron.Float(f))
Bool = reflect("bool", lambda f: ron.Bool(f))
RgbaLinear = reflect(
    "bevy_render::color::Color",
    lambda col: ron.EnumValue(
        "RgbaLinear", ron.Struct(red=col.r, green=col.g, blue=col.b, alpha=1.0)
    ),
)
Entity = reflect("bevy_ecs::entity::Entity", lambda x: x)


class Enum:
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


class Option:
    """Rust option. None or Some(value)"""

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
