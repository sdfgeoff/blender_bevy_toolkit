use bevy::prelude::*;
use bevy_rapier3d::na::{Isometry3, Point3};
use bevy_rapier3d::prelude::*;
use bevy_rapier3d::rapier::geometry::SharedShape;
use std::convert::TryInto;

use smallvec;

#[derive(Reflect, Default, Component)]
#[reflect(Component)]
/// A RigidBodyDescription is only present until the body_description_to_builder system runs,
/// upon which it is converted to a rapier::dynamics::RigidBodyBuilder with matching properties.
/// Then the bevy rapier plugin converts that into a RigidBodyHandle component for the purpose
/// of actually simulating it.
pub struct RigidBodyDescription {
    /// Because we can't export enums yet, this is encoded as a u8
    ///  0 => dynamic
    ///  1 => static
    ///  2 => kinematic position based
    ///  3 => kinematic velocity based
    pub body_status: u8,

    /// Damp the rotation of the body
    pub damping_angular: f32,
    /// Damp the linear of the body
    pub damping_linear: f32,

    /// Enable continous collision detection - good for fast moving objects but increases
    /// processor load
    pub ccd_enable: bool,

    /// Allow the physics engine to "sleep" the body when it's velocity is low. This helps
    /// save processing time if there are lots of nearly-static-bodies
    pub sleep_allow: bool,

    pub lock_translation: glam::i32::IVec3,
    pub lock_rotation: glam::i32::IVec3,
}

/// Converts a RigidBodyDescription into a rapier::dynamics::RigidBodyBuilder. This allows
/// RigidBodyBuilders to be created from a file using bevies Reflection system and scene format
pub fn body_description_to_builder(
    mut commands: Commands,
    body_desc_query: Query<(&RigidBodyDescription, Entity, &Transform)>,
) {
    for (body_desc, entity, transform) in body_desc_query.iter() {
        commands.entity(entity).remove::<RigidBodyDescription>();

        //updated body_status to store updated RigidBody types

        let body_status = match body_desc.body_status {
            0 => RigidBody::Dynamic,
            1 => RigidBody::Fixed,
            2 => RigidBody::KinematicPositionBased,
            3 => RigidBody::KinematicVelocityBased,
            _ => RigidBody::Dynamic,
        };

        //updated lock flags to store LockedAxes to how they are used in the newest version of rapier

        let lock_flags = {
            let mut flags = LockedAxes::empty();
            if body_desc.lock_translation.x != 0 {
                flags.insert(LockedAxes::TRANSLATION_LOCKED_X);
            }
            if body_desc.lock_translation.y != 0 {
                flags.insert(LockedAxes::TRANSLATION_LOCKED_Y);
            }
            if body_desc.lock_translation.z != 0 {
                flags.insert(LockedAxes::TRANSLATION_LOCKED_Z);
            }
            if body_desc.lock_rotation.x != 0 {
                flags.insert(LockedAxes::ROTATION_LOCKED_X);
            }
            if body_desc.lock_rotation.y != 0 {
                flags.insert(LockedAxes::ROTATION_LOCKED_Y);
            }
            if body_desc.lock_rotation.z != 0 {
                flags.insert(LockedAxes::ROTATION_LOCKED_Z);
            }

            flags
        };

        //new method of inserting rigid bodies into entities
        if body_desc.ccd_enable{
            commands
                .entity(entity)
                .insert(body_status)
                .insert(lock_flags)
                .insert(Damping {
                    linear_damping: body_desc.damping_linear,
                    angular_damping: body_desc.damping_angular
                })
                .insert(Ccd::enabled());
        }
        else {
            commands
                .entity(entity)
                .insert(body_status)
                .insert(lock_flags)
                .insert(Damping {
                    linear_damping: body_desc.damping_linear,
                    angular_damping: body_desc.damping_angular
                })
                .insert(Ccd::disabled());
        }
    }
}

#[derive(Reflect, Default, Debug, Component)]
#[reflect(Component)]
pub struct ColliderDescription {
    friction: f32,
    restitution: f32,
    is_sensor: bool,
    density: f32,

    // Transform to the center of the shape. This allows you to (eg) define a sphere that is not
    // centered at the object origin.
    centroid_translation: Vec3,

    /// At the moment, you can't use an enum with bevy's Reflect derivation.
    /// So instead we're doing this the old fashioned way.
    ///
    /// collider_shape = 0: Sphere collider
    ///     collider_shape_data: f32 = radius
    collider_shape: u8,
    collider_shape_data: smallvec::SmallVec<[u8; 8]>,
}

/// Reads a f32 from a buffer
fn get_f32(arr: &[u8]) -> f32 {
    f32::from_le_bytes(arr[0..4].try_into().unwrap())
}

pub fn collider_description_to_builder(
    mut commands: Commands,
    collider_desc_query: Query<(&ColliderDescription, Entity)>,
) {
    for (collider_desc, entity) in collider_desc_query.iter() {
        commands.entity(entity).remove::<ColliderDescription>();

        let shape = match collider_desc.collider_shape {
            0 => {
                // Sphere
                let radius = get_f32(&collider_desc.collider_shape_data[0..]);
                SharedShape::ball(radius)
            }
            1 => {
                // Capsule
                let half_height = get_f32(&collider_desc.collider_shape_data[0..]);
                let radius = get_f32(&collider_desc.collider_shape_data[4..]);
                SharedShape::capsule(
                    Point3::new(0.0, 0.0, half_height),
                    Point3::new(0.0, 0.0, -half_height),
                    radius,
                )
            }
            2 => {
                // Box
                SharedShape::cuboid(
                    get_f32(&collider_desc.collider_shape_data[0..]),
                    get_f32(&collider_desc.collider_shape_data[4..]),
                    get_f32(&collider_desc.collider_shape_data[8..]),
                )
            } //fixed typo
            _ => panic!("Unknown collider shape"),
        };

        //new method for adding inserting Colliders and their various properties to entities

        commands.entity(entity)
        .insert(Collider::from(shape))
        .insert(Sensor(collider_desc.is_sensor))
        .insert(Friction {
            coefficient: collider_desc.friction,
            ..Default::default()
        })
        .insert(Restitution {
            coefficient: collider_desc.restitution,
            ..Default::default()
        })
        .insert(Transform::from_xyz(
            collider_desc.centroid_translation.x,
            collider_desc.centroid_translation.y,
            collider_desc.centroid_translation.z
        ))
        .insert(ColliderMassProperties::Density(collider_desc.density));
    }
}
