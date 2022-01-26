import bpy
from . import component_base


# We need a list of all the components with a unique ID's and the
# class that represents it. This is used to create the add/remote drop-downs
ALL_COMPONENT_LIST = [
    # ID, Name, Class
]


def update_all_component_list():
    global ALL_COMPONENT_LIST
    component_list = []
    for id, component in enumerate(component_base.COMPONENTS):
        component_list.append((str(id + 1), component.__name__, component))
    ALL_COMPONENT_LIST = component_list


class RemoveBevyComponent(bpy.types.Operator):
    bl_idname = "object.remove_bevy_component"
    bl_label = "Remove Bevy Component"
    bl_options = {"REGISTER", "UNDO"}

    def update_component_to_remove_list(self, context):
        component_types = [("0", "None", "None")]
        for id_str, name, component in ALL_COMPONENT_LIST:
            if component.is_present(context.object) and component.can_add(
                context.object
            ):
                component_types.append((id_str, name, name))

        return component_types

    property_to_remove: bpy.props.EnumProperty(
        name="Remove Component",
        description="Select the component you wish to remove",
        default=None,
        items=update_component_to_remove_list,
    )

    def invoke(self, context, _event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected = self.property_to_remove
        if selected == "0" or selected == "":
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

    def update_component_to_add_list(self, context):
        component_types = [("0", "None", "None")]
        for id_str, name, component in ALL_COMPONENT_LIST:
            if component.is_present(context.object):
                continue
            if component.can_add(context.object):
                component_types.append((id_str, name, name))

        return component_types

    property_to_add: bpy.props.EnumProperty(
        name="Add Component",
        description="Select the component you wish to add",
        default=None,
        items=update_component_to_add_list,
    )

    def invoke(self, context, _event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected = self.property_to_add
        if selected == "0" or selected == "":
            return {"FINISHED"}

        component = component_base.COMPONENTS[int(selected) - 1]
        component.add(context.object)

        # Redraw UI
        for area in bpy.context.window.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()
        return {"FINISHED"}
