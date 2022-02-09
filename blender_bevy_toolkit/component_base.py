""" Base functionality for all components and for finding/idetifying
them """
from abc import ABCMeta, abstractmethod
from . import rust_types


class ComponentBase(metaclass=ABCMeta):
    """All components need to implement this base class to work with the exporter"""

    @staticmethod
    @abstractmethod
    def encode(config, obj):
        """Returns a Component representing this component"""
        return rust_types.Component(
            "mycrate::mymodule::MyStruct",
            rust_types.Map(),
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
    assert isinstance(
        cls(), ComponentBase
    ), "Attempting to register component that does not inherit from Componentbase"

    COMPONENTS.append(cls)
    COMPONENTS.sort(key=lambda c: c.__name__)
    return cls
