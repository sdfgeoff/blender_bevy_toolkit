""" Base functionality for all components and for finding/idetifying
them """
from . import utils


class ComponentRepresentation:
    """Utility class to assis with encoding a component struct.
    All components need to identify their type external to their data,
    and this class aids in that."""

    def __init__(self, typ, struct, type_override="struct"):
        self.typ = typ
        self.struct = struct
        self.type_override = type_override

    def to_str(self):
        """Converts into the string that is encoded into the scene"""
        return utils.encode({"type": self.typ, self.type_override: self.struct})

    def __repr__(self):
        return f"{self.typ} {{...}}"


COMPONENTS = []


def register_component(cls):
    """Adds a class as a component. This means that the class can be
    located by (eg) the UI and exporter phase.

    This can be used as a decorator on the class:

    ```
    @register_component
    class MyNewComponent():
        def __init__(self):
            ...
    ```
    or called as a function on a class.
    """
    COMPONENTS.append(cls)
    COMPONENTS.sort(key=lambda c: c.__name__)
    return cls
