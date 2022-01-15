use bevy::prelude::*;
use bevy_rapier3d::physics::{ColliderBundle, RigidBodyBundle};
use bevy_rapier3d::prelude::{
    ColliderMassProps, ColliderMassPropsComponent, ColliderMaterial, ColliderMaterialComponent,
    ColliderShape, ColliderShapeComponent, ColliderType, ColliderTypeComponent, RigidBodyCcd,
    RigidBodyCcdComponent, RigidBodyDamping, RigidBodyDampingComponent, RigidBodyPosition,
    RigidBodyPositionComponent, RigidBodyTypeComponent,
};
use bevy_rapier3d::rapier::dynamics::RigidBodyType;
use bevy_rapier3d::rapier::na;
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
    ///  2 => kinematic
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

    /// Mass of the body (additional to the densities of the collision shapes)
    pub mass_extra: f32,

    /// Inertia of the body (additional to the intertia contributed by the collision shapes)
    pub inertia_extra: Vec3,
}

/// Converts a RigidBodyDescription into a rapier::dynamics::RigidBodyBuilder. This allows
/// RigidBodyBuilders to be created from a file using bevy's Reflection system and scene format
pub fn body_description_to_builder(
    mut commands: Commands,
    body_desc_query: Query<(&RigidBodyDescription, Entity, &Transform)>,
) {
    for (body_desc, entity, transform) in body_desc_query.iter() {
        commands.entity(entity).remove::<RigidBodyDescription>();

        // There's probably a better way to convert from a glam vector to a nalgebra matrix,
        // but I couldn't find it.
        // let inertia_vec = AngVector::from_iterator(
        //     vec![
        //         body_desc.inertia_extra.x,
        //         body_desc.inertia_extra.y,
        //         body_desc.inertia_extra.z,
        //     ]
        //     .into_iter(),
        // );

        let position = na::Isometry3::from_parts(
            na::Translation3::new(
                transform.translation.x,
                transform.translation.y,
                transform.translation.z,
            ),
            na::UnitQuaternion::from_quaternion(na::Quaternion::new(
                transform.rotation.w,
                transform.rotation.x,
                transform.rotation.y,
                transform.rotation.z,
            )),
        );

        let body_status = match body_desc.body_status {
            0 => RigidBodyType::Dynamic,
            1 => RigidBodyType::Static,
            2 => RigidBodyType::KinematicPositionBased,
            3 => RigidBodyType::KinematicVelocityBased,
            _ => panic!("Unknown body status"),
        };

        let position = RigidBodyPosition::from(position);

        let rigid_body_bundle = RigidBodyBundle {
            body_type: RigidBodyTypeComponent(body_status),
            position: RigidBodyPositionComponent(position),
            damping: RigidBodyDampingComponent(RigidBodyDamping {
                linear_damping: body_desc.damping_linear,
                angular_damping: body_desc.damping_angular,
            }),
            ccd: RigidBodyCcdComponent(RigidBodyCcd {
                ccd_enabled: false,
                ..Default::default()
            }),
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(rigid_body_bundle);

        // TODO: remove this when collider loading is implemented
        // let collider1 = ColliderBuilder::ball(1.0).density(1.0);
        // commands.entity(entity).insert(collider1);
    }
}

#[derive(Reflect, Default, Debug, Component)]
#[reflect(Component)]
pub struct ColliderDescription {
    friction: f32,
    restitution: f32,
    is_sensor: bool,
    density: f32,

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
                ColliderShape::ball(radius)
            }
            1 => {
                // Capsule
                let half_height = get_f32(&collider_desc.collider_shape_data[0..]);
                let radius = get_f32(&collider_desc.collider_shape_data[4..]);
                ColliderShape::capsule(
                    na::Point3::new(0.0, 0.0, half_height),
                    na::Point3::new(0.0, 0.0, -half_height),
                    radius,
                )
            }
            2 => {
                // Box
                ColliderShape::cuboid(
                    get_f32(&collider_desc.collider_shape_data[0..]),
                    get_f32(&collider_desc.collider_shape_data[4..]),
                    get_f32(&collider_desc.collider_shape_data[8..]),
                )
            }
            _ => panic!("Unnknown collider shape"),
        };

        let collider_bundle = ColliderBundle {
            collider_type: ColliderTypeComponent(if collider_desc.is_sensor {
                ColliderType::Sensor
            } else {
                ColliderType::Solid
            }),
            shape: ColliderShapeComponent(shape),
            material: ColliderMaterialComponent(ColliderMaterial {
                friction: collider_desc.friction,
                restitution: collider_desc.restitution,
                ..Default::default()
            }),
            flags: Default::default(),
            mass_properties: ColliderMassPropsComponent(ColliderMassProps::Density(
                collider_desc.density,
            )),
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(collider_bundle);
    }
}
