import bpy
import struct
import hashlib
import os
import shutil
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
            serialize_material(config, obj.data.materials[0])
            if obj.data.materials and obj.data.materials[0] is not None
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


def col_to_ron(col):
    return ron.EnumValue(
        "RgbaLinear", ron.Struct(red=col[0], green=col[1], blue=col[2], alpha=col[3])
    )


DEFAULT_MATERIAL = ron.encode(
    ron.Struct(
        base_color=col_to_ron([0.8, 0.8, 0.8, 1.0]),
        base_color_texture=ron.EnumValue("None"),
        emissive=col_to_ron((0.0, 0.0, 0.0, 1.0)),
        emissive_texture=ron.EnumValue("None"),
        perceptual_roughness=ron.Float(0.5),
        metallic=ron.Float(0.5),
        metallic_roughness_texture=ron.EnumValue("None"),
        reflectance=ron.Float(0.5),
        normal_map_texture=ron.EnumValue("None"),
        occlusion_texture=ron.EnumValue("None"),
        double_sided=ron.Bool(False),
        unlit=ron.Bool(False),
        alpha_mode=ron.EnumValue("Opaque"),
    )
).encode("utf-8")


def serialize_material(config, material):
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
        # In blender, the base color is overwritten by the texture
        base_color_input = main_node.inputs["Base Color"]
        if len(base_color_input.links) == 0:
            base_color = col_to_ron(base_color_input.default_value)
        else:
            base_color = col_to_ron([1.0, 1.0, 1.0, 1.0])
        base_color_texture = get_image_from_node_socket(config, base_color_input)

        # In blender, the emissive color is overwritten by the texture
        emmissive_color_input = main_node.inputs["Emission"]
        if len(emmissive_color_input.links) == 0:
            emissive_color = col_to_ron(emmissive_color_input.default_value)
        else:
            emissive_color = col_to_ron([1.0, 1.0, 1.0, 1.0])
        emissive_color_texture = get_image_from_node_socket(
            config, emmissive_color_input
        )

        # Roughness + metallic are combined
        metallic_node_input = main_node.inputs["Metallic"]
        if len(metallic_node_input.links) == 0:
            metallic = ron.Float(metallic_node_input.default_value)
            use_metallic_texture = False
        else:
            metallic = ron.Float(1.0)
            use_metallic_texture = True

        roughness_node_input = main_node.inputs["Roughness"]
        if len(roughness_node_input.links) == 0:
            roughness = ron.Float(roughness_node_input.default_value)
            use_roughness_texture = False
        else:
            roughness = ron.Float(1.0)
            use_roughness_texture = True

        if use_roughness_texture != use_metallic_texture:
            raise Exception(
                "Either both or none of [metallic, roughness] must be texture driven"
            )
        elif use_roughness_texture and use_metallic_texture:

            if (
                roughness_node_input.links[0].from_node
                != metallic_node_input.links[0].from_node
            ):
                raise Exception("Roughness and Metallic must come from the same node")

            sep_node = roughness_node_input.links[0].from_node
            if sep_node.type != "SEPRGB":
                raise Exception(
                    "Roughness and Metallic must be connected to a Separate RGB Node"
                )

            if roughness_node_input.links[0].from_socket.name != "G":
                raise Exception("Roughness should be connected to the Green Channel")
            if metallic_node_input.links[0].from_socket.name != "R":
                raise Exception("Metallic should be connected to the Red Channel")

            met_rough_tex = get_image_from_node_socket(config, sep_node.inputs["Image"])
        else:
            met_rough_tex = ron.EnumValue("None")

        return ron.encode(
            ron.Struct(
                base_color=base_color,
                base_color_texture=base_color_texture,
                emissive=emissive_color,
                emissive_texture=emissive_color_texture,
                perceptual_roughness=roughness,
                metallic=metallic,
                metallic_roughness_texture=met_rough_tex,
                reflectance=ron.Float(main_node.inputs["Specular"].default_value),
                normal_map_texture=get_normal_map(config, main_node.inputs["Normal"]),
                occlusion_texture=ron.EnumValue(
                    "None"
                ),  # Blenders node graph doesn't have a neat way to represent this, so we'll leave it for now
                double_sided=not material.use_backface_culling,
                unlit=ron.Bool(False),
                alpha_mode=ron.EnumValue("Opaque"),  # TODO
            )
        ).encode("utf-8")

    else:
        raise Exception(
            f"Unable to export node type {main_node.type} from material {material.name}"
        )


def get_normal_map(config, socket):
    """Read through blender's normal map node"""
    if len(socket.links) == 0:
        return ron.EnumValue("None")

    normal_map_node = socket.links[0].from_node
    if normal_map_node.type != "NORMAL_MAP":
        raise Exception(
            "Expected node feeding into surface normal to be a Vector -> Normal Map node"
        )

    return get_image_from_node_socket(config, normal_map_node.inputs["Color"])


def get_image_from_node_socket(config, socket):
    """Copies image to textures folder"""
    if len(socket.links) == 0:
        return ron.EnumValue("None")
    elif len(socket.links) > 1:
        raise Exception("Muliple inputs to image slot???")

    source = socket.links[0].from_node
    if source.type != "TEX_IMAGE":
        raise Exception("Expected image input to socket", socket.name)

    image = source.image
    if source.image is None:
        return ron.EnumValue("None")

    current_path = bpy.path.abspath(source.image.filepath, library=source.image.library)
    hashval = hashimage(image)
    extension = {
        "BMP": "bmp",
        # "IRIS": "",
        "PNG": "png",
        "JPEG": "jpg",
        # "JPEG2000": "",
        "TARGA": "tga",
        # "TARGA_RAW": "",
        # "CINEON": "",
        # "DPX": "",
        # "OPEN_EXR_MULTILAYER": "",
        # "OPEN_EXR": "",
        # "HDR": "",
        "TIFF": "tiff",
        "AVI_JPEG": "avi",
        "AVI_RAW": "avi",
        # "FFMPEG": "",
    }[source.image.file_format]

    image_output_path = os.path.join(
        config["texture_output_folder"], f"{hashval}.{extension}"
    )
    shutil.copyfile(current_path, image_output_path)

    path = os.path.relpath(image_output_path, config["output_folder"])
    # TODO: The rust side doesn't support relative paths, so for now we have to hardcode this
    path = os.path.join("scenes", path)

    return ron.EnumValue("Some", ron.Tuple(path))


def hashimage(image):
    hash = hashlib.md5()
    hash.update(
        open(bpy.path.abspath(image.filepath, library=image.library), "rb").read()
    )
    hash_text = hash.hexdigest()
    return hash_text
