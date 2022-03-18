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

        let isometry = Isometry3::from((transform.translation, transform.rotation));

        let body_status = match body_desc.body_status {
            0 => RigidBodyType::Dynamic,
            1 => RigidBodyType::Static,
            2 => RigidBodyType::KinematicPositionBased,
            3 => RigidBodyType::KinematicVelocityBased,
            _ => RigidBodyType::Dynamic,
        };

        let lock_flags = {
            let mut flags = RigidBodyMassPropsFlags::empty();
            if body_desc.lock_translation.x != 0 {
                flags.insert(RigidBodyMassPropsFlags::TRANSLATION_LOCKED_X);
            }
            if body_desc.lock_translation.y != 0 {
                flags.insert(RigidBodyMassPropsFlags::TRANSLATION_LOCKED_Y);
            }
            if body_desc.lock_translation.z != 0 {
                flags.insert(RigidBodyMassPropsFlags::TRANSLATION_LOCKED_Z);
            }
            if body_desc.lock_rotation.x != 0 {
                flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_X);
            }
            if body_desc.lock_rotation.y != 0 {
                flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_Y);
            }
            if body_desc.lock_rotation.z != 0 {
                flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_Z);
            }

            flags
        };

        let bundle = RigidBodyBundle {
            body_type: RigidBodyTypeComponent(body_status),
            position: RigidBodyPositionComponent(RigidBodyPosition {
                position: isometry,
                next_position: isometry,
            }),
            mass_properties: RigidBodyMassPropsComponent(RigidBodyMassProps {
                flags: lock_flags,
                ..Default::default()
            }),
            forces: RigidBodyForcesComponent(RigidBodyForces {
                ..Default::default()
            }),
            activation: Default::default(),
            damping: RigidBodyDampingComponent(RigidBodyDamping {
                linear_damping: body_desc.damping_linear,
                angular_damping: body_desc.damping_angular,
            }),
            ccd: RigidBodyCcdComponent(RigidBodyCcd {
                ccd_enabled: body_desc.ccd_enable,
                ..Default::default()
            }),
            ..Default::default()
        };

        commands
            .entity(entity)
            .insert_bundle(bundle)
            .insert(RigidBodyPositionSync::Discrete);
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

        let collider_type = match collider_desc.is_sensor {
            true => ColliderType::Sensor,
            false => ColliderType::Solid,
        };

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
            }
            _ => panic!("Unnknown collider shape"),
        };

        let collider_bundle = ColliderBundle {
            collider_type: ColliderTypeComponent(collider_type),
            shape: ColliderShapeComponent(shape),
            material: ColliderMaterialComponent(ColliderMaterial {
                friction: collider_desc.friction,
                restitution: collider_desc.restitution,
                ..Default::default()
            }),
            position: ColliderPositionComponent(
                (collider_desc.centroid_translation, Quat::IDENTITY).into(),
            ),
            mass_properties: ColliderMassPropsComponent(ColliderMassProps::Density(
                collider_desc.density,
            )),
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(collider_bundle);
    }
}
