//! This example loads the various test scenes
use bevy::prelude::*;
use bevy::reflect::TypeRegistry;
use bevy_rapier3d::physics::{NoUserData, RapierPhysicsPlugin};
use blender_bevy_toolkit::BlendLoadPlugin;

fn save_scene(world: &mut World) {
    //Create a camera
    // world.spawn().insert_bundle(PerspectiveCameraBundle {
    //     transform: Transform::from_matrix(Mat4::from_rotation_translation(
    //         Quat::from_xyzw(-0.3, -0.5, -0.3, 0.5).normalize(),
    //         Vec3::new(-13.0, 20.0, 0.0) * 6.0,
    //     )),
    //     ..Default::default()
    // });
    world
        .spawn()
        .insert_bundle(OrthographicCameraBundle::new_3d());

    // Create a Light
    world.spawn().insert_bundle(PointLightBundle {
        transform: Transform::from_translation(Vec3::new(0.0, 8.0, 0.0)),
        ..Default::default()
    });

    let type_registry = world.get_resource::<TypeRegistry>().unwrap();
    let scene = DynamicScene::from_world(&world, type_registry);

    // Scenes can be serialized like this:
    info!("{}", scene.serialize_ron(type_registry).unwrap());
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(RapierPhysicsPlugin::<NoUserData>::default())
        .add_plugin(BlendLoadPlugin::default())
        .add_startup_system(save_scene.exclusive_system())
        .run();
}
