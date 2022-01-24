""" Handles encoding fundamental types (vectors, floats) from blender formats into
bevy/glam formats """
import json
import mathutils


def jdict(**kwargs):
    """Dump arguments into a JSON-encoded string"""
    return json.dumps(dict(**kwargs))


def iterable_to_string(data, start="[", end="]", joiner=","):
    """recursively encodes an array as a string by calling `encode`"""
    return start + joiner.join(encode(d) for d in data) + end


def dict_to_str(data):
    """recursively encodes a dictionary as a string by calling `encode`"""
    items = ",".join(f"{encode(k)}:{encode(v)}" for k, v in data.items())
    return f"{{{items}}}"


def vect_to_str(data):
    """Convert from a mathutils vector into a glam vector"""
    vec_size = len(data)
    return encode({"type": f"glam::vec{vec_size}::Vec{vec_size}", "value": tuple(data)})


def quat_to_str(data):
    """Convert from a mathutils quaternion into a glam quaternion"""
    return encode(
        {"type": "glam::quat::Quat", "value": (data.x, data.y, data.z, data.w)}
    )


def dq_string(data):
    """repr a string with double quotes. This is probably a fragile
    hack, so if it breaks, please do something better!"""
    return '"' + repr("'" + data)[2:]


def bool_to_str(value):
    """represents a boolean as a string true and false"""
    return str(value).lower()


class F32:
    """Represents a floating point 32 bit number and encodes into bevys scn format"""

    def __init__(self, val):
        self.val = val

    def to_str(self):
        """Encode the float into a bevy-compatible string!"""
        return encode({"type": "f32", "value": self.val})


class F64:
    """Represents a floating point 64 bit number and encodes into bevys scn format"""

    def __init__(self, val):
        self.val = val

    def to_str(self):
        """Encode the float into a bevy-compatible string!"""
        return encode({"type": "f64", "value": self.val})


def encode(data):
    """The "base" encoder. Call this with some data and hopefully it will be encoded
    as a string"""
    if hasattr(data, "to_str"):
        return data.to_str()
    return ENCODE_MAP[type(data)](data)


ENCODE_MAP = {
    str: dq_string,
    int: str,
    float: str,
    bool: bool_to_str,
    tuple: lambda x: iterable_to_string(x, "(", ")", ","),
    list: lambda x: iterable_to_string(x, "[", "]", ","),
    dict: dict_to_str,
    mathutils.Vector: vect_to_str,
    mathutils.Quaternion: quat_to_str,
}
