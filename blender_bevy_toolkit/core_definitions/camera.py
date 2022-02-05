# import bpy
# from blender_bevy_toolkit.component_base import (
#     ComponentRepresentation,
#     register_component,
#     ComponentBase,
# )


# import logging
# from blender_bevy_toolkit import jdict, utils

# logger = logging.getLogger(__name__)


# """
# (
#     entity: 0,
#     components: [
#       {
#         "type": "bevy_render::camera::camera::Camera",
#         "struct": {
#           "projection_matrix": {
#             "type": "glam::mat4::Mat4",
#             "value": (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
#           },
#           "name": {
#             "type": "core::option::Option<alloc::string::String>",
#             "value": Some("camera_3d"),
#           },
#           "near": {
#             "type": "f32",
#             "value": 0.1,
#           },
#           "far": {
#             "type": "f32",
#             "value": 1000.0,
#           },
#         },
#       },
#       {
#         "type": "bevy_render::camera::projection::PerspectiveProjection",
#         "struct": {
#           "fov": {
#             "type": "f32",
#             "value": 0.7853982,
#           },
#           "aspect_ratio": {
#             "type": "f32",
#             "value": 1.0,
#           },
#           "near": {
#             "type": "f32",
#             "value": 0.1,
#           },
#           "far": {
#             "type": "f32",
#             "value": 1000.0,
#           },
#         },
#       },
#       {
#         "type": "bevy_render::view::visibility::VisibleEntities",
#         "struct": {},
#       },
#       {
#         "type": "bevy_render::primitives::Frustum",
#         "struct": {},
#       },
#     ],
#   ),
# """


# @register_component
# class Camera(ComponentBase):
#     @staticmethod
#     def encode(config, obj):
#         """
#         {
#             "type": "bevy_render::camera::camera::Camera",
#             "struct": {
#             "projection_matrix": {
#                 "type": "glam::mat4::Mat4",
#                 "value": (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
#             },
#             "name": {
#                 "type": "core::option::Option<alloc::string::String>",
#                 "value": Some("camera_3d"),
#             },
#             "near": {
#                 "type": "f32",
#                 "value": 0.1,
#             },
#             "far": {
#                 "type": "f32",
#                 "value": 1000.0,
#             },
#             },
#         },
#         """
#         return ComponentRepresentation(
#             "bevy_render::camera::camera::Camera",
#             {
#                 # "projection_matrix", # Auto-computed from projection component (I hope)
#                 "near": utils.F32(obj.data.clip_start),
#                 "far": utils.F32(obj.data.clip_end),
#                 # "name": obj.data.name, # Why do camera's have names?
#             },
#         )

#     @staticmethod
#     def is_present(obj):
#         return obj.type == "CAMERA"

#     @staticmethod
#     def register():
#         bpy.utils.register_class(CameraPanel)

#     @staticmethod
#     def unregister():
#         bpy.utils.unregister_class(CameraPanel)

#     @staticmethod
#     def can_add(obj):
#         return False


# class CameraPanel(bpy.types.Panel):
#     bl_idname = "OBJECT_PT_camera_properties"
#     bl_label = "BevyCamera"
#     bl_space_type = "PROPERTIES"
#     bl_region_type = "WINDOW"
#     bl_context = "physics"

#     @classmethod
#     def poll(cls, context):
#         return Camera.is_present(context.object)

#     def draw(self, context):
#         row = self.layout.row()
#         row.label(text="Renders the scene")

#         row = self.layout.row()
#         row.prop(context.object.data, "clip_start", text="Near")
#         row = self.layout.row()
#         row.prop(context.object.data, "clip_end", text="Far")


# # Supporting classes
# @register_component
# class VisibleEntities(ComponentBase):
#     @staticmethod
#     def encode(config, obj):
#         return ComponentRepresentation(
#             "bevy_render::view::visibility::VisibleEntities", {}
#         )

#     @staticmethod
#     def is_present(obj):
#         return Camera.is_present(obj)

#     @staticmethod
#     def register():
#         pass

#     @staticmethod
#     def unregister():
#         pass

#     @staticmethod
#     def can_add(obj):
#         return False


# @register_component
# class Frustum(ComponentBase):
#     @staticmethod
#     def encode(config, obj):
#         return ComponentRepresentation("bevy_render::primitives::Frustum", {})

#     @staticmethod
#     def is_present(obj):
#         return Camera.is_present(obj)

#     @staticmethod
#     def register():
#         pass

#     @staticmethod
#     def unregister():
#         pass

#     @staticmethod
#     def can_add(obj):
#         return False
