//! This example loads the various test scenes
use bevy::prelude::*;
use bevy_rapier3d::physics::{NoUserData, RapierPhysicsPlugin};
use bevy_rapier3d::prelude::*;
use blender_bevy_toolkit::BlendLoadPlugin;
use std::env;


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

    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        println!("Please specify a scene file to load. For example:\n cargo run --example scenes -- scenes/Heirarchy.scn");
        std::process::exit(1);
    }

    println!("Running scene: {}", args[1]);

    let scene_handle: Handle<DynamicScene> = asset_server.load(args[1].as_str());
    scene_spawner.spawn_dynamic(scene_handle);
}


fn setup_physics(mut physics_config: ResMut<RapierConfiguration>) {
    physics_config.gravity.y = 0.0;
    physics_config.gravity.z = -9.8;
}


fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(RapierPhysicsPlugin::<NoUserData>::default())
        .add_plugin(BlendLoadPlugin::default())
        .add_startup_system(spawn_scene.system())
        .add_system(setup_physics.system())
        .run();
}
