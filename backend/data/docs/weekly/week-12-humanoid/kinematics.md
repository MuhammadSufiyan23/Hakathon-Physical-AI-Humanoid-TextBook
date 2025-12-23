---
sidebar_label: 'Humanoid Kinematics and Motion Planning'
title: 'Humanoid Kinematics and Motion Planning'
---

# Humanoid Kinematics and Motion Planning

## Introduction to Humanoid Kinematics

Humanoid kinematics is the study of motion in human-like robots without considering the forces that cause the motion. Unlike simple robotic systems, humanoid robots have complex kinematic structures with multiple degrees of freedom (DOF) distributed across arms, legs, torso, and head, requiring sophisticated mathematical approaches to describe and control their motion.

## Humanoid Kinematic Structure

### Anthropomorphic Design Considerations

Humanoid robots are designed to mimic human anatomy and kinematics. A typical humanoid has:

- **Torso**: 3-6 DOF (pitch, roll, yaw for upper and lower torso)
- **Head**: 2-3 DOF (neck pitch, yaw, and sometimes roll)
- **Arms**: 6-8 DOF each (shoulder: 3 DOF, elbow: 1-2 DOF, wrist: 2-3 DOF)
- **Legs**: 6 DOF each (hip: 3 DOF, knee: 1 DOF, ankle: 2 DOF)

### Denavit-Hartenberg Parameters for Humanoid Robots

The Denavit-Hartenberg (DH) convention is used to define coordinate frames for each joint in a humanoid robot:

```python
import numpy as np
import math

class HumanoidDHParameters:
    def __init__(self):
        # Define DH parameters for a simplified humanoid arm
        self.arm_dh_params = {
            'shoulder_yaw': {'a': 0, 'alpha': -math.pi/2, 'd': 0.2, 'theta_offset': 0},
            'shoulder_pitch': {'a': 0.15, 'alpha': 0, 'd': 0, 'theta_offset': math.pi/2},
            'shoulder_roll': {'a': 0, 'alpha': math.pi/2, 'd': 0, 'theta_offset': 0},
            'elbow_pitch': {'a': 0.25, 'alpha': 0, 'd': 0, 'theta_offset': 0},
            'wrist_yaw': {'a': 0.2, 'alpha': 0, 'd': 0, 'theta_offset': 0},
            'wrist_pitch': {'a': 0, 'alpha': -math.pi/2, 'd': 0, 'theta_offset': 0}
        }

        # Define DH parameters for a simplified humanoid leg
        self.leg_dh_params = {
            'hip_yaw': {'a': 0, 'alpha': -math.pi/2, 'd': 0.05, 'theta_offset': 0},
            'hip_roll': {'a': 0, 'alpha': math.pi/2, 'd': 0, 'theta_offset': 0},
            'hip_pitch': {'a': 0, 'alpha': -math.pi/2, 'd': -0.4, 'theta_offset': -math.pi/2},
            'knee_pitch': {'a': -0.4, 'alpha': 0, 'd': 0, 'theta_offset': 0},
            'ankle_pitch': {'a': -0.4, 'alpha': 0, 'd': 0, 'theta_offset': 0},
            'ankle_roll': {'a': 0, 'alpha': -math.pi/2, 'd': 0, 'theta_offset': 0}
        }

    def dh_transform(self, a, alpha, d, theta):
        """Calculate Denavit-Hartenberg transformation matrix."""
        return np.array([
            [math.cos(theta), -math.sin(theta)*math.cos(alpha), math.sin(theta)*math.sin(alpha), a*math.cos(theta)],
            [math.sin(theta), math.cos(theta)*math.cos(alpha), -math.cos(theta)*math.sin(alpha), a*math.sin(theta)],
            [0, math.sin(alpha), math.cos(alpha), d],
            [0, 0, 0, 1]
        ])

    def forward_kinematics_arm(self, joint_angles):
        """
        Calculate forward kinematics for humanoid arm.

        Args:
            joint_angles: List of joint angles [shoulder_yaw, shoulder_pitch, shoulder_roll,
                         elbow_pitch, wrist_yaw, wrist_pitch]
        """
        if len(joint_angles) != 6:
            raise ValueError("Expected 6 joint angles for arm")

        # Calculate transformation matrices for each joint
        T = np.eye(4)  # Identity matrix

        for i, (joint_name, params) in enumerate(self.arm_dh_params.items()):
            theta = joint_angles[i] + params['theta_offset']
            A = self.dh_transform(params['a'], params['alpha'], params['d'], theta)
            T = T @ A

        return T  # Returns transformation matrix to end effector

    def forward_kinematics_leg(self, joint_angles):
        """
        Calculate forward kinematics for humanoid leg.

        Args:
            joint_angles: List of joint angles [hip_yaw, hip_roll, hip_pitch,
                         knee_pitch, ankle_pitch, ankle_roll]
        """
        if len(joint_angles) != 6:
            raise ValueError("Expected 6 joint angles for leg")

        T = np.eye(4)

        for i, (joint_name, params) in enumerate(self.leg_dh_params.items()):
            theta = joint_angles[i] + params['theta_offset']
            A = self.dh_transform(params['a'], params['alpha'], params['d'], theta)
            T = T @ A

        return T
```

## Forward Kinematics for Humanoid Systems

### Multi-Chain Forward Kinematics

Humanoid robots have multiple kinematic chains that need to be considered simultaneously:

```python
class MultiChainForwardKinematics:
    def __init__(self, robot_model):
        self.robot_model = robot_model
        self.chains = {
            'left_arm': ['left_shoulder', 'left_elbow', 'left_wrist'],
            'right_arm': ['right_shoulder', 'right_elbow', 'right_wrist'],
            'left_leg': ['left_hip', 'left_knee', 'left_ankle'],
            'right_leg': ['right_hip', 'right_knee', 'right_ankle']
        }

    def calculate_all_end_effectors(self, joint_angles):
        """
        Calculate positions and orientations of all end effectors.

        Args:
            joint_angles: Dictionary mapping joint names to angles
        """
        end_effectors = {}

        for chain_name, chain_joints in self.chains.items():
            # Extract relevant joint angles for this chain
            chain_angles = []
            for joint_name in chain_joints:
                if joint_name in joint_angles:
                    chain_angles.append(joint_angles[joint_name])

            if len(chain_angles) == len(chain_joints):
                # Calculate forward kinematics for this chain
                T = self.calculate_chain_fk(chain_name, chain_angles)

                # Extract position and orientation
                position = T[:3, 3]
                orientation_matrix = T[:3, :3]

                # Convert to quaternion
                quaternion = self.rotation_matrix_to_quaternion(orientation_matrix)

                end_effectors[chain_name] = {
                    'position': position,
                    'orientation': quaternion,
                    'transform': T
                }

        return end_effectors

    def calculate_chain_fk(self, chain_name, joint_angles):
        """Calculate forward kinematics for a specific chain."""
        # This would use the specific DH parameters for each chain
        # For this example, we'll use a simplified approach

        T = np.eye(4)

        if chain_name.startswith('arm'):
            # Use arm DH parameters
            dh_params = self.get_arm_dh_params()
        else:
            # Use leg DH parameters
            dh_params = self.get_leg_dh_params()

        for i, (joint_name, params) in enumerate(dh_params.items()):
            if i < len(joint_angles):
                theta = joint_angles[i] + params['theta_offset']
                A = self.dh_transform(params['a'], params['alpha'], params['d'], theta)
                T = T @ A

        return T

    def rotation_matrix_to_quaternion(self, R):
        """Convert rotation matrix to quaternion."""
        # Method from http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/
        trace = np.trace(R)

        if trace > 0:
            s = math.sqrt(trace + 1.0) * 2  # s=4*qw
            qw = 0.25 * s
            qx = (R[2,1] - R[1,2]) / s
            qy = (R[0,2] - R[2,0]) / s
            qz = (R[1,0] - R[0,1]) / s
        elif (R[0,0] > R[1,1]) and (R[0,0] > R[2,2]):
            s = math.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2  # s=4*qx
            qw = (R[2,1] - R[1,2]) / s
            qx = 0.25 * s
            qy = (R[0,1] + R[1,0]) / s
            qz = (R[0,2] + R[2,0]) / s
        elif R[1,1] > R[2,2]:
            s = math.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2  # s=4*qy
            qw = (R[0,2] - R[2,0]) / s
            qx = (R[0,1] + R[1,0]) / s
            qy = 0.25 * s
            qz = (R[1,2] + R[2,1]) / s
        else:
            s = math.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2  # s=4*qz
            qw = (R[1,0] - R[0,1]) / s
            qx = (R[0,2] + R[2,0]) / s
            qy = (R[1,2] + R[2,1]) / s
            qz = 0.25 * s

        return np.array([qw, qx, qy, qz])
```

## Inverse Kinematics for Humanoid Robots

### Analytical Inverse Kinematics

For some humanoid limbs, analytical solutions exist:

```python
class AnalyticalInverseKinematics:
    def __init__(self):
        # Anthropometric data (typical human proportions)
        self.upper_arm_length = 0.28  # meters
        self.forearm_length = 0.25   # meters
        self.thigh_length = 0.45     # meters
        self.shin_length = 0.42      # meters

    def inverse_kinematics_arm_3dof(self, target_position, current_shoulder_pos):
        """
        Analytical inverse kinematics for 3DOF arm (shoulder pitch, elbow, wrist).

        Args:
            target_position: [x, y, z] desired end-effector position
            current_shoulder_pos: [x, y, z] current shoulder position
        """
        # Calculate relative position from shoulder
        rel_x = target_position[0] - current_shoulder_pos[0]
        rel_y = target_position[1] - current_shoulder_pos[1]
        rel_z = target_position[2] - current_shoulder_pos[2]

        # Calculate distance from shoulder to target
        r = math.sqrt(rel_x**2 + rel_y**2)
        d = math.sqrt(r**2 + rel_z**2)

        # Check if target is reachable
        total_arm_length = self.upper_arm_length + self.forearm_length
        if d > total_arm_length:
            raise ValueError("Target position is out of reach")

        if d < abs(self.upper_arm_length - self.forearm_length):
            raise ValueError("Target position is too close (within arm range)")

        # Calculate shoulder yaw (if needed for full 6DOF arm)
        shoulder_yaw = math.atan2(rel_y, rel_x)

        # Calculate shoulder pitch using law of cosines
        # Triangle formed by: shoulder, elbow, target
        # Sides: upper_arm_length, forearm_length, d
        cos_shoulder_angle = (self.upper_arm_length**2 + d**2 - self.forearm_length**2) / (2 * self.upper_arm_length * d)
        cos_shoulder_angle = max(-1, min(1, cos_shoulder_angle))  # Clamp to valid range
        shoulder_angle = math.acos(cos_shoulder_angle)

        # Calculate angle from horizontal
        angle_from_horizontal = math.atan2(rel_z, r)

        # Shoulder pitch is sum of angles
        shoulder_pitch = angle_from_horizontal + shoulder_angle

        # Calculate elbow angle using law of cosines
        cos_elbow_angle = (self.upper_arm_length**2 + self.forearm_length**2 - d**2) / (2 * self.upper_arm_length * self.forearm_length)
        cos_elbow_angle = max(-1, min(1, cos_elbow_angle))
        elbow_angle = math.pi - math.acos(cos_elbow_angle)

        # Calculate wrist angle to achieve desired orientation
        # This is simplified - full solution would consider orientation
        wrist_angle = 0  # Placeholder

        return {
            'shoulder_yaw': shoulder_yaw,
            'shoulder_pitch': shoulder_pitch,
            'elbow_angle': elbow_angle,
            'wrist_angle': wrist_angle
        }

    def inverse_kinematics_leg_3dof(self, target_foot_pos, current_hip_pos):
        """
        Analytical inverse kinematics for 3DOF leg (hip pitch, knee, ankle pitch).

        Args:
            target_foot_pos: [x, y, z] desired foot position
            current_hip_pos: [x, y, z] current hip position
        """
        # Calculate relative position
        rel_x = target_foot_pos[0] - current_hip_pos[0]
        rel_y = target_foot_pos[1] - current_hip_pos[1]
        rel_z = target_foot_pos[2] - current_hip_pos[2]

        # Calculate horizontal distance
        r = math.sqrt(rel_x**2 + rel_y**2)

        # Calculate distance from hip to foot
        d = math.sqrt(r**2 + rel_z**2)

        # Check reachability
        total_leg_length = self.thigh_length + self.shin_length
        if d > total_leg_length:
            raise ValueError("Target position is out of reach")

        if d < abs(self.thigh_length - self.shin_length):
            raise ValueError("Target position is too close")

        # Calculate hip yaw
        hip_yaw = math.atan2(rel_y, rel_x)

        # Calculate hip pitch
        cos_hip_angle = (self.thigh_length**2 + d**2 - self.shin_length**2) / (2 * self.thigh_length * d)
        cos_hip_angle = max(-1, min(1, cos_hip_angle))
        hip_angle = math.acos(cos_hip_angle)

        # Calculate angle from horizontal
        angle_from_horizontal = math.atan2(rel_z, r)

        # Hip pitch is sum of angles
        hip_pitch = angle_from_horizontal + hip_angle

        # Calculate knee angle
        cos_knee_angle = (self.thigh_length**2 + self.shin_length**2 - d**2) / (2 * self.thigh_length * self.shin_length)
        cos_knee_angle = max(-1, min(1, cos_knee_angle))
        knee_angle = math.pi - math.acos(cos_knee_angle)

        # Calculate ankle angle to achieve desired foot orientation
        ankle_angle = 0  # Placeholder

        return {
            'hip_yaw': hip_yaw,
            'hip_pitch': hip_pitch,
            'knee_angle': knee_angle,
            'ankle_angle': ankle_angle
        }
```

### Numerical Inverse Kinematics

For more complex humanoid systems, numerical methods are often necessary:

```python
import scipy.optimize
from scipy.spatial.transform import Rotation as R

class NumericalInverseKinematics:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.max_iterations = 1000
        self.tolerance = 1e-4

    def inverse_kinematics_numerical(self, target_pos, target_rot, initial_joints,
                                   chain_joints, weights=None):
        """
        Solve inverse kinematics using numerical optimization.

        Args:
            target_pos: [x, y, z] desired end-effector position
            target_rot: [w, x, y, z] desired end-effector orientation (quaternion)
            initial_joints: Initial joint configuration
            chain_joints: List of joint names in the kinematic chain
            weights: Optional weights for position/orientation importance
        """
        if weights is None:
            weights = [1.0, 1.0]  # Position and orientation weights

        def objective_function(joint_angles):
            """Objective function to minimize."""
            # Calculate current end-effector pose with given joint angles
            current_pos, current_rot = self.forward_kinematics(joint_angles, chain_joints)

            # Calculate position error
            pos_error = np.linalg.norm(np.array(target_pos) - np.array(current_pos))

            # Calculate orientation error (using quaternion distance)
            q1 = np.array(target_rot)
            q2 = np.array(current_rot)
            # Ensure quaternions have same handedness
            if np.dot(q1, q2) < 0:
                q2 = -q2
            orientation_error = 2 * np.arccos(np.abs(np.dot(q1, q2)))

            # Weighted error
            total_error = weights[0] * pos_error + weights[1] * orientation_error

            return total_error

        def joint_limits_constraint(joint_angles):
            """Constraint function for joint limits."""
            constraints = []
            for i, joint_name in enumerate(chain_joints):
                if i < len(joint_angles):
                    joint_limits = self.robot.get_joint_limits(joint_name)
                    lower, upper = joint_limits

                    # Return positive values for satisfied constraints
                    constraints.append(joint_angles[i] - lower)  # joint >= lower
                    constraints.append(upper - joint_angles[i])  # joint <= upper

            return np.array(constraints)

        # Set up constraints
        constraints = {
            'type': 'ineq',
            'fun': joint_limits_constraint
        }

        # Solve optimization problem
        result = scipy.optimize.minimize(
            objective_function,
            initial_joints,
            method='SLSQP',
            constraints=constraints,
            options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
        )

        if result.success:
            return result.x
        else:
            raise RuntimeError(f"IK solution failed: {result.message}")

    def jacobian_transpose_method(self, target_pos, target_rot, current_joints, chain_joints):
        """
        Solve inverse kinematics using Jacobian transpose method.
        """
        current_pos, current_rot = self.forward_kinematics(current_joints, chain_joints)

        # Calculate position and orientation errors
        pos_error = np.array(target_pos) - np.array(current_pos)

        # Calculate orientation error using logarithmic map
        q_error = self.quaternion_error(np.array(target_rot), np.array(current_rot))
        rot_error = self.quaternion_to_rotation_vector(q_error)

        # Combine position and orientation errors
        error = np.concatenate([pos_error, rot_error])

        # Calculate Jacobian
        jacobian = self.calculate_jacobian(current_joints, chain_joints)

        # Calculate joint velocity using Jacobian transpose
        joint_velocity = 0.1 * jacobian.T @ error  # Learning rate of 0.1

        # Update joint angles
        new_joints = current_joints + joint_velocity

        return new_joints

    def calculate_jacobian(self, joint_angles, chain_joints):
        """
        Calculate geometric Jacobian for the kinematic chain.

        Returns:
            Jacobian matrix of size (6, n_joints) where 6 represents
            3 linear and 3 angular velocities
        """
        n_joints = len(chain_joints)
        jacobian = np.zeros((6, n_joints))

        # Get transformation matrices for each joint
        transforms = self.get_transform_chain(joint_angles, chain_joints)

        # Get end-effector position
        end_effector_pos = transforms[-1][:3, 3]

        # Calculate each column of the Jacobian
        for i in range(n_joints):
            # Z-axis of joint i in base frame
            z_i = transforms[i][:3, 2]  # Third column is the z-axis
            # Position vector from joint i to end-effector
            r_ie = end_effector_pos - transforms[i][:3, 3]

            # Linear velocity contribution
            jacobian[:3, i] = np.cross(z_i, r_ie)
            # Angular velocity contribution
            jacobian[3:, i] = z_i

        return jacobian

    def quaternion_error(self, q1, q2):
        """
        Calculate the error quaternion between two orientations.
        """
        # q_error = q1 * q2^-1 (where q2^-1 is conjugate of q2)
        q2_conj = np.array([q2[0], -q2[1], -q2[2], -q2[3]])  # Conjugate
        q_error = self.quaternion_multiply(q1, q2_conj)
        return q_error

    def quaternion_multiply(self, q1, q2):
        """
        Multiply two quaternions.
        """
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2

        return np.array([w, x, y, z])

    def quaternion_to_rotation_vector(self, quaternion):
        """
        Convert quaternion to rotation vector (axis-angle representation).
        """
        # Normalize quaternion
        q = quaternion / np.linalg.norm(quaternion)

        # Extract angle
        angle = 2 * math.acos(q[0])

        # Extract axis
        s = math.sqrt(1 - q[0]**2)
        if s < 1e-6:  # Singularity at angle = 0
            return np.array([0, 0, 0])

        axis = np.array([q[1], q[2], q[3]]) / s
        rotation_vector = axis * angle

        return rotation_vector

    def forward_kinematics(self, joint_angles, chain_joints):
        """
        Calculate forward kinematics for a given chain.
        This would typically use the robot's URDF/SDF model.
        """
        # In a real implementation, this would use the robot's kinematic model
        # For this example, we'll return a placeholder
        return [0, 0, 0], [1, 0, 0, 0]  # [x,y,z], [w,x,y,z]
```

## Whole-Body Kinematics

### Humanoid Whole-Body Control

Humanoid robots require coordination of all kinematic chains simultaneously:

```python
class WholeBodyKinematics:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.chains = {
            'left_arm': ['l_shoulder_pitch', 'l_shoulder_roll', 'l_shoulder_yaw',
                        'l_elbow_pitch', 'l_wrist_yaw', 'l_wrist_pitch'],
            'right_arm': ['r_shoulder_pitch', 'r_shoulder_roll', 'r_shoulder_yaw',
                         'r_elbow_pitch', 'r_wrist_yaw', 'r_wrist_pitch'],
            'left_leg': ['l_hip_yaw', 'l_hip_roll', 'l_hip_pitch',
                        'l_knee_pitch', 'l_ankle_pitch', 'l_ankle_roll'],
            'right_leg': ['r_hip_yaw', 'r_hip_roll', 'r_hip_pitch',
                         'r_knee_pitch', 'r_ankle_pitch', 'r_ankle_roll']
        }

    def calculate_com_position(self, joint_angles):
        """
        Calculate center of mass position given joint angles.
        This uses anthropometric data and link masses.
        """
        total_mass = 0
        weighted_com_sum = np.zeros(3)

        for link_name, link_info in self.robot.links.items():
            if 'mass' in link_info and 'com_offset' in link_info:
                mass = link_info['mass']
                # Calculate link COM position in global frame
                link_com_global = self.calculate_link_com_position(
                    link_name, joint_angles, link_info['com_offset']
                )

                total_mass += mass
                weighted_com_sum += mass * link_com_global

        if total_mass > 0:
            com_position = weighted_com_sum / total_mass
        else:
            com_position = np.zeros(3)

        return com_position

    def calculate_link_com_position(self, link_name, joint_angles, local_com_offset):
        """
        Calculate the global position of a link's center of mass.
        """
        # Get the transformation from base to this link
        T_base_to_link = self.get_link_transform(link_name, joint_angles)

        # Transform local COM offset to global position
        local_com_homogeneous = np.array([*local_com_offset, 1.0])
        global_com = T_base_to_link @ local_com_homogeneous

        return global_com[:3]

    def get_link_transform(self, link_name, joint_angles):
        """
        Get transformation matrix from base to specified link.
        """
        # This would traverse the kinematic tree to calculate the transform
        # For this example, we'll return a placeholder
        return np.eye(4)

    def calculate_support_polygon(self, left_foot_pos, right_foot_pos):
        """
        Calculate support polygon for bipedal balance.
        """
        # Create polygon vertices based on foot positions and sizes
        foot_size_x = 0.15  # 15cm
        foot_size_y = 0.07  # 7cm

        # Left foot vertices
        left_foot_vertices = np.array([
            [left_foot_pos[0] - foot_size_x/2, left_foot_pos[1] - foot_size_y/2, left_foot_pos[2]],
            [left_foot_pos[0] + foot_size_x/2, left_foot_pos[1] - foot_size_y/2, left_foot_pos[2]],
            [left_foot_pos[0] + foot_size_x/2, left_foot_pos[1] + foot_size_y/2, left_foot_pos[2]],
            [left_foot_pos[0] - foot_size_x/2, left_foot_pos[1] + foot_size_y/2, left_foot_pos[2]]
        ])

        # Right foot vertices
        right_foot_vertices = np.array([
            [right_foot_pos[0] - foot_size_x/2, right_foot_pos[1] - foot_size_y/2, right_foot_pos[2]],
            [right_foot_pos[0] + foot_size_x/2, right_foot_pos[1] - foot_size_y/2, right_foot_pos[2]],
            [right_foot_pos[0] + foot_size_x/2, right_foot_pos[1] + foot_size_y/2, right_foot_pos[2]],
            [right_foot_pos[0] - foot_size_x/2, right_foot_pos[1] + foot_size_y/2, right_foot_pos[2]]
        ])

        # Combine vertices to form support polygon
        if self.is_double_support(left_foot_pos, right_foot_pos):
            # Double support - combine both feet
            support_vertices = np.vstack([left_foot_vertices, right_foot_vertices])
        else:
            # Single support - use only stance foot
            stance_foot = self.get_stance_foot(left_foot_pos, right_foot_pos)
            if stance_foot == 'left':
                support_vertices = left_foot_vertices
            else:
                support_vertices = right_foot_vertices

        return support_vertices

    def is_double_support(self, left_pos, right_pos):
        """
        Determine if robot is in double support phase.
        """
        # Simplified check - in reality this would use contact sensors
        # and dynamic criteria
        return abs(left_pos[1] - right_pos[1]) < 0.3  # Less than 30cm apart

    def get_stance_foot(self, left_pos, right_pos):
        """
        Determine which foot is in stance phase.
        """
        # Simplified - in reality this would use contact sensors
        # and dynamic criteria
        return 'left'  # Default assumption

    def is_zmp_stable(self, zmp_pos, support_polygon):
        """
        Check if ZMP is within support polygon.
        """
        # Use ray casting algorithm to check point in polygon
        x, y = zmp_pos[0], zmp_pos[1]
        n = len(support_polygon)
        inside = False

        p1x, p1y = support_polygon[0][0], support_polygon[0][1]
        for i in range(1, n + 1):
            p2x, p2y = support_polygon[i % n][0], support_polygon[i % n][1]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
```

## Motion Planning for Humanoid Robots

### Trajectory Generation

```python
from scipy.interpolate import CubicSpline
import bezier

class HumanoidTrajectoryGenerator:
    def __init__(self):
        self.dt = 0.01  # 100Hz control frequency

    def generate_arm_trajectory(self, start_pos, end_pos, duration=2.0):
        """
        Generate smooth trajectory for arm movement.

        Args:
            start_pos: Starting position [x, y, z]
            end_pos: Ending position [x, y, z]
            duration: Movement duration in seconds
        """
        n_points = int(duration / self.dt) + 1
        t = np.linspace(0, duration, n_points)

        # Generate smooth trajectory using quintic polynomial
        # This ensures continuity in position, velocity, and acceleration
        trajectory = []
        for i in range(3):  # x, y, z
            pos_traj = self.generate_quintic_trajectory(
                start_pos[i], 0, 0,  # start pos, vel, acc
                end_pos[i], 0, 0,    # end pos, vel, acc
                duration
            )

            for j, time_step in enumerate(t):
                if j < len(pos_traj):
                    trajectory.append({
                        'time': time_step,
                        'position': [pos_traj[j] if k == i else start_pos[k] + (end_pos[k] - start_pos[k]) * (time_step / duration) for k in range(3)],
                        'velocity': self.calculate_velocity(trajectory, j),
                        'acceleration': self.calculate_acceleration(trajectory, j)
                    })

        return trajectory

    def generate_quintic_trajectory(self, start_pos, start_vel, start_acc,
                                  end_pos, end_vel, end_acc, duration):
        """
        Generate quintic polynomial trajectory.

        Args:
            start_pos, start_vel, start_acc: Initial conditions
            end_pos, end_vel, end_acc: Final conditions
            duration: Total time
        """
        t = np.linspace(0, duration, int(duration / self.dt) + 1)

        # Quintic polynomial coefficients
        # q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
        a0 = start_pos
        a1 = start_vel
        a2 = start_acc / 2

        # Solving for coefficients that satisfy boundary conditions
        T = duration
        a3 = (20*end_pos - 20*start_pos - (8*end_vel + 12*start_vel)*T - (3*start_acc - end_acc)*T**2) / (2*T**3)
        a4 = (30*start_pos - 30*end_pos + (14*end_vel + 16*start_vel)*T + (3*start_acc - 2*end_acc)*T**2) / (2*T**4)
        a5 = (12*end_pos - 12*start_pos - (6*end_vel + 6*start_vel)*T - (start_acc - end_acc)*T**2) / (2*T**5)

        positions = a0 + a1*t + a2*t**2 + a3*t**3 + a4*t**4 + a5*t**5
        return positions

    def generate_com_trajectory(self, start_pos, goal_pos, height=0.8, duration=3.0):
        """
        Generate CoM trajectory using inverted pendulum model.
        """
        n_points = int(duration / self.dt) + 1
        t = np.linspace(0, duration, n_points)

        # Use linear interpolation for horizontal movement
        x_traj = np.linspace(start_pos[0], goal_pos[0], n_points)
        y_traj = np.linspace(start_pos[1], goal_pos[1], n_points)

        # Keep height constant for simple CoM movement
        z_traj = np.full(n_points, height)

        # Add small oscillations for natural movement
        oscillation_freq = 2.0  # Hz
        oscillation_amp = 0.01  # meters
        z_traj += oscillation_amp * np.sin(2 * np.pi * oscillation_freq * t)

        # Calculate velocities and accelerations
        vx_traj = np.gradient(x_traj, self.dt)
        vy_traj = np.gradient(y_traj, self.dt)
        vz_traj = np.gradient(z_traj, self.dt)

        ax_traj = np.gradient(vx_traj, self.dt)
        ay_traj = np.gradient(vy_traj, self.dt)
        az_traj = np.gradient(vz_traj, self.dt)

        trajectory = []
        for i in range(n_points):
            trajectory.append({
                'time': t[i],
                'position': np.array([x_traj[i], y_traj[i], z_traj[i]]),
                'velocity': np.array([vx_traj[i], vy_traj[i], vz_traj[i]]),
                'acceleration': np.array([ax_traj[i], ay_traj[i], az_traj[i]])
            })

        return trajectory

    def generate_walking_trajectory(self, step_positions, step_times, step_height=0.05):
        """
        Generate walking trajectory for bipedal locomotion.

        Args:
            step_positions: List of foot positions for each step
            step_times: List of times for each step
            step_height: Maximum height of swinging foot
        """
        if len(step_positions) < 2:
            return []

        trajectory = []
        gravity = 9.81

        for i in range(len(step_positions) - 1):
            # Generate trajectory from current step to next step
            start_pos = step_positions[i]
            end_pos = step_positions[i + 1]
            step_duration = step_times[i + 1] - step_times[i]

            # Calculate intermediate trajectory points
            n_points = int(step_duration / self.dt) + 1
            t = np.linspace(0, step_duration, n_points)

            # Generate foot trajectory (elliptical arc for swing phase)
            for j, time_step in enumerate(t):
                progress = j / (n_points - 1) if n_points > 1 else 0

                # Calculate foot position
                if progress < 0.5:  # Swing phase - lifting foot
                    # Interpolate horizontally
                    x = start_pos[0] + progress * 2 * (end_pos[0] - start_pos[0])
                    y = start_pos[1] + progress * 2 * (end_pos[1] - start_pos[1])

                    # Vertical trajectory (parabolic arc)
                    vertical_progress = progress * 2  # 0 to 1 for rising, 1 to 2 for falling
                    if vertical_progress <= 1:
                        z = start_pos[2] + step_height * (4 * vertical_progress - 4 * vertical_progress**2)
                    else:
                        z = start_pos[2] + step_height * (4 * (2 - vertical_progress) - 4 * (2 - vertical_progress)**2)
                else:  # Support phase - foot on ground
                    x = end_pos[0]
                    y = end_pos[1]
                    z = end_pos[2]

                trajectory.append({
                    'time': step_times[i] + time_step,
                    'position': np.array([x, y, z]),
                    'support_foot': 'left' if i % 2 == 0 else 'right'
                })

        return trajectory

    def calculate_velocity(self, trajectory, index):
        """Calculate velocity from position trajectory."""
        if index == 0 or len(trajectory) < 2:
            return np.zeros(3)

        dt = trajectory[index]['time'] - trajectory[index-1]['time']
        if dt <= 0:
            return np.zeros(3)

        dx = trajectory[index]['position'] - trajectory[index-1]['position']
        return dx / dt

    def calculate_acceleration(self, trajectory, index):
        """Calculate acceleration from velocity trajectory."""
        if index < 2 or len(trajectory) < 3:
            return np.zeros(3)

        dt = trajectory[index]['time'] - trajectory[index-1]['time']
        if dt <= 0:
            return np.zeros(3)

        dv = trajectory[index]['velocity'] - trajectory[index-1]['velocity']
        return dv / dt

    def generate_bezier_trajectory(self, control_points, n_points=100):
        """
        Generate trajectory using Bezier curves for smooth motion.

        Args:
            control_points: List of control points [[x1, y1, z1], [x2, y2, z2], ...]
            n_points: Number of points in the generated trajectory
        """
        # Convert to Bezier curve using the bezier library
        nodes = np.array(control_points).T  # Transpose for bezier format
        curve = bezier.Curve(nodes, degree=len(control_points)-1)

        # Evaluate curve at multiple points
        s_vals = np.linspace(0.0, 1.0, n_points)
        points = curve.evaluate_multi(s_vals)

        trajectory = []
        for i, s in enumerate(s_vals):
            pos = points[:, i]
            trajectory.append({
                'time': i * (1.0 / n_points),  # Simplified timing
                'position': pos,
                'velocity': self.calculate_bezier_velocity(curve, s),
                'acceleration': self.calculate_bezier_acceleration(curve, s)
            })

        return trajectory

    def calculate_bezier_velocity(self, curve, s):
        """Calculate velocity at point s on Bezier curve."""
        # First derivative of Bezier curve gives velocity
        derivative = curve.derivative()
        velocity = derivative.evaluate(s)
        return velocity.flatten()

    def calculate_bezier_acceleration(self, curve, s):
        """Calculate acceleration at point s on Bezier curve."""
        # Second derivative of Bezier curve gives acceleration
        first_deriv = curve.derivative()
        second_deriv = first_deriv.derivative()
        acceleration = second_deriv.evaluate(s)
        return acceleration.flatten()
```

## Humanoid-Specific Kinematic Challenges

### Redundancy Resolution

Humanoid robots typically have redundant DOFs that require special handling:

```python
class RedundancyResolver:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.jacobian_cache = {}

    def resolve_redundancy(self, primary_task_jacobian, primary_task_desired,
                          nullspace_objective_jacobian, nullspace_objective_desired,
                          joint_limits=None):
        """
        Resolve kinematic redundancy using nullspace projection.

        Args:
            primary_task_jacobian: Jacobian for primary task
            primary_task_desired: Desired primary task velocity
            nullspace_objective_jacobian: Jacobian for nullspace objective
            nullspace_objective_desired: Desired nullspace objective velocity
            joint_limits: Optional joint limit constraints
        """
        # Calculate pseudoinverse of primary task Jacobian
        J_primary = primary_task_jacobian
        J_pseudo_inv = np.linalg.pinv(J_primary)

        # Calculate primary joint velocities
        qdot_primary = J_pseudo_inv @ primary_task_desired

        # Calculate nullspace projection matrix
        I = np.eye(J_primary.shape[1])  # Identity matrix
        nullspace_proj = I - J_pseudo_inv @ J_primary

        # Calculate nullspace objective joint velocities
        if nullspace_objective_jacobian is not None:
            J_null = nullspace_objective_jacobian
            qdot_null = nullspace_proj @ np.linalg.pinv(J_null) @ nullspace_objective_desired
        else:
            qdot_null = np.zeros(J_primary.shape[1])

        # Combine primary and nullspace velocities
        qdot_total = qdot_primary + qdot_null

        # Apply joint limit avoidance if specified
        if joint_limits is not None:
            qdot_total = self.avoid_joint_limits(qdot_total, joint_limits)

        return qdot_total

    def avoid_joint_limits(self, joint_velocities, joint_limits, weights=None):
        """
        Modify joint velocities to avoid joint limits.

        Args:
            joint_velocities: Current joint velocities
            joint_limits: Tuple of (lower_limits, upper_limits)
            weights: Optional weights for each joint's limit avoidance
        """
        if weights is None:
            weights = np.ones(len(joint_velocities))

        lower_limits, upper_limits = joint_limits
        current_positions = self.robot.get_current_joint_positions()

        for i in range(len(joint_velocities)):
            if i < len(current_positions) and i < len(lower_limits) and i < len(upper_limits):
                pos = current_positions[i]
                lower = lower_limits[i]
                upper = upper_limits[i]

                # Calculate distance to limits
                dist_to_lower = pos - lower
                dist_to_upper = upper - pos

                # Modify velocity based on proximity to limits
                if dist_to_lower < 0.1:  # Within 0.1 radians of lower limit
                    joint_velocities[i] = max(joint_velocities[i], 0)  # Don't go lower
                elif dist_to_upper < 0.1:  # Within 0.1 radians of upper limit
                    joint_velocities[i] = min(joint_velocities[i], 0)  # Don't go higher

        return joint_velocities

    def calculate_compliance_task(self, desired_compliance, current_jacobian):
        """
        Calculate task space compliance for interaction control.
        """
        # Calculate compliance matrix (inverse of stiffness)
        compliance_matrix = np.linalg.inv(desired_compliance)

        # Map compliance to joint space using Jacobian
        joint_compliance = current_jacobian.T @ compliance_matrix @ current_jacobian

        return joint_compliance

    def calculate_manipulability(self, jacobian):
        """
        Calculate manipulability measure for the robot.

        The manipulability measure indicates how well the robot can move
        in different directions in task space.
        """
        # Calculate manipulability using the determinant of J*J^T
        JJT = jacobian @ jacobian.T
        manipulability = np.sqrt(np.linalg.det(JJT))

        return manipulability

    def find_optimal_configuration(self, task_jacobian, task_desired,
                                 optimization_function, constraints=None):
        """
        Find optimal joint configuration that maximizes some objective function
        while satisfying the primary task.

        Args:
            task_jacobian: Task Jacobian matrix
            task_desired: Desired task velocity
            optimization_function: Function to optimize (e.g., manipulability)
            constraints: Optional constraints on the optimization
        """
        from scipy.optimize import minimize

        def objective(q):
            # Calculate Jacobian at configuration q
            J = self.robot.calculate_jacobian(q)

            # Calculate manipulability or other metric
            return -optimization_function(J)  # Negative because we minimize

        # Solve inverse kinematics with optimization objective
        result = minimize(
            objective,
            x0=self.robot.get_current_configuration(),
            method='SLSQP',
            constraints=constraints
        )

        if result.success:
            return result.x
        else:
            # Fall back to standard inverse kinematics
            return self.inverse_kinematics(task_jacobian, task_desired)
```

## Practical Implementation Example

### Humanoid Arm Control System

```python
class HumanoidArmController:
    def __init__(self, robot_interface):
        self.robot = robot_interface
        self.ik_solver = NumericalInverseKinematics(robot_interface)
        self.trajectory_gen = HumanoidTrajectoryGenerator()
        self.redundancy_resolver = RedundancyResolver(robot_interface)

        # Control parameters
        self.kp_position = 100.0
        self.kd_position = 20.0
        self.kp_orientation = 50.0
        self.kd_orientation = 10.0

    def move_to_cartesian_pose(self, end_effector_name, target_pose,
                              duration=2.0, avoid_obstacles=False):
        """
        Move end effector to target Cartesian pose.

        Args:
            end_effector_name: Name of the end effector (e.g., 'left_hand', 'right_hand')
            target_pose: Target pose as [position, orientation] where position=[x,y,z]
                        and orientation=[w,x,y,z] (quaternion)
            duration: Movement duration
            avoid_obstacles: Whether to perform obstacle avoidance
        """
        # Get current joint configuration
        current_joints = self.robot.get_joint_positions()

        # Solve inverse kinematics for target pose
        try:
            target_joints = self.ik_solver.inverse_kinematics_numerical(
                target_pose[:3],  # Position
                target_pose[3:],  # Orientation
                current_joints,
                self.get_chain_joints(end_effector_name)
            )
        except Exception as e:
            print(f"IK solution failed: {e}")
            return False

        # Generate trajectory
        trajectory = self.trajectory_gen.generate_joint_trajectory(
            current_joints, target_joints, duration
        )

        # Execute trajectory
        success = self.execute_trajectory(trajectory)

        return success

    def generate_reaching_trajectory(self, target_position, preferred_ik_solution=None):
        """
        Generate trajectory for reaching a target position.

        Args:
            target_position: [x, y, z] target position
            preferred_ik_solution: Preferred joint configuration (for redundancy resolution)
        """
        current_pos, current_rot = self.robot.get_end_effector_pose('right_hand')
        current_joints = self.robot.get_joint_positions()

        # Solve inverse kinematics
        try:
            if preferred_ik_solution is not None:
                # Use redundancy resolution to prefer certain configuration
                ik_solution = self.resolve_redundancy_with_preference(
                    target_position, current_joints, preferred_ik_solution
                )
            else:
                ik_solution = self.ik_solver.inverse_kinematics_numerical(
                    target_position, [1, 0, 0, 0],  # Default orientation
                    current_joints, self.get_arm_chain_joints('right_arm')
                )
        except Exception as e:
            print(f"Could not find IK solution: {e}")
            return None

        # Generate smooth trajectory between current and target configurations
        trajectory = self.trajectory_gen.generate_joint_trajectory(
            current_joints, ik_solution, duration=3.0
        )

        return trajectory

    def resolve_redundancy_with_preference(self, target_pos, current_joints,
                                         preferred_config, weight=0.1):
        """
        Resolve redundancy while trying to maintain preferred configuration.
        """
        # This would implement a weighted least-norm approach
        # to maintain joint configuration close to preferred
        pass

    def execute_trajectory(self, trajectory):
        """
        Execute a joint trajectory on the robot.
        """
        for point in trajectory:
            # Send joint positions to robot
            self.robot.set_joint_positions(point['positions'])

            # Wait for control timestep
            self.robot.wait_for_control_timestep()

            # Check for safety conditions
            if self.robot.emergency_stop_requested():
                return False

        return True

    def get_arm_chain_joints(self, arm_name):
        """
        Get joint names for specified arm.
        """
        if arm_name == 'left_arm':
            return ['l_shoulder_pitch', 'l_shoulder_roll', 'l_shoulder_yaw',
                   'l_elbow_pitch', 'l_wrist_yaw', 'l_wrist_pitch']
        elif arm_name == 'right_arm':
            return ['r_shoulder_pitch', 'r_shoulder_roll', 'r_shoulder_yaw',
                   'r_elbow_pitch', 'r_wrist_yaw', 'r_wrist_pitch']
        else:
            return []

    def calculate_arm_workspace(self, arm_name, resolution=0.1):
        """
        Calculate reachable workspace for the specified arm.
        """
        workspace_points = []
        joint_limits = self.robot.get_joint_limits(self.get_arm_chain_joints(arm_name))

        # Sample joint space within limits
        for joint_angles in self.sample_joint_space(joint_limits, resolution):
            try:
                pos, rot = self.robot.forward_kinematics(joint_angles, arm_name)
                workspace_points.append(pos)
            except:
                continue  # Skip unreachable configurations

        return np.array(workspace_points)

    def sample_joint_space(self, joint_limits, resolution):
        """
        Sample joint space for workspace calculation.
        This is a simplified approach - more sophisticated methods exist.
        """
        # For demonstration, return a few sample configurations
        samples = []

        # Sample a few key configurations
        for i in range(100):  # Generate 100 random samples
            joint_angles = []
            for lim in joint_limits:
                # Sample uniformly between joint limits
                angle = np.random.uniform(lim[0], lim[1])
                joint_angles.append(angle)
            samples.append(joint_angles)

        return samples

class HumanoidWalkingController:
    def __init__(self, robot_interface):
        self.robot = robot_interface
        self.trajectory_generator = HumanoidTrajectoryGenerator()
        self.com_controller = COMController()
        self.foot_step_planner = FootstepPlanner()

    def walk_to_pose(self, target_pose, step_size=0.3, step_width=0.2):
        """
        Plan and execute walking to target pose.

        Args:
            target_pose: Target pose [x, y, theta]
            step_size: Size of each step (m)
            step_width: Lateral distance between feet (m)
        """
        # Plan footstep sequence
        footsteps = self.foot_step_planner.plan_to_pose(
            self.robot.get_current_pose(), target_pose, step_size, step_width
        )

        # Generate walking pattern
        walking_pattern = self.generate_walking_pattern(footsteps)

        # Execute walking
        self.execute_walking_pattern(walking_pattern)

    def generate_walking_pattern(self, footsteps):
        """
        Generate complete walking pattern from footstep plan.
        """
        # This would generate:
        # - CoM trajectory to maintain balance
        # - Swing foot trajectories
        # - Support foot trajectories
        # - Joint trajectories for entire body
        pass

    def execute_walking_pattern(self, pattern):
        """
        Execute the walking pattern on the robot.
        """
        # This would coordinate:
        # - CoM control for balance
        # - Foot trajectory following
        # - Joint control for stable walking
        pass
```

## Summary

Humanoid kinematics and motion planning involve complex mathematical formulations to handle the high degrees of freedom and redundancy inherent in human-like robotic systems. Key aspects include:

1. **Multi-chain kinematics**: Managing multiple simultaneous kinematic chains (arms, legs)
2. **Redundancy resolution**: Handling excess DOFs through nullspace optimization
3. **Whole-body coordination**: Integrating all body parts for coordinated motion
4. **Balance maintenance**: Ensuring stability during dynamic movements
5. **Trajectory generation**: Creating smooth, feasible motion paths
6. **Real-time control**: Executing complex kinematic solutions in real-time

The combination of analytical and numerical methods allows humanoid robots to perform complex tasks while maintaining balance and avoiding self-collision, making them suitable for human-centered environments.