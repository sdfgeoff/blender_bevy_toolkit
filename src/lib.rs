use bevy::prelude::*;

pub mod blend_collection;
pub mod blend_label;
pub mod blend_material;
pub mod blend_mesh;
pub mod rapier_physics;

#[derive(Default)]
pub struct BlendLoadPlugin {}

impl BlendLoadPlugin {
    pub fn new() -> Self {
        Self {}
    }
}

impl Plugin for BlendLoadPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<blend_label::BlendLabel>();
        app.register_type::<blend_collection::BlendCollectionLoader>();
        app.register_type::<blend_mesh::BlendMeshLoader>();
        app.register_type::<blend_material::BlendMaterialLoader>();
        app.register_type::<rapier_physics::RigidBodyDescription>();
        app.register_type::<rapier_physics::ColliderDescription>();

        app.init_asset_loader::<blend_mesh::BlendMeshAssetLoader>();
        app.init_asset_loader::<blend_material::BlendMaterialAssetLoader>();
        //removed deprecated .system() call, as it is no longer needed
        app.add_system(blend_collection::blend_collection_loader);
        app.add_system(blend_mesh::blend_mesh_loader);
        app.add_system(blend_material::blend_material_loader);
        app.add_system(rapier_physics::body_description_to_builder);
        app.add_system(rapier_physics::collider_description_to_builder);
    }
}
