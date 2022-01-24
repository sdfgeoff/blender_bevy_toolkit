import mathutils
import bpy
import json


def jdict(**kwargs):
    return json.dumps(dict(**kwargs))


def iterable_to_string(data, start="[", end="]", joiner=","):
    return start + joiner.join(encode(d) for d in data) + end


def dict_to_str(data):
    return (
        "{"
        + ",".join("{}:{}".format(encode(k), encode(v)) for k, v in data.items())
        + "}"
    )


def vect_to_str(data):
    vec_size = len(data)
    return encode(
        {"type": "glam::vec{0}::Vec{0}".format(vec_size), "value": tuple(data)}
    )


def quat_to_str(data):
    return encode(
        {"type": "glam::quat::Quat", "value": (data.x, data.y, data.z, data.w)}
    )


def dq_string(data):
    """repr a string with double quotes. This is probably a fragile
    hack, so if it breaks, please do something better!"""
    return '"' + repr("'" + data)[2:]


def bool_to_str(b):
    # return encode({
    #     "type": "bool",
    #     "value": str(b).lower()
    # })
    return str(b).lower()


def encode(data):
    if hasattr(data, "to_str"):
        return data.to_str()
    return ENCODE_MAP[type(data)](data)


class F32:
    def __init__(self, val):
        self.val = val

    def to_str(self):
        return encode({"type": "f32", "value": self.val})


class F64:
    def __init__(self, val):
        self.val = val

    def to_str(self):
        return encode({"type": "f64", "value": self.val})


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
