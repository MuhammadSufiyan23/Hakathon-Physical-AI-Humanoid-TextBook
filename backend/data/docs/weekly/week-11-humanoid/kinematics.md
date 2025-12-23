---
sidebar_label: 'Humanoid Kinematics and Motion Planning'
title: 'Humanoid Kinematics and Motion Planning'
---

# Humanoid Kinematics and Motion Planning

## Introduction to Humanoid Kinematics

Humanoid kinematics deals with the mathematical description of motion for robots with human-like structure. Unlike simpler robots, humanoids have complex kinematic chains involving multiple limbs, each with multiple degrees of freedom (DOF), requiring sophisticated mathematical approaches to describe and control their motion.

## Humanoid Kinematic Structure

### Typical Humanoid Configuration

A standard humanoid robot typically consists of:

```
                    Head
                     |
                   Neck
                     |
                   Torso
                  /     \
                /         \
            Left Arm    Right Arm
            /              \
        Shoulder          Shoulder
        /   |              |   \
     Elbow  |            |  Elbow
     /      |            |      \
   Wrist    |            |     Wrist
    |       |            |       |
  Hand    Left Leg    Right Leg  Hand
          /    \        /    \
       Hip     Hip    Hip     Hip
       /       /        \       \
    Knee    Knee      Knee    Knee
    /       /           \       \
  Ankle   Ankle       Ankle   Ankle
   |       |            |       |
  Foot    Foot         Foot    Foot
```

### Joint Classification

#### Upper Body (Arms)
- **Shoulder**: 3-7 DOF (depending on design)
- **Elbow**: 1-2 DOF (flexion/extension, sometimes pronation/supination)
- **Wrist**: 1-3 DOF (flexion/extension, abduction/adduction, rotation)
- **Hand**: 10-20+ DOF (individual finger joints)

#### Lower Body (Legs)
- **Hip**: 3-6 DOF (flexion/extension, abduction/adduction, internal/external rotation)
- **Knee**: 1 DOF (flexion/extension)
- **Ankle**: 2-3 DOF (dorsiflexion/plantarflexion, inversion/eversion)
- **Foot**: 0-2 DOF (toe flexion/extension in some designs)

## Forward Kinematics

Forward kinematics calculates the position and orientation of end-effectors (hands, feet) given joint angles.

### Mathematical Representation

```python
import numpy as np
import math

def rotation_matrix_x(angle):
    """Rotation matrix around X-axis."""
    return np.array([
        [1, 0, 0],
        [0, math.cos(angle), -math.sin(angle)],
        [0, math.sin(angle), math.cos(angle)]
    ])

def rotation_matrix_y(angle):
    """Rotation matrix around Y-axis."""
    return np.array([
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]
    ])

def rotation_matrix_z(angle):
    """Rotation matrix around Z-axis."""
    return np.array([
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ])

def dh_transform(a, alpha, d, theta):
    """Denavit-Hartenberg transformation matrix."""
    return np.array([
        [math.cos(theta), -math.sin(theta)*math.cos(alpha), math.sin(theta)*math.sin(alpha), a*math.cos(theta)],
        [math.sin(theta), math.cos(theta)*math.cos(alpha), -math.cos(theta)*math.sin(alpha), a*math.sin(theta)],
        [0, math.sin(alpha), math.cos(alpha), d],
        [0, 0, 0, 1]
    ])

class HumanoidArmKinematics:
    def __init__(self, arm_lengths):
        """
        Initialize arm kinematics with link lengths.
        arm_lengths: [upper_arm_length, forearm_length, hand_length]
        """
        self.l1 = arm_lengths[0]  # Shoulder to elbow
        self.l2 = arm_lengths[1]  # Elbow to wrist
        self.l3 = arm_lengths[2]  # Wrist to hand tip

    def forward_kinematics(self, shoulder_pitch, shoulder_roll, shoulder_yaw,
                          elbow_flex, wrist_pitch, wrist_yaw):
        """
        Calculate end-effector position using forward kinematics.
        All angles in radians.
        """
        # Shoulder transformations
        T_shoulder = dh_transform(0, -math.pi/2, 0, shoulder_yaw) @ \
                    dh_transform(0, math.pi/2, 0, shoulder_pitch) @ \
                    dh_transform(self.l1, 0, 0, shoulder_roll)

        # Elbow transformation
        T_elbow = T_shoulder @ dh_transform(0, -math.pi/2, 0, elbow_flex)

        # Wrist transformations
        T_wrist = T_elbow @ dh_transform(self.l2, 0, 0, wrist_yaw) @ \
                 dh_transform(0, math.pi/2, 0, wrist_pitch)

        # End effector position
        end_effector_pos = T_wrist[:3, 3]

        # End effector orientation (simplified)
        end_effector_rot = T_wrist[:3, :3]

        return end_effector_pos, end_effector_rot

    def calculate_arm_workspace(self, resolution=0.1):
        """Calculate reachable workspace for the arm."""
        workspace_points = []

        # Define joint angle ranges (in radians)
        pitch_range = np.arange(-0.5, 0.5, resolution)
        roll_range = np.arange(-1.0, 1.0, resolution)
        yaw_range = np.arange(-1.0, 1.0, resolution)
        elbow_range = np.arange(0, 1.5, resolution)

        for pitch in pitch_range:
            for roll in roll_range:
                for yaw in yaw_range:
                    for elbow in elbow_range:
                        pos, _ = self.forward_kinematics(pitch, roll, yaw, elbow, 0, 0)
                        workspace_points.append(pos)

        return np.array(workspace_points)
```

### Leg Forward Kinematics

```python
class HumanoidLegKinematics:
    def __init__(self, leg_lengths):
        """
        Initialize leg kinematics with link lengths.
        leg_lengths: [hip_to_knee, knee_to_ankle, ankle_to_foot]
        """
        self.thigh = leg_lengths[0]   # Hip to knee
        self.shin = leg_lengths[1]    # Knee to ankle
        self.foot = leg_lengths[2]    # Ankle to foot tip

    def forward_kinematics(self, hip_flex, hip_abd, hip_rot,
                          knee_flex, ankle_pitch, ankle_roll):
        """
        Calculate foot position using forward kinematics.
        All angles in radians.
        """
        # Hip transformations
        T_hip = dh_transform(0, -math.pi/2, 0, hip_rot) @ \
               dh_transform(0, math.pi/2, 0, hip_flex) @ \
               dh_transform(0, -math.pi/2, 0, hip_abd)

        # Knee transformation
        T_knee = T_hip @ dh_transform(self.thigh, 0, 0, knee_flex)

        # Ankle transformations
        T_ankle = T_knee @ dh_transform(0, -math.pi/2, 0, ankle_roll) @ \
                 dh_transform(self.shin, 0, 0, ankle_pitch)

        # Foot transformation
        T_foot = T_ankle @ dh_transform(self.foot, 0, 0, 0)

        # Foot position and orientation
        foot_pos = T_foot[:3, 3]
        foot_rot = T_foot[:3, :3]

        return foot_pos, foot_rot

    def calculate_leg_workspace(self, resolution=0.05):
        """Calculate reachable workspace for the leg."""
        workspace_points = []

        # Define joint angle ranges for leg
        hip_flex_range = np.arange(-0.5, 1.0, resolution)
        hip_abd_range = np.arange(-0.5, 0.5, resolution)
        knee_flex_range = np.arange(0, 2.0, resolution)

        for hip_flex in hip_flex_range[:10]:  # Limit for performance
            for hip_abd in hip_abd_range[:10]:
                for knee_flex in knee_flex_range[:10]:
                    pos, _ = self.forward_kinematics(hip_flex, hip_abd, 0, knee_flex, 0, 0)
                    workspace_points.append(pos)

        return np.array(workspace_points)
```

## Inverse Kinematics

Inverse kinematics solves for joint angles given desired end-effector position and orientation. This is crucial for humanoid motion planning.

### Analytical vs Numerical Methods

#### Analytical Solution (for 6-DOF arm)

```python
class HumanoidArmAnalyticalIK:
    def __init__(self, arm_lengths):
        self.l1 = arm_lengths[0]  # Shoulder to elbow
        self.l2 = arm_lengths[1]  # Elbow to wrist
        self.l3 = arm_lengths[2]  # Wrist to hand tip

    def inverse_kinematics_6dof(self, target_pos, target_rot, elbow_pos='up'):
        """
        Analytical inverse kinematics for 6-DOF arm.
        Returns joint angles [shoulder_yaw, shoulder_pitch, shoulder_roll,
                             elbow_flex, wrist_yaw, wrist_pitch]
        """
        x, y, z = target_pos

        # Calculate wrist position (accounting for wrist length)
        wrist_pos = target_pos - self.l3 * target_rot[:3, 2]  # Move back along approach vector

        # Shoulder yaw (rotation around Z-axis)
        shoulder_yaw = math.atan2(wrist_pos[1], wrist_pos[0])

        # Shoulder pitch and roll (solve for shoulder position)
        # Calculate distance from shoulder to wrist
        dist = math.sqrt(wrist_pos[0]**2 + wrist_pos[1]**2 + (wrist_pos[2])**2)

        # Use law of cosines to find shoulder-roll angle
        try:
            # Angle at shoulder joint
            cos_shoulder_roll = (self.l1**2 + dist**2 - self.l2**2) / (2 * self.l1 * dist)
            cos_shoulder_roll = max(-1, min(1, cos_shoulder_roll))  # Clamp to valid range
            alpha = math.acos(cos_shoulder_roll)

            # Angle at wrist joint
            cos_wrist_angle = (self.l1**2 + self.l2**2 - dist**2) / (2 * self.l1 * self.l2)
            cos_wrist_angle = max(-1, min(1, cos_wrist_angle))
            beta = math.acos(cos_wrist_angle)

            # Calculate shoulder pitch and roll
            shoulder_pitch = math.atan2(wrist_pos[2], math.sqrt(wrist_pos[0]**2 + wrist_pos[1]**2))

            # Calculate shoulder roll based on elbow position
            if elbow_pos == 'up':
                shoulder_roll = alpha + math.atan2(math.sqrt(wrist_pos[0]**2 + wrist_pos[1]**2), wrist_pos[2])
            else:
                shoulder_roll = alpha - math.atan2(math.sqrt(wrist_pos[0]**2 + wrist_pos[1]**2), wrist_pos[2])

            # Elbow flex angle
            elbow_flex = math.pi - beta

            # Wrist angles (to achieve desired orientation)
            # This is simplified - full solution would involve more complex calculations
            wrist_yaw = math.atan2(target_rot[1, 2], target_rot[0, 2])
            wrist_pitch = math.atan2(-target_rot[2, 2],
                                    math.sqrt(target_rot[0, 2]**2 + target_rot[1, 2]**2))

            return [shoulder_yaw, shoulder_pitch, shoulder_roll, elbow_flex, wrist_yaw, wrist_pitch]

        except ValueError:
            # Solution not possible
            return None
```

#### Numerical Solution (Jacobian-based)

```python
class HumanoidNumericalIK:
    def __init__(self, robot_model):
        self.robot_model = robot_model
        self.learning_rate = 0.01
        self.max_iterations = 100
        self.tolerance = 1e-4

    def calculate_jacobian(self, joint_angles, chain_type='arm'):
        """Calculate geometric Jacobian matrix."""
        n_joints = len(joint_angles)
        jacobian = np.zeros((6, n_joints))  # 6 DoF: 3 position + 3 orientation

        # Get current end-effector pose and joint positions
        current_pos, current_rot = self.forward_kinematics(joint_angles, chain_type)

        # Calculate transformation matrices for each joint
        transforms = self.calculate_transform_chain(joint_angles, chain_type)

        # Get end-effector position in base frame
        end_effector_pos = transforms[-1][:3, 3]

        # Calculate Jacobian columns
        for i in range(n_joints):
            # Z-axis of joint i in base frame
            z_i = transforms[i][:3, 2]  # Third column of rotation matrix

            # Position vector from joint i to end-effector
            r_i = end_effector_pos - transforms[i][:3, 3]

            # Position part of Jacobian (linear velocity contribution)
            jacobian[:3, i] = np.cross(z_i, r_i)

            # Orientation part of Jacobian (angular velocity contribution)
            jacobian[3:, i] = z_i

        return jacobian

    def forward_kinematics(self, joint_angles, chain_type):
        """Calculate forward kinematics for given joint angles."""
        # This would use the specific robot model
        # For this example, we'll return a placeholder
        return np.array([0, 0, 0]), np.eye(3)

    def calculate_transform_chain(self, joint_angles, chain_type):
        """Calculate transformation chain for all joints."""
        # This would implement the full DH parameter transformation
        # For this example, we'll return identity matrices
        n_joints = len(joint_angles)
        transforms = [np.eye(4) for _ in range(n_joints)]
        return transforms

    def inverse_kinematics(self, target_pose, initial_joints, chain_type='arm'):
        """
        Solve inverse kinematics using numerical methods.
        target_pose: [x, y, z, roll, pitch, yaw] or SE(3) matrix
        initial_joints: initial joint angle configuration
        """
        current_joints = np.array(initial_joints)

        for iteration in range(self.max_iterations):
            # Calculate current end-effector pose
            current_pos, current_rot = self.forward_kinematics(current_joints, chain_type)

            # Calculate position and orientation errors
            pos_error = target_pose[:3] - current_pos

            # For orientation, use a simple approach (in practice, use rotation error)
            rot_error = self.calculate_rotation_error(current_rot, target_pose[3:])

            # Combine position and orientation errors
            error = np.concatenate([pos_error, rot_error])

            # Check convergence
            if np.linalg.norm(error) < self.tolerance:
                print(f'IK converged after {iteration} iterations')
                return current_joints.tolist()

            # Calculate Jacobian
            jacobian = self.calculate_jacobian(current_joints, chain_type)

            # Solve for joint velocities using damped least squares
            damping = 0.01
            I = np.eye(len(current_joints))
            try:
                joint_velocities = np.linalg.solve(
                    jacobian.T @ jacobian + damping * I,
                    jacobian.T @ error
                )

                # Update joint angles
                current_joints = current_joints + self.learning_rate * joint_velocities

            except np.linalg.LinAlgError:
                # Handle singularities
                print(f'Singular configuration at iteration {iteration}')
                break

        print('IK did not converge within maximum iterations')
        return current_joints.tolist()

    def calculate_rotation_error(self, current_rot, target_rot):
        """Calculate rotation error between current and target orientations."""
        # Simple approach: use angle-axis representation
        # In practice, use more sophisticated rotation error calculations
        return np.array([0, 0, 0])  # Placeholder
```

## Humanoid Motion Planning

### Whole-Body Motion Planning

```python
class HumanoidMotionPlanner:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.base_support_polygon = None
        self.step_planner = FootstepPlanner()
        self.com_trajectory_generator = COMTrajectoryGenerator()
        self.ik_solver = HumanoidNumericalIK(robot_model)

    def plan_reaching_motion(self, target_pos, target_rot, support_leg='left'):
        """
        Plan reaching motion while maintaining balance.
        target_pos: [x, y, z] - target position for reaching hand
        target_rot: [roll, pitch, yaw] - target orientation for reaching hand
        support_leg: 'left', 'right', or 'both' - supporting leg configuration
        """
        # 1. Check if target is reachable
        if not self.is_reachable(target_pos, support_leg):
            raise ValueError("Target position is not reachable")

        # 2. Plan center of mass trajectory to maintain balance
        com_trajectory = self.com_trajectory_generator.plan_trajectory(
            target_pos, support_leg
        )

        # 3. Plan stepping motion if needed for balance
        footstep_plan = self.step_planner.plan_footsteps(
            com_trajectory, support_leg
        )

        # 4. Generate joint trajectories for reaching
        joint_trajectory = self.generate_reaching_trajectory(
            target_pos, target_rot, com_trajectory, support_leg
        )

        return {
            'com_trajectory': com_trajectory,
            'footstep_plan': footstep_plan,
            'joint_trajectory': joint_trajectory
        }

    def is_reachable(self, target_pos, support_leg):
        """Check if target position is reachable while maintaining balance."""
        # Calculate workspace considering balance constraints
        # This would involve checking if the target is within the workspace
        # of the arm while keeping the center of mass within the support polygon

        # Simplified check
        arm_workspace = self.calculate_arm_workspace(support_leg)

        # Check if target is approximately within workspace
        # (In practice, this would be much more complex)
        return True

    def generate_reaching_trajectory(self, target_pos, target_rot, com_trajectory, support_leg):
        """Generate joint trajectory for reaching motion."""
        # Sample trajectory points
        n_waypoints = 50
        trajectory = []

        # Interpolate from current to target position
        current_pos, current_rot = self.get_current_hand_pose(support_leg)

        for i in range(n_waypoints):
            t = i / (n_waypoints - 1)

            # Interpolate position
            pos = (1 - t) * current_pos + t * target_pos
            rot = self.interpolate_rotation(current_rot, target_rot, t)

            # Solve inverse kinematics
            joint_angles = self.ik_solver.inverse_kinematics(
                np.concatenate([pos, rot]),
                self.get_current_joints(),
                'arm'
            )

            trajectory.append({
                'time': t,
                'joint_angles': joint_angles,
                'hand_pose': (pos, rot)
            })

        return trajectory

    def get_current_hand_pose(self, hand='right'):
        """Get current hand pose from current joint angles."""
        # This would call forward kinematics with current joint angles
        return np.array([0, 0, 0]), np.array([0, 0, 0])

    def get_current_joints(self):
        """Get current joint angles."""
        # This would return current joint state from robot
        return [0] * 30  # Placeholder for 30 DOF humanoid

    def interpolate_rotation(self, start_rot, end_rot, t):
        """Interpolate between two rotations."""
        # Use spherical linear interpolation (SLERP) for quaternions
        # or simple linear interpolation for Euler angles
        return (1 - t) * start_rot + t * end_rot
```

### Walking Pattern Generation

```python
class WalkingPatternGenerator:
    def __init__(self):
        self.step_length = 0.3  # meters
        self.step_width = 0.2   # meters
        self.step_height = 0.05 # meters (foot lift)
        self.cycle_time = 1.0   # seconds per step

    def generate_walk_pattern(self, num_steps, walk_direction='forward'):
        """
        Generate walking pattern for humanoid robot.
        num_steps: number of steps to generate
        walk_direction: 'forward', 'backward', 'left', 'right', 'turn_left', 'turn_right'
        """
        footsteps = []

        # Starting position
        x, y, theta = 0.0, 0.0, 0.0

        for i in range(num_steps):
            # Determine which foot to step with
            foot = 'left' if i % 2 == 0 else 'right'

            # Calculate step offset based on walking direction
            if walk_direction == 'forward':
                dx, dy, dtheta = self.step_length, 0, 0
            elif walk_direction == 'backward':
                dx, dy, dtheta = -self.step_length, 0, 0
            elif walk_direction == 'left':
                dx, dy, dtheta = 0, self.step_width, 0
            elif walk_direction == 'right':
                dx, dy, dtheta = 0, -self.step_width, 0
            elif walk_direction == 'turn_left':
                dx, dy, dtheta = 0, 0, 0.2  # radians
            elif walk_direction == 'turn_right':
                dx, dy, dtheta = 0, 0, -0.2
            else:
                dx, dy, dtheta = 0, 0, 0

            # Apply step offset
            if foot == 'left':
                x += dx
                y += self.step_width / 2
                theta += dtheta
            else:  # right foot
                x += dx
                y -= self.step_width / 2
                theta += dtheta

            # Create footstep
            footstep = {
                'step_num': i,
                'foot': foot,
                'position': (x, y, 0.0),
                'orientation': (0, 0, theta),
                'timing': i * self.cycle_time,
                'lift_height': self.step_height
            }

            footsteps.append(footstep)

        return footsteps

    def generate_com_trajectory(self, footsteps, z_height=0.8):
        """
        Generate center of mass trajectory following the footsteps.
        Uses inverted pendulum model for balance.
        """
        com_trajectory = []

        for i, step in enumerate(footsteps):
            # Calculate CoM position based on inverted pendulum model
            # This is a simplified version - real implementation would be more complex
            time_in_cycle = (step['timing'] % self.cycle_time) / self.cycle_time

            # Smooth CoM transition between steps
            if i == 0:
                com_x = step['position'][0]
                com_y = step['position'][1]
            else:
                prev_step = footsteps[i-1]
                # Interpolate between previous and current step positions
                com_x = (1 - time_in_cycle) * prev_step['position'][0] + time_in_cycle * step['position'][0]
                com_y = (1 - time_in_cycle) * prev_step['position'][1] + time_in_cycle * step['position'][1]

            # Add slight oscillation for natural movement
            oscillation = 0.01 * math.sin(2 * math.pi * step['timing'])
            com_z = z_height + oscillation

            com_trajectory.append({
                'time': step['timing'],
                'position': (com_x, com_y, com_z),
                'velocity': self.calculate_com_velocity(com_trajectory, step['timing'])
            })

        return com_trajectory

    def calculate_com_velocity(self, com_trajectory, current_time):
        """Calculate CoM velocity from trajectory."""
        # Simplified velocity calculation
        if len(com_trajectory) < 2:
            return (0, 0, 0)

        # Use finite differences
        dt = 0.01  # 10ms time step
        # This would be implemented with proper differentiation
        return (0, 0, 0)
```

### Balance Control

```python
class BalanceController:
    def __init__(self):
        self.zmp_controller = ZMPController()
        self.com_estimator = COMEstimator()
        self.foot_pressure_sensors = FootPressureSensors()

        # Control gains
        self.kp_com = 10.0  # Proportional gain for CoM control
        self.kd_com = 2.0   # Derivative gain for CoM control
        self.kp_zmp = 5.0   # Proportional gain for ZMP control

    def calculate_balance_correction(self, current_state, desired_state):
        """
        Calculate balance correction torques.
        current_state: dict with current robot state
        desired_state: dict with desired robot state
        """
        # Estimate current center of mass
        current_com = self.com_estimator.estimate(current_state)

        # Calculate desired ZMP based on CoM trajectory
        desired_zmp = self.calculate_desired_zmp(current_com, desired_state)

        # Measure current ZMP from pressure sensors
        measured_zmp = self.foot_pressure_sensors.get_zmp()

        # Calculate ZMP error
        zmp_error = desired_zmp - measured_zmp

        # Generate corrective joint torques
        correction_torques = self.zmp_controller.compute_torques(
            zmp_error, current_state
        )

        return correction_torques

    def calculate_desired_zmp(self, current_com, desired_state):
        """Calculate desired ZMP based on inverted pendulum model."""
        # Inverted pendulum model: ZMP = CoM - (CoM_height / gravity) * CoM_acceleration
        gravity = 9.81
        com_height = current_com[2]

        # Calculate desired CoM acceleration
        desired_com_acc = self.calculate_com_acceleration(desired_state)

        # Calculate desired ZMP
        desired_zmp = current_com[:2] - (com_height / gravity) * desired_com_acc[:2]

        return desired_zmp

    def calculate_com_acceleration(self, desired_state):
        """Calculate desired CoM acceleration."""
        # This would implement trajectory following control
        # For this example, return zero acceleration
        return np.array([0, 0, 0])
```

## Optimization Techniques

### Trajectory Optimization

```python
import cvxpy as cp

class TrajectoryOptimizer:
    def __init__(self):
        self.dt = 0.01  # Time step
        self.weight_smoothness = 1.0
        self.weight_energymotion = 0.1

    def optimize_trajectory(self, waypoints, initial_state, final_state):
        """
        Optimize trajectory using convex optimization.
        Minimizes jerk (smoothness) and energy while satisfying constraints.
        """
        n_waypoints = len(waypoints)
        n_vars = n_waypoints * 3  # 3D positions for each waypoint

        # Define optimization variables
        positions = cp.Variable((n_waypoints, 3))

        # Objective function: minimize jerk and energy
        jerk_cost = 0
        energy_cost = 0

        for i in range(2, n_waypoints - 2):
            # Jerk is third derivative of position
            jerk = (positions[i+2] - 3*positions[i+1] + 3*positions[i] - positions[i-1]) / (self.dt**3)
            jerk_cost += cp.sum_squares(jerk)

            # Velocity
            vel = (positions[i+1] - positions[i-1]) / (2 * self.dt)
            energy_cost += cp.sum_squares(vel)

        objective = cp.Minimize(
            self.weight_smoothness * jerk_cost +
            self.weight_energymotion * energy_cost
        )

        # Constraints
        constraints = []

        # Waypoint constraints
        for i, waypoint in enumerate(waypoints):
            constraints.append(positions[i, :] == waypoint)

        # Boundary conditions
        constraints.append(positions[0, :] == initial_state[:3])
        constraints.append(positions[-1, :] == final_state[:3])

        # Velocity constraints (start and end with zero velocity)
        constraints.append((positions[1, :] - positions[0, :]) / self.dt == np.zeros(3))
        constraints.append((positions[-1, :] - positions[-2, :]) / self.dt == np.zeros(3))

        # Solve optimization problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        if problem.status not in ["infeasible", "unbounded"]:
            return positions.value
        else:
            raise ValueError(f"Optimization failed: {problem.status}")
```

## Humanoid-Specific Challenges

### Redundancy Resolution

Humanoid robots typically have redundant DOFs (more joints than necessary for a task), requiring special consideration:

```python
class RedundancyResolver:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.nullspace_weights = np.ones(robot_model.num_joints)

    def resolve_redundancy(self, primary_solution, nullspace_objective):
        """
        Resolve redundancy using nullspace projection.
        primary_solution: solution for primary task
        nullspace_objective: objective to optimize in nullspace
        """
        # Calculate Jacobian
        jacobian = self.robot.calculate_jacobian()

        # Calculate nullspace projection matrix
        I = np.eye(self.robot.num_joints)
        pseudo_inverse = np.linalg.pinv(jacobian)
        nullspace_proj = I - pseudo_inverse @ jacobian

        # Optimize nullspace objective
        weighted_nullspace = self.nullspace_weights * nullspace_proj
        nullspace_solution = weighted_nullspace @ nullspace_objective

        # Combine primary and nullspace solutions
        final_solution = primary_solution + nullspace_solution

        return final_solution
```

## Summary

Humanoid kinematics and motion planning involve complex mathematical formulations to describe and control robots with human-like structure. The challenges include dealing with redundant DOFs, maintaining balance during motion, and coordinating multiple limbs simultaneously. Modern approaches combine analytical solutions with numerical optimization techniques to achieve efficient and stable humanoid motion. Understanding these concepts is crucial for developing advanced humanoid robotic systems capable of performing complex tasks in human environments.