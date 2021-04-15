use bevy::prelude::*;

/// This component loads another collection and spawns it as a child
/// of the entity with this component
#[derive(Reflect, Default)]
#[reflect(Component)]
pub struct BlendCollectionLoader {
    path: String,
}

pub fn blend_collection_loader(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut scene_spawner: ResMut<SceneSpawner>,
    query: Query<(&BlendCollectionLoader, Entity)>,
) {
    for (collectionloader, entity) in query.iter() {
        //println!("Loading Collection {} for {:?}", collectionloader.path, entity);
        commands.entity(entity).remove::<BlendCollectionLoader>();

        let collection_handle: Handle<DynamicScene> =
            asset_server.load(collectionloader.path.as_str());

        // let dynscene = assets_dynscene.get(collection_handle).unwrap();
        // let mut world = World::default();
        // dynscene.write_to_world(&mut world, &mut entity_map).expect("Failed to create world");
        // let scene: Scene = Scene::new(world);
        // let scene_handle: Handle<Scene> = assets_scene.add(scene);

        //TODO!!!!
        scene_spawner.spawn_dynamic(collection_handle);
    }
}
