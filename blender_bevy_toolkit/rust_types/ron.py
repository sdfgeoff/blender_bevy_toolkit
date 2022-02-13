""" Ron is a fairly nice format for encoding data in rust. 
For more information, see:
https://github.com/ron-rs/ron

This module provides virtual "types" to aid serialization.
For example, you can construct a tuple with:

```
t = ron.Tuple(1,2,3,4)
ron.encode(t)
```
"""
from abc import ABCMeta


INDENT_SIZE = 1
INDENT_CHAR = "\t"


def ind(indent_level):
    if INDENT_SIZE == 0:
        return ""
    return "\n" + INDENT_CHAR * INDENT_SIZE * indent_level


class Base(metaclass=ABCMeta):
    """Convert into a rust/ron type"""

    def to_str(self, indent):
        """Do Serialization"""


class List(Base):
    """List"""

    def __init__(self, *values):
        self.values = values

    def to_str(self, indent):
        if not self.values:
            return "[]"
        indc = ind(indent + 1)
        return (
            f"[{indc}"
            + f",{indc}".join(encode(d, indent + 1) for d in self.values)
            + f"{ind(indent)}]"
        )


class Tuple(Base):
    """Tuple"""

    def __init__(self, *values):
        self.values = values

    def to_str(self, indent):
        if not self.values:
            return "()"
        indc = ind(indent + 1)
        return (
            f"({indc}"
            + f",{indc}".join(encode(d, indent + 1) for d in self.values)
            + f"{ind(indent)})"
        )


class Struct(Base):
    """eg:
    (
        this: 2,
        that: 6
    )
    """

    def __init__(self, **mapping):
        self.mapping = mapping

    def to_str(self, indent):
        if not self.mapping:
            return "()"
        indc = ind(indent+1)
        field_string = f",{indc}".join(
            f"{k}:{encode(v, indent+1)}" for k, v in self.mapping.items()
        )
        return f"({indc}{field_string}{ind(indent)})"


class Map(Base):
    """eg:
    {
        "this": 2,
        "that": 4,
    }
    """

    def __init__(self, **mapping):
        self.mapping = mapping

    def to_str(self, indent):
        if not self.mapping:
            return "{}"
        indc = ind(indent + 1)
        field_string = f",{indc}".join(
            f"{encode(k, indent+1)}:{encode(v, indent+1)}"
            for k, v in self.mapping.items()
        )
        return f"{{{indc}{field_string}{ind(indent)}}}"


class EnumValue(Base):
    """A variant-prefixed value or just the prefix.

    Eg:
    EnumValue("Some", Tuple("Thing")) => Some(Thing)
    EnumValue("None") => None
    EnumValue("Event", Struct(id=3)) => Event{id=3}
    """

    def __init__(self, variant, value=None):
        self.variant = variant
        self.value = value

    def to_str(self, indent):
        if self.value is None:
            return self.variant
        return self.variant + encode(self.value, indent)


class Str(Base):
    """&str"""

    def __init__(self, value):
        self.value = value

    def to_str(self, _indent):
        """repr a string with double quotes. This is probably a fragile
        hack, so if it breaks, please do something better!"""
        return '"' + repr("'" + self.value)[2:]


class Bool(Base):
    """Bool"""

    def __init__(self, value):
        self.value = value

    def to_str(self, _indent):
        if self.value:
            return "true"
        return "false"


class Int(Base):
    """i32, u64 etc."""

    def __init__(self, value):
        self.value = value

    def to_str(self, _indent):
        return str(self.value)


class Float(Base):
    """f32, f64, etc..."""

    def __init__(self, value):
        self.value = value

    def to_str(self, _indent):
        return str(self.value)


ENCODE_MAP = {
    str: Str,
    int: Int,
    bool: Bool,
    float: Float,
    list: List,
    tuple: Tuple,
}


def encode(data, indent=0):
    """The "base" encoder. Call this with some data and hopefully it will be encoded
    as a string"""
    if hasattr(data, "to_str"):
        return data.to_str(indent)
    return ENCODE_MAP[type(data)](data).to_str(indent)
