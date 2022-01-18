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
    /// Maps to [`RigidBodyType`]. Because we can't export enums yet, this is encoded as a u8
    ///  0 => dynamic
    ///  1 => static
    ///  2 => kinematic position based
    ///  3 => kinematic velocity based
    pub body_type: u8,

    /// Maps to [`RigidBodyPosition`] `translation`
    pub position: Vec3,
    /// Maps to [`RigidBodyPosition`] `scale`
    pub scale: Vec3,
    /// Maps to [`RigidBodyPosition`] `rotation`
    pub rotation: Vec3,

    /// Maps to [`RigidBodyVelocity`] `linvel`
    pub linear_velocity: Vec3,
    /// Maps to [`RigidBodyVelocity`] `linvel`
    pub angular_velocity: Vec3,

    /// Maps to [`RigidBodyMassProps`] flags, [`RigidBodyMassPropsFlags`]
    pub lock_translation: bool,
    /// Maps to [`RigidBodyMassProps`] flags, [`RigidBodyMassPropsFlags`]
    pub lock_rotation_x: bool,
    /// Maps to [`RigidBodyMassProps`] flags, [`RigidBodyMassPropsFlags`]
    pub lock_rotation_y: bool,
    /// Maps to [`RigidBodyMassProps`] flags, [`RigidBodyMassPropsFlags`]
    pub lock_rotation_z: bool,

    /// Maps to [`RigidBodyForces`] `gravity_scale`
    pub gravity_scale: f32,
    // /// Maps to [`RigidBodyForces`] `force`
    // pub inertia_extra: Vec3,
    /// Maps to [`RigidBodyForces`] `torque`
    pub initial_torque: Vec3,

    /// Maps to [`RigidBodyDamping`] `linear_damping`
    pub linear_damping: f32,
    /// Maps to [`RigidBodyDamping`] `angular_damping`
    pub angular_damping: f32,

    /// Maps to [`RigidBodyCcd`] `ccd_enabled` (default is false)
    pub ccd_enabled: bool,
    // pub sleep_allow: bool,

    // /// Mass of the body (additional to the densities of the collision shapes)
    // pub mass_extra: f32,
}

impl RigidBodyDescription {
    fn rigid_body_type(&self) -> RigidBodyTypeComponent {
        RigidBodyTypeComponent(match self.body_type {
            0 => RigidBodyType::Dynamic,
            1 => RigidBodyType::Static,
            2 => RigidBodyType::KinematicPositionBased,
            3 => RigidBodyType::KinematicVelocityBased,
            _ => RigidBodyType::Dynamic,
        })
    }

    fn rigid_body_flags(&self) -> RigidBodyMassPropsFlags {
        let mut flags = RigidBodyMassPropsFlags::empty();
        if self.lock_rotation_x {
            // lock all r
            flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_X);
        }
        if self.lock_rotation_y {
            // lock all r
            flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_Y);
        }
        if self.lock_rotation_z {
            // lock all r
            flags.insert(RigidBodyMassPropsFlags::ROTATION_LOCKED_Z);
        }
        if self.lock_translation {
            // lock all r
            flags.insert(RigidBodyMassPropsFlags::TRANSLATION_LOCKED);
        }
        flags
    }
}

/// Converts a RigidBodyDescription into a rapier::dynamics::RigidBodyBuilder. This allows
/// RigidBodyBuilders to be created from a file using bevies Reflection system and scene format
pub fn body_description_to_builder(
    mut commands: Commands,
    body_desc_query: Query<(&RigidBodyDescription, Entity, &Transform)>,
) {
    for (desc, entity, transform) in body_desc_query.iter() {
        commands.entity(entity).remove::<RigidBodyDescription>();

        let isometry = Isometry3::from((transform.translation, transform.rotation));

        let bundle = RigidBodyBundle {
            body_type: desc.rigid_body_type(),
            position: RigidBodyPositionComponent(RigidBodyPosition {
                position: isometry,
                next_position: isometry,
            }),
            velocity: RigidBodyVelocityComponent(RigidBodyVelocity {
                linvel: desc.linear_velocity.into(),
                angvel: desc.angular_velocity.into(),
            }),
            mass_properties: RigidBodyMassPropsComponent(RigidBodyMassProps {
                flags: desc.rigid_body_flags(),
                ..Default::default()
            }),
            forces: RigidBodyForcesComponent(RigidBodyForces {
                gravity_scale: desc.gravity_scale,
                ..Default::default()
            }),
            activation: Default::default(),
            damping: RigidBodyDampingComponent(RigidBodyDamping {
                linear_damping: desc.linear_damping,
                angular_damping: desc.angular_damping,
            }),
            ccd: RigidBodyCcdComponent(RigidBodyCcd {
                ccd_enabled: desc.ccd_enabled,
                ..Default::default()
            }),
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(bundle);
    }
}

/// Maps to a [`ColliderBundle`]
#[derive(Reflect, Default, Debug, Component)]
#[reflect(Component)]
pub struct ColliderDescription {
    /// Maps to [`ColliderMaterial`] friction
    friction: f32,
    /// Maps to [`ColliderMaterial`] restitution
    restitution: f32,
    /// Maps to [`ColliderType`] as `Solid` if false, and `Sensor` if true
    is_sensor: bool,
    /// Maps to [`ColliderMassProps::Density`]
    density: f32,

    /// At the moment, you can't use an enum with bevy's Reflect derivation.
    /// So instead we're doing this the old fashioned way.
    ///
    /// collider_shape = 0: Sphere collider
    ///     collider_shape_data: f32 = radius
    collider_shape: u8,
    collider_shape_data: smallvec::SmallVec<[u8; 8]>,
}

impl ColliderDescription {
    fn collider_type(&self) -> ColliderTypeComponent {
        ColliderTypeComponent(match self.is_sensor {
            true => ColliderType::Sensor,
            false => ColliderType::Solid,
        })
    }

    fn collider_shape(&self) -> ColliderShapeComponent {
        ColliderShapeComponent(match self.collider_shape {
            0 => {
                // Sphere
                let radius = get_f32(&self.collider_shape_data[0..]);
                SharedShape::ball(radius)
            }
            1 => {
                // Capsule
                let half_height = get_f32(&self.collider_shape_data[0..]);
                let radius = get_f32(&self.collider_shape_data[4..]);
                SharedShape::capsule(
                    Point3::from_slice(&[0.0, 0.0, half_height]),
                    Point3::from_slice(&[0.0, 0.0, -half_height]),
                    radius,
                )
            }
            2 => {
                // Box
                SharedShape::cuboid(
                    get_f32(&self.collider_shape_data[0..]),
                    get_f32(&self.collider_shape_data[4..]),
                    get_f32(&self.collider_shape_data[8..]),
                )
            }
            _ => panic!("Unnknown collider shape"),
        })
    }
}

pub fn collider_description_to_builder(
    mut commands: Commands,
    collider_desc_query: Query<(Entity, &ColliderDescription, &Transform)>,
) {
    for (entity, desc, transform) in collider_desc_query.iter() {
        commands.entity(entity).remove::<ColliderDescription>();

        let bundle = ColliderBundle {
            collider_type: desc.collider_type(),
            shape: desc.collider_shape(),
            material: ColliderMaterialComponent(ColliderMaterial {
                friction: desc.friction,
                restitution: desc.restitution,
                ..Default::default()
            }),
            mass_properties: ColliderMassPropsComponent(
                ColliderMassProps::Density(desc.density)
            ),
            ..Default::default()
        };

        commands.entity(entity).insert_bundle(bundle);
    }
}

/// Reads a f32 from a buffer
fn get_f32(arr: &[u8]) -> f32 {
    f32::from_le_bytes(arr[0..4].try_into().unwrap())
}