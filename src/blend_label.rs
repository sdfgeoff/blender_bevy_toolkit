use bevy::prelude::*;

/// Component that contains the name of the object
#[derive(Reflect, Default)]
#[reflect(Component)]
#[derive(Component)]
pub struct BlendLabel {
    pub name: String,
}
