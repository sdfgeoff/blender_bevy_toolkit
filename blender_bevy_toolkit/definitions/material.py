import bpy
import struct
import hashlib
import os
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit.rust_types import ron, Map, Str

import logging
from blender_bevy_toolkit import jdict

logger = logging.getLogger(__name__)


@register_component
class Material(ComponentBase):
    def encode(config, obj):
        """Saves an auxilary file containing material data and a component
        that references it"""
        assert Material.is_present(obj)

        material_data = (
            serialize_material(obj.data.materials[0])
            if obj.data.materials
            else DEFAULT_MATERIAL
        )

        hash = hashlib.md5()
        hash.update(material_data)
        hash_text = hash.hexdigest()

        material_output_file = os.path.join(
            config["material_output_folder"],
            "{}.material".format(
                hash_text,
            ),
        )
        if not os.path.exists(material_output_file):
            logger.info(jdict(event="writing_material", path=material_output_file))
            open(material_output_file, "wb").write(material_data)

        path = os.path.relpath(material_output_file, config["output_folder"])

        # TODO: The rust side doesn't support relative paths, so for now we have to hardcode this
        path = os.path.join("scenes", path)

        return Map(
            type="blender_bevy_toolkit::blend_material::BlendMaterialLoader",
            struct=Map(path=Str(path)),
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


DEFAULT_MATERIAL = ron.encode(
    ron.Struct(
        base_color=ron.Tuple(1.0, 0.0, 1.0, 1.0),
        unlit=ron.Bool(True),
    )
).encode("utf-8")


def serialize_material(material):
    """
    pub struct StandardMaterial {
        /// Doubles as diffuse albedo for non-metallic, specular for metallic and a mix for everything
        /// in between. If used together with a base_color_texture, this is factored into the final
        /// base color as `base_color * base_color_texture_value`
        pub base_color: Color,
        pub base_color_texture: Option<Handle<Image>>,
        // Use a color for user friendliness even though we technically don't use the alpha channel
        // Might be used in the future for exposure correction in HDR
        pub emissive: Color,
        pub emissive_texture: Option<Handle<Image>>,
        /// Linear perceptual roughness, clamped to [0.089, 1.0] in the shader
        /// Defaults to minimum of 0.089
        /// If used together with a roughness/metallic texture, this is factored into the final base
        /// color as `roughness * roughness_texture_value`
        pub perceptual_roughness: f32,
        /// From [0.0, 1.0], dielectric to pure metallic
        /// If used together with a roughness/metallic texture, this is factored into the final base
        /// color as `metallic * metallic_texture_value`
        pub metallic: f32,
        pub metallic_roughness_texture: Option<Handle<Image>>,
        /// Specular intensity for non-metals on a linear scale of [0.0, 1.0]
        /// defaults to 0.5 which is mapped to 4% reflectance in the shader
        pub reflectance: f32,
        pub normal_map_texture: Option<Handle<Image>>,
        pub occlusion_texture: Option<Handle<Image>>,
        pub double_sided: bool,
        pub unlit: bool,
        pub alpha_mode: AlphaMode,
    }

    """
    output_node = material.node_tree.get_output_node("ALL")

    surface_socket = output_node.inputs["Surface"]
    if len(surface_socket.links) != 1:
        raise Exception("Expected exactly one surface link")

    main_node = surface_socket.links[0].from_node

    if main_node.type == "BSDF_PRINCIPLED":
        return ron.encode(
            ron.Struct(
                base_color=ron.Tuple(*main_node.inputs["Base Color"].default_value),
                base_color_texture=ron.EnumValue("None"),  # TODO
                emisssive=ron.Tuple(*main_node.inputs["Emission"].default_value),
                emisssive_texture=ron.EnumValue("None"),  # TODO
                perceptual_roughness=ron.Float(
                    main_node.inputs["Roughness"].default_value
                ),
                metallic=ron.Float(main_node.inputs["Metallic"].default_value),
                metallic_roughness_texture=ron.EnumValue("None"),  # TODO
                reflectance=ron.Float(main_node.inputs["Specular"].default_value),
                normal_map_texture=ron.EnumValue("None"),  # TODO
                occlusion_texture=ron.EnumValue("None"),  # TODO
                double_sided=not material.use_backface_culling,
                unlit=ron.Bool(False),
                alpha_mode=ron.EnumValue("Opaque"),  # TODO
            )
        ).encode("utf-8")

    else:
        raise Exception(
            f"Unable to export node type {main_node.type} from material {material.name}"
        )

    return b"Test"
