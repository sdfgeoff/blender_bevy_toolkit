import bpy
from . import component_base


# We need a list of all the components with a unique ID's and the
# class that represents it. This is used to create the add/remote drop-downs
ALL_COMPONENT_LIST = [
    # ID, Name, Class
]


def update_all_component_list():
    """Maintain the list of components present in the scene. This needs
    to be re-invoked whenever this list may have changed (eg a new
    blend file is loaded)."""
    global ALL_COMPONENT_LIST
    component_list = []
    for component_index, component in enumerate(component_base.COMPONENTS):
        component_list.append((str(component_index + 1), component.__name__, component))
    ALL_COMPONENT_LIST = component_list


def generate_component_to_remove_list(widget, context):
    """The remove component dialog only shows what components the
    object has present that can be removed. This function
    figures out what functions can be removed from an object"""
    component_types = [("0", "None", "None")]
    for id_str, name, component in ALL_COMPONENT_LIST:
        if component.is_present(context.object) and component.can_add(context.object):
            component_types.append((id_str, name, name))

    return component_types


def generate_component_to_add_list(widget, context):
    """When adding a bevy component, the list only displays the
    components that do not already exist on the object and ones that
    can be added to this object type"""
    component_types = [("0", "None", "None")]
    for id_str, name, component in ALL_COMPONENT_LIST:
        if component.is_present(context.object):
            continue
        if component.can_add(context.object):
            component_types.append((id_str, name, name))

    return component_types


class RemoveBevyComponent(bpy.types.Operator):
    bl_idname = "object.remove_bevy_component"
    bl_label = "Remove Bevy Component"
    bl_options = {"REGISTER", "UNDO"}

    property_to_remove: bpy.props.EnumProperty(
        name="Remove Component",
        description="Select the component you wish to remove",
        default=None,
        items=generate_component_to_remove_list,
    )

    def invoke(self, context, _event):
        """Show selection dialog that allows the user to select a compoent
        to remove"""
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        """Removes the selected component from the object"""
        selected = self.property_to_remove
        if selected in ("0", ""):
            return {"FINISHED"}

        component = component_base.COMPONENTS[int(selected) - 1]
        component.remove(context.object)

        # Redraw UI
        for area in bpy.context.window.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()

        return {"FINISHED"}


class AddBevyComponent(bpy.types.Operator):
    bl_idname = "object.add_bevy_component"
    bl_label = "Add Bevy Component"
    bl_options = {"REGISTER", "UNDO"}

    property_to_add: bpy.props.EnumProperty(
        name="Add Component",
        description="Select the component you wish to add",
        default=None,
        items=generate_component_to_add_list,
    )

    def invoke(self, context, _event):
        """Display the add-component selector, allowing the user to
        select what component they wish to add"""
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        """Adds the currently selected component to the object by invoking
        it's add method"""
        selected = self.property_to_add
        if selected in ("0", ""):
            return {"FINISHED"}

        component = component_base.COMPONENTS[int(selected) - 1]
        component.add(context.object)

        # Redraw UI
        for area in bpy.context.window.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()
        return {"FINISHED"}
