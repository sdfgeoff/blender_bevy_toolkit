use bevy::{
    asset::{AssetLoader, AssetPath, LoadContext},
    prelude::*,
    utils::BoxedFuture,
};
use ron;
use serde::{Deserialize, Serialize};

#[derive(Reflect, Default, Component)]
#[reflect(Component)] // this tells the reflect derive to also reflect component behaviors
pub struct BlendMaterialLoader {
    path: String,
}

pub fn blend_material_loader(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    query: Query<(&BlendMaterialLoader, Entity)>,
) {
    for (mat_loader, entity) in query.iter() {
        //println!("Loading Mesh {} for {:?}", meshloader.path, entity);
        commands.entity(entity).remove::<BlendMaterialLoader>();

        let material_handle: Handle<StandardMaterial> = asset_server.load(mat_loader.path.as_str());

        commands.entity(entity).insert(material_handle);
    }
}
use std::path::Path;

#[derive(Default)]
pub struct BlendMaterialAssetLoader;

impl AssetLoader for BlendMaterialAssetLoader {
    fn load<'a>(
        &'a self,
        bytes: &'a [u8],
        load_context: &'a mut LoadContext,
    ) -> BoxedFuture<'a, Result<(), anyhow::Error>> {
        Box::pin(async move {
            let material_raw: BlenderStandardMaterial = ron::from_str(std::str::from_utf8(bytes)?)?;

            let mut material = StandardMaterial {
                base_color: material_raw.base_color,
                emissive: material_raw.emissive,
                perceptual_roughness: material_raw.perceptual_roughness,
                metallic: material_raw.metallic,
                reflectance: material_raw.reflectance,
                double_sided: material_raw.double_sided,
                unlit: material_raw.unlit,
                alpha_mode: material_raw.alpha_mode.into(),
                ..Default::default()
            };

            let mut dependant_assets = Vec::new();

            if let Some(tex_path) = material_raw.base_color_texture {
                let path = Path::new(&tex_path);
                let asset_path = AssetPath::new_ref(path, None);
                material.base_color_texture = Some(load_context.get_handle(asset_path.clone()));
                dependant_assets.push(tex_path);
            }

            if let Some(tex_path) = material_raw.emissive_texture {
                let path = Path::new(&tex_path);
                let asset_path = AssetPath::new_ref(path, None);
                material.emissive_texture = Some(load_context.get_handle(asset_path.clone()));
                dependant_assets.push(tex_path);
            }

            if let Some(tex_path) = material_raw.metallic_roughness_texture {
                let path = Path::new(&tex_path);
                let asset_path = AssetPath::new_ref(path, None);
                material.metallic_roughness_texture =
                    Some(load_context.get_handle(asset_path.clone()));
                dependant_assets.push(tex_path);
            }

            if let Some(tex_path) = material_raw.normal_map_texture {
                let path = Path::new(&tex_path);
                let asset_path = AssetPath::new_ref(path, None);
                material.normal_map_texture = Some(load_context.get_handle(asset_path.clone()));
                dependant_assets.push(tex_path);
            }

            if let Some(tex_path) = material_raw.occlusion_texture {
                let path = Path::new(&tex_path);
                let asset_path = AssetPath::new_ref(path, None);
                material.occlusion_texture = Some(load_context.get_handle(asset_path.clone()));
                dependant_assets.push(tex_path);
            }

            let mut asset = bevy::asset::LoadedAsset::new(material);
            for path in dependant_assets {
                let path = Path::new(&path);
                let asset_path = AssetPath::new_ref(path, None);
                asset = asset.with_dependency(asset_path)
            }

            load_context.set_default_asset(asset);
            Ok(())
        })
    }

    fn extensions(&self) -> &[&str] {
        &["material"]
    }
}

#[derive(Debug, Deserialize, Serialize)]
enum BlendAlphaMode {
    Opaque,
    Mask(f32),
    Blend,
}

impl Into<AlphaMode> for BlendAlphaMode {
    fn into(self) -> AlphaMode {
        match self {
            Self::Opaque => AlphaMode::Opaque,
            Self::Blend => AlphaMode::Blend,
            Self::Mask(v) => AlphaMode::Mask(v),
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
struct BlenderStandardMaterial {
    /// Doubles as diffuse albedo for non-metallic, specular for metallic and a mix for everything
    /// in between. If used together with a base_color_texture, this is factored into the final
    /// base color as `base_color * base_color_texture_value`
    pub base_color: Color,
    pub base_color_texture: Option<String>,
    // Use a color for user friendliness even though we technically don't use the alpha channel
    // Might be used in the future for exposure correction in HDR
    pub emissive: Color,
    pub emissive_texture: Option<String>,
    /// Linear perceptual roughness, clamped to [0.089, 1.0] in the shader
    /// Defaults to minimum of 0.089
    /// If used together with a roughness/metallic texture, this is factored into the final base
    /// color as `roughness * roughness_texture_value`
    pub perceptual_roughness: f32,
    /// From [0.0, 1.0], dielectric to pure metallic
    /// If used together with a roughness/metallic texture, this is factored into the final base
    /// color as `metallic * metallic_texture_value`
    pub metallic: f32,
    pub metallic_roughness_texture: Option<String>,
    /// Specular intensity for non-metals on a linear scale of [0.0, 1.0]
    /// defaults to 0.5 which is mapped to 4% reflectance in the shader
    pub reflectance: f32,
    pub normal_map_texture: Option<String>,
    pub occlusion_texture: Option<String>,
    pub double_sided: bool,
    pub unlit: bool,
    pub alpha_mode: BlendAlphaMode,
}
