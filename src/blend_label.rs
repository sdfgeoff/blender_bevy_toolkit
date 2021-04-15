use bevy::prelude::*;

/// Component that contains the name of the object
#[derive(Reflect, Default)]
#[reflect(Component)]
pub struct BlendLabel {
    pub name: String,
}
