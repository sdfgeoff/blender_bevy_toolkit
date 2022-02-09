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


class Base(metaclass=ABCMeta):
    """Convert into a rust/ron type"""

    def to_str(self):
        """Do Serialization"""


class List(Base):
    """List"""

    def __init__(self, *values):
        self.values = values

    def to_str(self):
        return "[" + ",".join(encode(d) for d in self.values) + "]"


class Tuple(Base):
    """Tuple"""

    def __init__(self, *values):
        self.values = values

    def to_str(self):
        return "(" + ",".join(encode(d) for d in self.values) + ")"


class Str(Base):
    """&str"""

    def __init__(self, value):
        self.value = value

    def to_str(self):
        """repr a string with double quotes. This is probably a fragile
        hack, so if it breaks, please do something better!"""
        return '"' + repr("'" + self.value)[2:]


class Bool(Base):
    """Bool"""

    def __init__(self, value):
        self.value = value

    def to_str(self):
        if self.value:
            return "true"
        return "false"


class Int(Base):
    """i32, u64 etc."""

    def __init__(self, value):
        self.value = value

    def to_str(self):
        return str(self.value)


class Float(Base):
    """f32, f64, etc..."""

    def __init__(self, value):
        self.value = value

    def to_str(self):
        return str(self.value)


class Struct(Base):
    """eg:
    (
        this: 2,
        that: 6
    )
    """

    def __init__(self, **mapping):
        self.mapping = mapping

    def to_str(self):
        field_string = ",".join(f"{k}:{encode(v)}" for k, v in self.mapping.items())
        return f"({field_string})"


class Map(Base):
    """eg:
    {
        "this": 2,
        "that": 4,
    }
    """

    def __init__(self, **mapping):
        self.mapping = mapping

    def to_str(self):
        field_string = ",".join(
            f"{encode(k)}:{encode(v)}" for k, v in self.mapping.items()
        )
        return f"{{{field_string}}}"


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

    def to_str(self):
        if self.value is None:
            return self.variant
        return self.variant + encode(self.value)


ENCODE_MAP = {
    str: Str,
    int: Int,
    bool: Bool,
    float: Float,
    list: List,
    tuple: Tuple,
}


def encode(data):
    """The "base" encoder. Call this with some data and hopefully it will be encoded
    as a string"""
    if hasattr(data, "to_str"):
        return data.to_str()
    return ENCODE_MAP[type(data)](data).to_str()
