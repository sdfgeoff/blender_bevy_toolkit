""" Base functionality for all components and for finding/idetifying
them """
from abc import ABCMeta, abstractmethod
from . import utils


class ComponentBase(metaclass=ABCMeta):
    """All components need to implement this base class to work with the exporter"""

    @staticmethod
    @abstractmethod
    def encode(config, obj):
        """Returns a ComponentRepresentation representing this component"""
        return ComponentRepresentation(
            "mycrate::mymodule::MyStruct",
            [],
        )

    @staticmethod
    @abstractmethod
    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return True

    @staticmethod
    @abstractmethod
    def can_add(obj):
        """Returns true if the supplied object can have this component
        (eg a blender light cannot have a mesh component)"""

    @staticmethod
    @abstractmethod
    def register():
        """Called on loading the plugin, use to register the panel UI and
        fields for this component

        You should probably call bpy.utils.register_class in here somewhere
        """

    @staticmethod
    @abstractmethod
    def unregister():
        """Called on unloading the plugin, use to register the panel UI and
        fields for this component.

        You should probably call bpy.utils.unregister_class in here somewhere
        """


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
    # Check the component has all the required functions
    assert isinstance(cls(), ComponentBase), "Attempting to register component that does not inherit from Componentbase"
    
    COMPONENTS.append(cls)
    COMPONENTS.sort(key=lambda c: c.__name__)
    return cls
