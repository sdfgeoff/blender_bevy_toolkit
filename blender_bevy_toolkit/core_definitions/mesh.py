import bpy
import struct
import hashlib
import os
from blender_bevy_toolkit.component_base import (
    ComponentRepresentation,
    register_component,
)

import logging
from blender_bevy_toolkit import jdict

logger = logging.getLogger(__name__)


@register_component
class Mesh:
    def encode(config, obj):
        """Returns a ComponentRepresentation to encode this component
        into a scene file"""
        assert Mesh.is_present(obj)

        mesh_data = Mesh.serialize_mesh(obj)

        hash = hashlib.md5()
        hash.update(mesh_data)
        hash_text = hash.hexdigest()

        mesh_output_file = os.path.join(
            config["mesh_output_folder"],
            "{}.mesh".format(
                hash_text,
            ),
        )
        if not os.path.exists(mesh_output_file):
            logger.info(jdict(event="writing_mesh", path=mesh_output_file))
            open(mesh_output_file, "wb").write(mesh_data)

        path = os.path.relpath(mesh_output_file, config["output_folder"])

        # TODO: The rust side doesn't support relative paths, so for now we have to hardcode this
        path = os.path.join("scenes", path)

        return ComponentRepresentation(
            "blender_bevy_toolkit::blend_mesh::BlendMeshLoader", {"path": path}
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return obj.type == "MESH"

    # INTERNAL FUNCTIONS

    def serialize_mesh(obj):
        depsgraph = bpy.context.view_layer.depsgraph
        depsgraph.update()

        eval_object = obj.evaluated_get(depsgraph)
        mesh = eval_object.to_mesh(
            # preserve_all_data_layers=preserve_vertex_groups,
            depsgraph=depsgraph
        )

        mesh.calc_loop_triangles()
        mesh.calc_normals_split()

        verts = []
        normals = []
        indices = []
        uv0 = []

        dedup_data_lookup = {}

        for loop_tri in mesh.loop_triangles:
            triangle_indices = []

            for loop_index in loop_tri.loops:
                loop = mesh.loops[loop_index]

                vert = mesh.vertices[loop.vertex_index]
                position = tuple(vert.co)
                normal = tuple(loop.normal)

                if mesh.uv_layers:

                    uv_raw = mesh.uv_layers[0].data[loop_index].uv
                    uv = (uv_raw[0], uv_raw[1])
                else:
                    uv = (0.0, 0.0)

                dedup = (position, normal, uv)
                if dedup not in dedup_data_lookup:
                    index = len(verts)
                    verts.append(position)
                    normals.append(normal)
                    uv0.append(uv)
                    dedup_data_lookup[dedup] = index
                else:
                    index = dedup_data_lookup[dedup]

                triangle_indices.append(index)
            indices.append(tuple(triangle_indices))

        eval_object.to_mesh_clear()

        # Output our file
        # We start off with a header containing data about the file
        out_data = b""
        out_data += struct.pack("H", len(verts))
        out_data += struct.pack("H", len(indices))

        # We don't need len(normals) because:
        assert len(normals) == len(verts)
        assert len(uv0) == len(verts)

        # Now we can pack all our data:
        for vert in verts:
            out_data += struct.pack("fff", *vert)
        for normal in normals:
            out_data += struct.pack("fff", *normal)
        for uv in uv0:
            out_data += struct.pack("ff", *uv)
        for index in indices:
            out_data += struct.pack("III", *index)

        return out_data

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
