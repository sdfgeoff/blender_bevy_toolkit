//! This example loads the various test scenes
use bevy::input::{keyboard::KeyboardInput, ElementState};
use bevy::prelude::*;
use bevy_rapier3d::physics::{NoUserData, RapierPhysicsPlugin};
use bevy_rapier3d::prelude::*;
use blender_bevy_toolkit::BlendLoadPlugin;

const SCENE_DIR: &'static str = "./assets/scenes";

struct SceneHandler {
    scene_list: Vec<String>,
    selected_scene_name: String,
    current_scene_name: Option<String>,
}

#[derive(Component)]
struct Preserve {}

#[derive(Component)]
struct SceneListTag {}
#[derive(Component)]
struct CurrentSceneTag {}

/// Scan for ".scn" files in the SCENE_DIR folder
fn read_scene_list() -> Vec<String> {
    use std::fs;
    let paths = fs::read_dir(SCENE_DIR).unwrap();

    let path_list = paths
        .filter_map(|p| {
            let path = p.unwrap().path();
            if path.extension() == Some(std::ffi::OsStr::new("scn")) {
                let string_path = path.to_str().unwrap().to_string();
                let local_path = string_path.replace("assets/", "");
                return Some(local_path);
            }
            None
        })
        .collect();
    info!("Found scene paths: {:?}", path_list);
    return path_list;
}

/// Handle keyboard events
fn key_handler(
    mut keyboard_input_events: EventReader<KeyboardInput>,
    mut scene_handler: ResMut<SceneHandler>,
    asset_server: Res<AssetServer>,
    mut scene_spawner: ResMut<SceneSpawner>,
    entities: Query<Entity, Without<Preserve>>,
    mut commands: Commands,
) {
    for event in keyboard_input_events.iter() {
        if event.state == ElementState::Released {
            // Reload list of scenes
            if event.key_code == Some(KeyCode::R) {
                scene_handler.scene_list = read_scene_list();
            }

            // Load selected scene
            if event.key_code == Some(KeyCode::Return) {
                info!("Despawning entities");
                for e in entities.iter() {
                    commands.entity(e).despawn()
                }
                scene_handler.current_scene_name = None;

                info!("Loading Scene: {:?}", scene_handler.selected_scene_name);
                let scene_handle: Handle<DynamicScene> =
                    asset_server.load(&scene_handler.selected_scene_name);
                scene_spawner.spawn_dynamic(scene_handle);
                scene_handler.current_scene_name = Some(scene_handler.selected_scene_name.clone());
            }
        }
        if event.state == ElementState::Pressed {
            // Scroll through list of scenes
            if event.key_code == Some(KeyCode::Down) {
                let index = scene_handler
                    .scene_list
                    .iter()
                    .position(|s| s == &scene_handler.selected_scene_name)
                    .unwrap_or(0)
                    + 1;
                let constrained_index = index.min(scene_handler.scene_list.len() - 1);
                let new_scene_name = &scene_handler.scene_list[constrained_index];
                scene_handler.selected_scene_name = new_scene_name.clone();
            }
            if event.key_code == Some(KeyCode::Up) {
                let index = scene_handler
                    .scene_list
                    .iter()
                    .position(|s| s == &scene_handler.selected_scene_name)
                    .unwrap_or(0);
                let constrained_index = index.max(1) - 1;
                let new_scene_name = &scene_handler.scene_list[constrained_index];
                scene_handler.selected_scene_name = new_scene_name.clone();
            }
        }
    }
}

fn setup_world(
    mut physics_config: ResMut<RapierConfiguration>,
    mut ambient_light: ResMut<AmbientLight>,
) {
    ambient_light.color = Color::BLACK;
    physics_config.gravity.y = 0.0;
    physics_config.gravity.z = -9.8;
}

fn setup_ui(mut commands: Commands, asset_server: Res<AssetServer>) {
    commands
        .spawn_bundle(UiCameraBundle::default())
        .insert(Preserve {});

    commands
        .spawn_bundle(TextBundle {
            style: Style {
                align_self: AlignSelf::FlexEnd,
                ..Default::default()
            },
            // Use `Text` directly
            text: Text {
                // Construct a `Vec` of `TextSection`s
                sections: vec![
                    TextSection {
                        value: "Scenes: (S to scan again, Arrows to select, Enter to load)"
                            .to_string(),
                        style: TextStyle {
                            font: asset_server.load("DroidSans.ttf"),
                            font_size: 20.0,
                            color: Color::WHITE,
                        },
                    },
                    TextSection {
                        value: "".to_string(),
                        style: TextStyle {
                            font: asset_server.load("DroidSans.ttf"),
                            font_size: 20.0,
                            color: Color::GOLD,
                        },
                    },
                ],
                ..Default::default()
            },
            ..Default::default()
        })
        .insert(SceneListTag {})
        .insert(Preserve {});
}

fn display_scene_list(
    mut query: Query<&mut Text, With<SceneListTag>>,
    scene_handler: ResMut<SceneHandler>,
) {
    let mut scene_path_list = String::new();

    for scene_path in scene_handler.scene_list.iter() {
        let selected = scene_path == &scene_handler.selected_scene_name;

        scene_path_list += "\n";
        if selected {
            scene_path_list += "> "
        } else {
            scene_path_list += "   "
        }
        scene_path_list += scene_path;
    }

    for mut text in query.iter_mut() {
        text.sections[1].value = scene_path_list.clone();
    }
}

fn main() {
    let scene_list = read_scene_list();
    let start_scene = scene_list[0].clone();
    App::new()
        .insert_resource(ClearColor(Color::BLACK))
        .add_plugins(DefaultPlugins)
        .add_plugin(RapierPhysicsPlugin::<NoUserData>::default())
        .add_plugin(BlendLoadPlugin::default())
        .insert_resource(SceneHandler {
            scene_list: scene_list,
            selected_scene_name: start_scene,
            current_scene_name: None,
        })
        .add_startup_system(setup_world.system())
        .add_startup_system(setup_ui.system())
        .add_system(key_handler.system())
        .add_system(display_scene_list.system())
        .run();
}
