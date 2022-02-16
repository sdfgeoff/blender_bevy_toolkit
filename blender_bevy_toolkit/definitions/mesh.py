import bpy
import struct
import hashlib
import os
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit import rust_types

import logging
from blender_bevy_toolkit import jdict
import bmesh

logger = logging.getLogger(__name__)


@register_component
class Mesh(ComponentBase):
    def encode(config, obj):
        """Returns a Component to encode this component
        into a scene file"""
        assert Mesh.is_present(obj)

        mesh_data = serialize_mesh(obj)

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

        return rust_types.Map(
            type="blender_bevy_toolkit::blend_mesh::BlendMeshLoader",
            struct=rust_types.Map(path=rust_types.Str(path)),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return obj.type == "MESH"

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass


def serialize_mesh(obj):
    depsgraph = bpy.context.view_layer.depsgraph
    depsgraph.update()

    eval_object = obj.evaluated_get(depsgraph)
    mesh = eval_object.to_mesh(
        # preserve_all_data_layers=preserve_vertex_groups,
        depsgraph=depsgraph
    )

    triangulate_ngons(mesh)
    mesh.calc_loop_triangles()
    mesh.calc_normals_split()
    mesh.calc_tangents()

    verts = []
    normals = []
    indices = []
    uv0 = []
    tangents = []

    dedup_data_lookup = {}

    for loop_tri in mesh.loop_triangles:
        triangle_indices = []

        for loop_index in loop_tri.loops:
            loop = mesh.loops[loop_index]

            vert = mesh.vertices[loop.vertex_index]
            position = tuple(vert.co)
            normal = tuple(loop.normal)
            tangent = tuple(loop.tangent)

            if mesh.uv_layers:

                uv_raw = mesh.uv_layers[0].data[loop_index].uv
                uv = (uv_raw[0], uv_raw[1])
            else:
                uv = (0.0, 0.0)

            dedup = (position, normal, uv, tangent)
            if dedup not in dedup_data_lookup:
                index = len(verts)
                verts.append(position)
                normals.append(normal)
                uv0.append(uv)
                tangents.append(tangent)
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
    assert len(tangents) == len(verts)

    # Now we can pack all our data:
    for vert in verts:
        out_data += struct.pack("fff", *vert)
    for normal in normals:
        out_data += struct.pack("fff", *normal)
    for tangent in tangents:
        out_data += struct.pack(
            "ffff", *tangent, 0.0
        )  # Bevy expects tangents to be a vec4 because https://github.com/bevyengine/bevy/issues/3604
    for uv in uv0:
        out_data += struct.pack("ff", *uv)
    for index in indices:
        out_data += struct.pack("III", *index)

    return out_data


def triangulate_ngons(mesh):
    """Triangulate n-gons in a mesh. Copied from blender-godot-exporter used
    under ... GPL like all this python is by virtue of being a blender addon"""
    tri_mesh = bmesh.new()
    tri_mesh.from_mesh(mesh)
    ngons = [face for face in tri_mesh.faces if len(face.verts) > 4]
    bmesh.ops.triangulate(tri_mesh, faces=ngons, quad_method="ALTERNATE")
    tri_mesh.to_mesh(mesh)
    tri_mesh.free()
    mesh.update()
