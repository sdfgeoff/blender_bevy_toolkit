use bevy::{
    asset::{AssetLoader, LoadContext},
    prelude::*,
    render::{mesh::Indices},
    utils::BoxedFuture,
};
use std::convert::TryInto;
use bevy::render::render_resource::PrimitiveTopology;

#[derive(Reflect, Default, Component)]
#[reflect(Component)] // this tells the reflect derive to also reflect component behaviors
pub struct BlendMeshLoader {
    path: String,
}

type FVec3Arr = Vec<[f32; 3]>;

pub fn blend_mesh_loader(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    query: Query<(&BlendMeshLoader, Entity)>,
) {
    for (meshloader, entity) in query.iter() {
        //println!("Loading Mesh {} for {:?}", meshloader.path, entity);
        commands.entity(entity).remove::<BlendMeshLoader>();

        let mesh_handle: Handle<Mesh> = asset_server.load(meshloader.path.as_str());

        let material = materials.add(StandardMaterial {
            base_color: Color::rgb(0.8, 0.7, 0.6),
            ..Default::default()
        });

        let bundle = PbrBundle {
            mesh: mesh_handle,
            material,
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(bundle);
    }
}

#[derive(Default)]
pub struct BlendMeshAssetLoader;

impl AssetLoader for BlendMeshAssetLoader {
    fn load<'a>(
        &'a self,
        bytes: &'a [u8],
        load_context: &'a mut LoadContext,
    ) -> BoxedFuture<'a, Result<(), anyhow::Error>> {
        Box::pin(async move {
            let mesh = load_mesh(bytes);
            let asset = bevy::asset::LoadedAsset::new(mesh);

            load_context.set_default_asset(asset);
            Ok(())
        })
    }

    fn extensions(&self) -> &[&str] {
        &["mesh"]
    }
}

pub fn load_mesh(data: &[u8]) -> Mesh {
    let (indices, positions, normals, uv0s) = extact_buffers_from_mesh(data);
    let indices = Indices::U32(indices);

    let mut mesh = Mesh::new(PrimitiveTopology::TriangleList);
    mesh.set_indices(Some(indices));
    mesh.set_attribute(Mesh::ATTRIBUTE_POSITION, positions);
    mesh.set_attribute(Mesh::ATTRIBUTE_NORMAL, normals);
    mesh.set_attribute(Mesh::ATTRIBUTE_UV_0, uv0s);

    mesh
}

/// Reads a f32 from a buffer
fn get_f32(arr: &[u8]) -> f32 {
    f32::from_le_bytes(arr[0..4].try_into().unwrap())
}
/// Reads a u16 from a buffer
fn get_u32(arr: &[u8]) -> u32 {
    u32::from_le_bytes(arr[0..4].try_into().unwrap())
}

/// Converts a slice of u8's into a vec of f32;s
fn parse_vec3_array(data: &[u8], num_elements: usize) -> Vec<[f32; 3]> {
    let mut out_array = Vec::with_capacity(num_elements);
    for i in 0..num_elements {
        out_array.push([
            get_f32(&data[i * 12..]),
            get_f32(&data[(i * 12 + 4)..]),
            get_f32(&data[(i * 12 + 8)..]),
        ]);
    }
    out_array
}
/// Converts a slice of u8's into a vec of u16's
fn parse_u32_array(data: &[u8], num_elements: usize) -> Vec<u32> {
    let mut out_array = Vec::with_capacity(num_elements);
    for i in 0..num_elements {
        out_array.push(get_u32(&data[i * 4..]));
    }
    out_array
}

/// Converts the bytes of a binary stl file into a vector of face indices,
/// vertices and vertex normals.
/// Expects correctly formatted STL files
fn extact_buffers_from_mesh(mesh: &[u8]) -> (Vec<u32>, FVec3Arr, FVec3Arr, FVec3Arr) {
    let num_verts = u16::from_le_bytes(mesh[0..2].try_into().unwrap()) as usize;
    let num_faces = u16::from_le_bytes(mesh[2..4].try_into().unwrap()) as usize;

    let verts_start = 4;
    let normals_start = verts_start + num_verts * 4 * 3;
    let uv0_start = normals_start + num_verts * 4 * 3;
    let indices_start = uv0_start + num_verts * 4 * 3;

    let positions = parse_vec3_array(&mesh[verts_start..], num_verts);
    let normals = parse_vec3_array(&mesh[normals_start..], num_verts);
    let uv0 = parse_vec3_array(&mesh[uv0_start..], num_verts);
    let indices = parse_u32_array(&mesh[indices_start..], num_faces * 3);

    (indices, positions, normals, uv0)
}
