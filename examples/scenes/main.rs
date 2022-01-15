//! This example loads the various test scenes
use bevy::prelude::*;
use bevy_rapier3d::prelude::*;
use blender_bevy_toolkit::BlendLoadPlugin;

fn spawn_scene(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut scene_spawner: ResMut<SceneSpawner>,
) {
    //Create a camera
    commands.spawn().insert_bundle(PerspectiveCameraBundle {
        transform: Transform::from_matrix(Mat4::from_rotation_translation(
            Quat::from_xyzw(-0.3, -0.5, -0.3, 0.5).normalize(),
            Vec3::new(-13.0, 20.0, 0.0) * 6.0,
        )),
        ..Default::default()
    });

    // Create a Light
    commands.spawn().insert_bundle(PointLightBundle {
        transform: Transform::from_translation(Vec3::new(0.0, 8.0, 0.0)),
        ..Default::default()
    });

    let scene_handle: Handle<DynamicScene> = asset_server.load("scenes/PhysicsTest.scn");
    scene_spawner.spawn_dynamic(scene_handle);
}

fn main() {
    println!("Running example scenes");

    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(RapierPhysicsPlugin::<NoUserData>::default())
        .add_plugin(BlendLoadPlugin::default())
        .add_startup_system(spawn_scene.system())
        .run();
}
