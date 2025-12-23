---
sidebar_label: 'Humanoid Control Systems and Algorithms'
title: 'Humanoid Control Systems and Algorithms'
---

# Humanoid Control Systems and Algorithms

## Introduction to Humanoid Control

Humanoid control systems are among the most challenging in robotics due to the complex dynamics, underactuation, and need for stable, human-like motion. Unlike wheeled or fixed-base robots, humanoid robots must maintain balance while performing tasks, requiring sophisticated control architectures that coordinate multiple subsystems.

## Control Architecture Overview

### Hierarchical Control Structure

Humanoid control typically follows a hierarchical structure:

```
High-Level Planner
├── Task Planning
├── Motion Planning
└── Path Planning

Middle-Level Controller
├── Whole-Body Controller
├── Balance Controller
├── Walking Pattern Generator
└── Trajectory Planner

Low-Level Controller
├── Joint Controllers
├── Motor Drivers
├── Sensor Processing
└── Safety Systems
```

### Control Frequency Requirements

Different control tasks require different frequencies:

- **High-level planning**: 1-10 Hz
- **Balance control**: 100-200 Hz
- **Walking control**: 50-100 Hz
- **Joint control**: 1000+ Hz
- **Safety systems**: 1000+ Hz

## Balance Control Systems

### Zero Moment Point (ZMP) Control

ZMP control is fundamental for humanoid balance:

```python
import numpy as np
import math
from scipy import signal
from scipy.optimize import minimize

class ZMPController:
    def __init__(self, com_height=0.8, gravity=9.81):
        self.com_height = com_height  # Center of mass height
        self.gravity = gravity
        self.omega = math.sqrt(gravity / com_height)  # Natural frequency
        self.zmp_error_integral = np.zeros(2)
        self.previous_zmp_error = np.zeros(2)

        # Control gains
        self.kp_zmp = 10.0  # Proportional gain
        self.ki_zmp = 1.0   # Integral gain
        self.kd_zmp = 2.0   # Derivative gain

        # Support polygon (defined by foot positions)
        self.support_polygon = None
        self.current_support_foot = 'left'

    def calculate_zmp(self, com_pos, com_acc):
        """
        Calculate Zero Moment Point from CoM position and acceleration.

        Args:
            com_pos: [x, y, z] center of mass position
            com_acc: [ẍ, ÿ, z̈] center of mass acceleration

        Returns:
            zmp: [x, y] zero moment point position
        """
        zmp_x = com_pos[0] - (self.com_height / self.gravity) * com_acc[0]
        zmp_y = com_pos[1] - (self.com_height / self.gravity) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def update_support_polygon(self, left_foot_pos, right_foot_pos):
        """
        Update support polygon based on foot positions.

        Args:
            left_foot_pos: [x, y, z] position of left foot
            right_foot_pos: [x, y, z] position of right foot
        """
        # Calculate support polygon vertices
        if self.current_support_foot == 'double':
            # Double support - use both feet
            foot_width = 0.15  # Approximate foot width
            foot_length = 0.20  # Approximate foot length

            # Create polygon from both feet
            left_vertices = self.get_foot_polygon(left_foot_pos, foot_width, foot_length)
            right_vertices = self.get_foot_polygon(right_foot_pos, foot_width, foot_length)

            # Combine vertices to form support polygon
            all_vertices = np.vstack([left_vertices, right_vertices])

            # Calculate convex hull (simplified)
            self.support_polygon = self.calculate_convex_hull(all_vertices)

        elif self.current_support_foot == 'left':
            # Single support on left foot
            foot_width = 0.15
            foot_length = 0.20
            self.support_polygon = self.get_foot_polygon(left_foot_pos, foot_width, foot_length)

        else:  # right foot support
            foot_width = 0.15
            foot_length = 0.20
            self.support_polygon = self.get_foot_polygon(right_foot_pos, foot_width, foot_length)

    def get_foot_polygon(self, foot_pos, width, length):
        """
        Get polygon representing a foot's support area.
        """
        # Create rectangle around foot position
        x, y, z = foot_pos
        half_width = width / 2
        half_length = length / 2

        vertices = np.array([
            [x - half_length, y - half_width, z],
            [x + half_length, y - half_width, z],
            [x + half_length, y + half_width, z],
            [x - half_length, y + half_width, z]
        ])

        return vertices[:, :2]  # Return only x,y coordinates

    def is_zmp_stable(self, zmp_pos):
        """
        Check if ZMP is within support polygon.

        Args:
            zmp_pos: [x, y] current ZMP position

        Returns:
            bool: True if ZMP is stable (inside support polygon)
        """
        if self.support_polygon is None:
            return False

        # Use ray casting algorithm to check if point is inside polygon
        x, y = zmp_pos
        n = len(self.support_polygon)
        inside = False

        p1x, p1y = self.support_polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = self.support_polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def compute_balance_correction(self, current_zmp, desired_zmp, dt=0.01):
        """
        Compute balance correction torques using PID control on ZMP error.

        Args:
            current_zmp: [x, y] current ZMP position
            desired_zmp: [x, y] desired ZMP position
            dt: Time step

        Returns:
            correction_torques: Joint torques for balance correction
            zmp_error: Current ZMP error
        """
        # Calculate ZMP error
        zmp_error = desired_zmp - current_zmp

        # Update integral term
        self.zmp_error_integral += zmp_error * dt

        # Calculate derivative term
        zmp_error_derivative = (zmp_error - self.previous_zmp_error) / dt if dt > 0 else np.zeros(2)

        # Store current error for next iteration
        self.previous_zmp_error = zmp_error

        # PID control
        correction = (self.kp_zmp * zmp_error +
                     self.ki_zmp * self.zmp_error_integral +
                     self.kd_zmp * zmp_error_derivative)

        # Map ZMP correction to joint torques
        # This is simplified - real implementation would use whole-body control
        joint_correction = self.map_zmp_to_joints(correction)

        return joint_correction, zmp_error

    def map_zmp_to_joints(self, zmp_correction):
        """
        Map ZMP correction to joint space torques.
        This is a simplified mapping - real implementation would use
        whole-body control techniques.
        """
        # In practice, this would involve complex whole-body control
        # such as operational space control or quadratic programming
        n_joints = 28  # Typical humanoid has ~28 DOF
        joint_torques = np.zeros(n_joints)

        # Distribute correction to balance-critical joints
        # These are typically ankle, hip, and trunk joints
        balance_joints = {
            'left_ankle_roll': 0.3,   # 30% to left ankle roll
            'left_ankle_pitch': 0.3,  # 30% to left ankle pitch
            'right_ankle_roll': 0.3,  # 30% to right ankle roll
            'right_ankle_pitch': 0.3, # 30% to right ankle pitch
            'left_hip_roll': 0.1,     # 10% to left hip roll
            'right_hip_roll': 0.1,    # 10% to right hip roll
            'torso_pitch': 0.05,      # 5% to torso pitch
            'torso_roll': 0.05        # 5% to torso roll
        }

        # Apply corrections based on ZMP error direction
        # X-direction ZMP error -> pitch corrections
        joint_torques[12] = zmp_correction[0] * balance_joints['left_ankle_pitch']  # Left ankle pitch
        joint_torques[13] = zmp_correction[0] * balance_joints['right_ankle_pitch']  # Right ankle pitch

        # Y-direction ZMP error -> roll corrections
        joint_torques[11] = zmp_correction[1] * balance_joints['left_ankle_roll']   # Left ankle roll
        joint_torques[14] = zmp_correction[1] * balance_joints['right_ankle_roll']  # Right ankle roll

        return joint_torques
```

### Linear Inverted Pendulum Model (LIPM)

The LIPM simplifies humanoid dynamics for walking control:

```python
class LinearInvertedPendulumController:
    def __init__(self, com_height=0.8, gravity=9.81):
        self.com_height = com_height
        self.gravity = gravity
        self.omega = math.sqrt(gravity / com_height)

        # Pre-compute constants
        self.com_height_gravity_ratio = com_height / gravity

    def lipm_zmp_equation(self, com_pos, com_vel):
        """
        Calculate ZMP from CoM position and velocity using LIPM.

        For LIPM: ZMP = CoM - (h/g) * CoM_acceleration
        But we can also express it as: ZMP = CoM - (1/ω²) * CoM_acceleration
        """
        # In LIPM, the relationship is:
        # ZMP = CoM - (h/g) * CoM_acceleration
        # Since CoM_acceleration = ω² * (CoM - ZMP)
        # We get: ZMP = CoM - (1/ω²) * ω² * (CoM - ZMP) -> This is circular
        # So we use: ZMP = CoM - (h/g) * CoM_acceleration

        # For control purposes, we often want to specify ZMP and find CoM trajectory
        # But for analysis, we calculate ZMP from CoM
        pass

    def compute_com_trajectory(self, zmp_trajectory, initial_com_pos, initial_com_vel):
        """
        Compute CoM trajectory from ZMP trajectory using LIPM.

        Args:
            zmp_trajectory: List of ZMP positions over time
            initial_com_pos: Initial CoM position
            initial_com_vel: Initial CoM velocity

        Returns:
            com_trajectory: Computed CoM trajectory
        """
        com_trajectory = []
        current_com_pos = np.array(initial_com_pos)
        current_com_vel = np.array(initial_com_vel)

        dt = 0.01  # 100 Hz control

        for zmp_point in zmp_trajectory:
            # LIPM equation: ẍ_com = ω² * (x_com - x_zmp)
            com_acc = self.omega**2 * (current_com_pos - zmp_point)

            # Integrate to get new CoM state
            new_com_vel = current_com_vel + com_acc * dt
            new_com_pos = current_com_pos + new_com_vel * dt

            com_trajectory.append({
                'time': len(com_trajectory) * dt,
                'position': new_com_pos,
                'velocity': new_com_vel,
                'acceleration': com_acc
            })

            # Update for next iteration
            current_com_pos = new_com_pos
            current_com_vel = new_com_vel

        return com_trajectory

    def compute_zmp_from_com(self, com_pos, com_acc):
        """
        Compute ZMP from CoM position and acceleration.
        """
        zmp_x = com_pos[0] - (self.com_height / self.gravity) * com_acc[0]
        zmp_y = com_pos[1] - (self.com_height / self.gravity) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def plan_step_timing(self, step_length, step_width, step_height, step_duration):
        """
        Plan timing for a single step using LIPM.
        """
        # Calculate step trajectory parameters
        n_points = int(step_duration / 0.01)  # Points at 100 Hz
        dt = step_duration / n_points

        # Generate swing foot trajectory
        swing_trajectory = []
        for i in range(n_points + 1):
            t = i / n_points  # Normalized time (0 to 1)

            # Horizontal movement (cubic interpolation for smooth motion)
            horizontal_progress = 3*t**2 - 2*t**3  # Smooth interpolation
            x_pos = step_length * horizontal_progress
            y_pos = step_width * math.sin(math.pi * t)  # Sinusoidal lateral movement

            # Vertical movement (elliptical arc for foot lift)
            if 0.2 < t < 0.8:  # Lift foot during middle portion
                lift_phase = (t - 0.2) / 0.6  # Normalize to 0-1 for lift phase
                z_pos = step_height * math.sin(math.pi * lift_phase)
            else:
                z_pos = 0.0  # Keep foot on ground at start/end

            swing_trajectory.append({
                'time': i * dt,
                'position': np.array([x_pos, y_pos, z_pos]),
                'velocity': self.calculate_foot_velocity(swing_trajectory, i, dt) if i > 0 else np.zeros(3),
                'acceleration': self.calculate_foot_acceleration(swing_trajectory, i, dt) if i > 1 else np.zeros(3)
            })

        return swing_trajectory

    def calculate_foot_velocity(self, trajectory, index, dt):
        """Calculate foot velocity from position trajectory."""
        if index == 0 or len(trajectory) < 2:
            return np.zeros(3)

        pos_current = trajectory[index]['position']
        pos_previous = trajectory[index-1]['position']

        velocity = (pos_current - pos_previous) / dt
        return velocity

    def calculate_foot_acceleration(self, trajectory, index, dt):
        """Calculate foot acceleration from velocity trajectory."""
        if index < 2 or len(trajectory) < 3:
            return np.zeros(3)

        vel_current = trajectory[index]['velocity']
        vel_previous = trajectory[index-1]['velocity']

        acceleration = (vel_current - vel_previous) / dt
        return acceleration
```

## Walking Pattern Generation

### Footstep Planning and Timing

```python
class FootstepPlanner:
    def __init__(self):
        self.step_length = 0.30  # meters
        self.step_width = 0.20   # meters (distance between feet)
        self.step_height = 0.05  # meters (foot lift height)
        self.step_duration = 0.8  # seconds per step
        self.double_support_ratio = 0.2  # 20% of step in double support

        # Walking parameters
        self.nominal_com_height = 0.85
        self.walk_speed = 0.5  # m/s
        self.turn_rate = 0.2   # rad/s

    def plan_footsteps(self, start_pos, goal_pos, start_yaw=0.0):
        """
        Plan footstep sequence from start to goal position.

        Args:
            start_pos: [x, y] starting position
            goal_pos: [x, y] goal position
            start_yaw: Initial orientation

        Returns:
            footsteps: List of footstep dictionaries
        """
        # Calculate distance and direction to goal
        dx = goal_pos[0] - start_pos[0]
        dy = goal_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        goal_yaw = math.atan2(dy, dx)

        # Calculate number of steps needed
        n_steps = max(1, int(distance / self.step_length))

        # Generate footsteps
        footsteps = []
        current_pos = np.array(start_pos)
        current_yaw = start_yaw

        # Start with left foot support (typical for humanoid robots)
        support_foot = 'right'  # Robot will step with left first

        for i in range(n_steps):
            # Determine swing foot
            swing_foot = 'left' if support_foot == 'right' else 'right'

            # Calculate step direction and position
            step_direction = current_yaw + (goal_yaw - current_yaw) * (i / n_steps)
            step_distance = self.step_length

            # Calculate step position
            step_x = current_pos[0] + step_distance * math.cos(step_direction)
            step_y = current_pos[1] + step_distance * math.sin(step_direction)

            # Add lateral offset based on support foot
            lateral_offset = self.step_width / 2
            if swing_foot == 'left':
                step_y += lateral_offset
            else:
                step_y -= lateral_offset

            # Create footstep
            footstep = {
                'step_number': i,
                'foot': swing_foot,
                'position': np.array([step_x, step_y, 0.0]),
                'orientation': step_direction,
                'timing': {
                    'lift_time': i * self.step_duration,
                    'touchdown_time': (i + 1) * self.step_duration,
                    'support_switch_time': (i + 0.5) * self.step_duration
                },
                'support_foot': support_foot
            }

            footsteps.append(footstep)

            # Update current position and support foot
            current_pos = np.array([step_x, step_y])
            support_foot = swing_foot  # Switch support foot

        return footsteps

    def generate_com_trajectory_for_walking(self, footsteps, com_height=None):
        """
        Generate CoM trajectory for a sequence of footsteps using Capture Point method.
        """
        if com_height is None:
            com_height = self.nominal_com_height

        omega = math.sqrt(9.81 / com_height)
        com_trajectory = []

        # Start from initial position (typically between feet)
        initial_com_x = (footsteps[0]['position'][0] + footsteps[1]['position'][0]) / 2 if len(footsteps) > 1 else footsteps[0]['position'][0]
        initial_com_y = (footsteps[0]['position'][1] + footsteps[1]['position'][1]) / 2 if len(footsteps) > 1 else footsteps[0]['position'][1]

        current_com = np.array([initial_com_x, initial_com_y, com_height])
        current_com_vel = np.zeros(3)

        dt = 0.01  # 100 Hz

        for i, footstep in enumerate(footsteps):
            # Determine support polygon for this step
            if i == 0:
                # First step - use initial support
                support_center = np.array([initial_com_x, initial_com_y, 0.0])
            else:
                # Use previous step as support
                prev_footstep = footsteps[i-1]
                support_center = np.array([prev_footstep['position'][0], prev_footstep['position'][1], 0.0])

            # Calculate target capture point (where robot should step to come to rest)
            target_capture_point = footstep['position']

            # Generate trajectory segment to move CoM toward capture point
            n_points_in_step = int(self.step_duration / dt)

            for j in range(n_points_in_step):
                t = j / n_points_in_step  # Progress through step (0 to 1)

                # Calculate desired CoM position using exponentially converging trajectory
                # towards capture point
                time_into_step = j * dt
                exp_factor = math.exp(-omega * time_into_step)

                # Desired CoM position gradually shifts toward capture point
                desired_com_x = (1 - exp_factor) * target_capture_point[0] + exp_factor * current_com[0]
                desired_com_y = (1 - exp_factor) * target_capture_point[1] + exp_factor * current_com[1]

                # Calculate required CoM acceleration to follow this trajectory
                desired_com_acc_x = omega**2 * (desired_com_x - current_com[0]) + 2*omega * (current_com_vel[0])
                desired_com_acc_y = omega**2 * (desired_com_y - current_com[1]) + 2*omega * (current_com_vel[1])

                # Update CoM state
                com_acc = np.array([desired_com_acc_x, desired_com_acc_y, 0.0])
                current_com_vel += com_acc * dt
                current_com += current_com_vel * dt

                # Add small vertical oscillation for natural movement
                vertical_oscillation = 0.01 * math.sin(2 * math.pi * 2 * (i * self.step_duration + time_into_step))
                current_com[2] = com_height + vertical_oscillation

                com_trajectory.append({
                    'time': i * self.step_duration + time_into_step,
                    'position': current_com.copy(),
                    'velocity': current_com_vel.copy(),
                    'acceleration': com_acc,
                    'support_foot': footstep['support_foot'],
                    'current_footstep': i
                })

        return com_trajectory

    def plan_ankle_trajectories(self, footstep_sequence, com_trajectory):
        """
        Plan ankle joint trajectories to achieve desired foot placements
        while maintaining CoM stability.
        """
        ankle_trajectories = {'left': [], 'right': []}

        for i, (footstep, com_state) in enumerate(zip(footstep_sequence, com_trajectory)):
            # Calculate required ankle positions to place foot at desired location
            # while keeping CoM stable

            foot_position = footstep['position']
            com_position = com_state['position']

            # Calculate ankle position that achieves foot placement
            # while considering CoM balance requirements
            ankle_position = self.calculate_ankle_pose_for_foot_placement(
                foot_position, com_position, footstep['foot']
            )

            ankle_trajectories[footstep['foot']].append({
                'time': footstep['timing']['lift_time'],
                'position': ankle_position,
                'co_state': com_state
            })

        return ankle_trajectories

    def calculate_ankle_pose_for_foot_placement(self, desired_foot_pos, com_pos, foot_side):
        """
        Calculate required ankle pose to achieve desired foot placement
        while considering CoM balance.
        """
        # This would involve inverse kinematics and balance optimization
        # For this example, we'll return a simplified calculation
        # In practice, this would use full kinematic chains and optimization

        # Calculate offset from CoM to foot considering balance
        com_to_foot = desired_foot_pos - com_pos[:2]

        # Calculate required ankle joint angles (simplified)
        # In reality, this would involve full IK solution
        if foot_side == 'left':
            # Left foot - may need different offset for balance
            ankle_offset = np.array([0.0, 0.1, -0.8])  # Simplified offset
        else:
            # Right foot
            ankle_offset = np.array([0.0, -0.1, -0.8])  # Simplified offset

        # Calculate ankle position in world frame
        ankle_world_pos = desired_foot_pos + ankle_offset

        return ankle_world_pos
```

## Whole-Body Control

### Operational Space Control for Humanoids

```python
class OperationalSpaceController:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.n_dofs = robot_model.get_num_joints()

        # Task priorities and weights
        self.task_hierarchy = []
        self.task_weights = {}

    def add_task(self, task_name, task_jacobian, task_desired, priority=0, weight=1.0):
        """
        Add a control task to the operational space controller.

        Args:
            task_name: Name of the task
            task_jacobian: Jacobian matrix for the task (6xN for pose tasks, 3xN for position)
            task_desired: Desired task-space velocity/acceleration
            priority: Priority level (0 = highest)
            weight: Task importance weight
        """
        task = {
            'name': task_name,
            'jacobian': task_jacobian,
            'desired': task_desired,
            'priority': priority,
            'weight': weight,
            'dimension': task_jacobian.shape[0]  # Task space dimension
        }

        self.task_hierarchy.append(task)
        self.task_hierarchy.sort(key=lambda x: x['priority'])

    def compute_operational_space_control(self, q, qdot, task_errors=None):
        """
        Compute operational space control torques using task prioritization.

        Args:
            q: Current joint positions
            qdot: Current joint velocities
            task_errors: Optional precomputed task errors

        Returns:
            joint_torques: Computed joint space torques
        """
        # Initialize total torque
        tau_total = np.zeros(self.n_dofs)

        # Mass matrix
        M = self.robot.get_mass_matrix(q)

        # Coriolis and gravity terms
        C = self.robot.get_coriolis_matrix(q, qdot)
        G = self.robot.get_gravity_vector(q)

        # Initialize nullspace projector
        I = np.eye(self.n_dofs)

        for task in self.task_hierarchy:
            J_task = task['jacobian']
            task_desired = task['desired']
            weight = task['weight']

            # Calculate operational space inertia matrix
            # Λ = (J * M⁻¹ * Jᵀ)⁻¹
            M_inv = np.linalg.inv(M)
            Lambda_inv = J_task @ M_inv @ J_task.T
            try:
                Lambda = np.linalg.inv(Lambda_inv)
            except np.linalg.LinAlgError:
                # Use pseudo-inverse for singular cases
                Lambda = np.linalg.pinv(Lambda_inv, rcond=1e-8)

            # Calculate operational space Coriolis and gravity terms
            # μ = Λ * J * M⁻¹ * (C*qdot - Jᵀ*λ_task)
            # η = Λ * J * M⁻¹ * G
            temp = J_task @ M_inv
            mu = Lambda @ temp @ (C @ qdot)
            eta = Lambda @ temp @ G

            # Calculate task-space error correction
            if task_errors is not None and task['name'] in task_errors:
                task_error = task_errors[task['name']]
                # PD control in task space
                Kp = 100.0  # Proportional gain
                Kd = 20.0   # Derivative gain
                task_correction = Kp * task_error[:task['dimension']] + Kd * task_error[task['dimension']:]
                task_desired += task_correction

            # Calculate task-space acceleration command
            # α_task = Λ * (ẍ_d - μ - η) + J * M⁻¹ * (τ_ext)
            alpha_task = Lambda @ (task_desired - mu - eta)

            # Calculate joint space torques for this task
            # τ_task = M * Jᵀ * Λ * (ẍ_d - μ - η) + Jᵀ * λ
            tau_task = J_task.T @ Lambda @ (task_desired - mu - eta) + J_task.T @ (Lambda @ mu + eta)

            # Apply task weighting
            tau_task = weight * tau_task

            # Add to total torque
            tau_total += tau_task

            # Update nullspace projector for next task
            # P = I - J⁺ * J where J⁺ = M⁻¹ * Jᵀ * Λ
            J_pseudo_inv = M_inv @ J_task.T @ Lambda
            I = I - J_pseudo_inv @ J_task

            # Project mass matrix to nullspace
            M = I.T @ M @ I

        return tau_total

    def balance_control_task(self, com_pos, com_vel, com_acc_desired):
        """
        Create balance control task in operational space.
        """
        # Calculate CoM Jacobian
        J_com = self.robot.get_com_jacobian()

        # Calculate desired CoM acceleration for balance
        # Using inverted pendulum model: ẍ_com = ω² * (x_com - x_zmp)
        zmp_desired = self.calculate_desired_zmp(com_pos, com_vel)
        com_acc_balance = self.omega**2 * (com_pos[:2] - zmp_desired)

        # Combine with desired acceleration
        com_acc_total = com_acc_desired[:2] + com_acc_balance

        return J_com[:2, :], np.concatenate([com_acc_total, np.zeros(4)])  # 6D task (only x,y for CoM)

    def posture_control_task(self, q_current, q_desired, Kp=50.0, Kd=10.0):
        """
        Create posture control task to maintain desired joint configuration.
        """
        # Posture control operates in joint space
        # We can treat this as a task with identity Jacobian
        J_posture = np.eye(self.n_dofs)

        # Calculate desired joint accelerations
        pos_error = q_desired - q_current
        vel_error = -self.robot.get_joint_velocities()  # Assuming current velocity should be reduced

        qdd_desired = Kp * pos_error + Kd * vel_error

        return J_posture, qdd_desired

    def end_effector_control_task(self, ee_name, target_pose, target_twist, target_accel):
        """
        Create end-effector control task.
        """
        # Get end-effector Jacobian
        J_ee = self.robot.get_jacobian(ee_name)

        # Combine pose, velocity, and acceleration commands
        task_desired = np.concatenate([
            target_accel[:3],  # Linear acceleration
            target_accel[3:]   # Angular acceleration
        ])

        return J_ee, task_desired
```

## Advanced Control Techniques

### Model Predictive Control (MPC) for Walking

```python
from scipy.optimize import minimize
import casadi as ca

class MPCWalkingController:
    def __init__(self, horizon=10, dt=0.1):
        self.horizon = horizon  # Prediction horizon
        self.dt = dt           # Time step
        self.com_height = 0.8
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Cost function weights
        self.weight_com_tracking = 1.0
        self.weight_zmp_stability = 10.0
        self.weight_control_effort = 0.1
        self.weight_terminal = 5.0

    def setup_mpc_problem(self):
        """
        Set up the MPC optimization problem using CasADi.
        """
        # Define symbolic variables
        N = self.horizon

        # State variables (CoM position and velocity)
        X = ca.MX.sym('X', 4, N+1)  # [x, y, ẋ, ẏ] for each time step

        # Control variables (ZMP positions)
        U = ca.MX.sym('U', 2, N)    # [zmp_x, zmp_y] for each control step

        # Parameters (reference trajectories, initial state)
        X_ref = ca.MX.sym('X_ref', 4, N+1)
        X_init = ca.MX.sym('X_init', 4)

        # Dynamics constraints (LIPM dynamics)
        # ẍ_com = ω² * (x_com - x_zmp)
        # ÿ_com = ω² * (y_com - y_zmp)
        constraints = []

        for k in range(N):
            # Dynamics: x(k+1) = A*x(k) + B*u(k) + c
            # For LIPM: ẍ = ω²(x - zmp), ẏ = vy, ẋ = vx
            # Linearized discrete-time dynamics

            # Simplified discrete dynamics
            x_next = X[0, k] + X[2, k] * self.dt + 0.5 * (self.omega**2 * (X[0, k] - U[0, k])) * self.dt**2
            y_next = X[1, k] + X[3, k] * self.dt + 0.5 * (self.omega**2 * (X[1, k] - U[1, k])) * self.dt**2
            vx_next = X[2, k] + self.omega**2 * (X[0, k] - U[0, k]) * self.dt
            vy_next = X[3, k] + self.omega**2 * (X[1, k] - U[1, k]) * self.dt

            # Add dynamics constraints
            constraints.append(X[0, k+1] - x_next)
            constraints.append(X[1, k+1] - y_next)
            constraints.append(X[2, k+1] - vx_next)
            constraints.append(X[3, k+1] - vy_next)

        # Initial state constraint
        constraints.append(X[:, 0] - X_init)

        # Cost function
        cost = 0

        # Tracking cost
        for k in range(N+1):
            pos_error = X[:2, k] - X_ref[:2, k]
            vel_error = X[2:, k] - X_ref[2:, k]
            cost += self.weight_com_tracking * ca.dot(pos_error, pos_error)
            cost += 0.1 * self.weight_com_tracking * ca.dot(vel_error, vel_error)

        # Control effort cost
        for k in range(N):
            cost += self.weight_control_effort * ca.dot(U[:, k], U[:, k])

        # Terminal cost
        terminal_pos_error = X[:2, N] - X_ref[:2, N]
        cost += self.weight_terminal * ca.dot(terminal_pos_error, terminal_pos_error)

        # Support polygon constraints (simplified)
        # In practice, these would be more complex
        for k in range(N):
            # Add constraints to keep ZMP within support polygon
            # This would depend on footstep plan
            pass

        # Create NLP
        nlp = {
            'x': ca.vertcat(ca.vec(X), ca.vec(U)),
            'f': cost,
            'g': ca.vertcat(*constraints),
            'p': ca.vertcat(ca.vec(X_ref), X_init)
        }

        # Solve using IPOPT
        opts = {
            'ipopt.print_level': 0,
            'print_time': 0,
            'ipopt.sb': 'yes'
        }

        self.solver = ca.nlpsol('solver', 'ipopt', nlp, opts)

    def solve_mpc(self, current_state, reference_trajectory):
        """
        Solve the MPC problem for current state and reference.

        Args:
            current_state: Current CoM state [x, y, ẋ, ẏ]
            reference_trajectory: Reference trajectory over horizon

        Returns:
            optimal_control_sequence: Sequence of optimal ZMP commands
        """
        # Set up optimization problem
        lbx = []  # Lower bounds on variables
        ubx = []  # Upper bounds on variables
        lbg = []  # Lower bounds on constraints
        ubg = []  # Upper bounds on constraints

        # Initialize variables
        x_init = ca.vertcat(
            ca.reshape(reference_trajectory, -1),  # Initial guess for states
            ca.reshape(np.zeros((2, self.horizon)), -1)  # Initial guess for controls
        )

        # Set parameters
        p = ca.vertcat(
            ca.reshape(reference_trajectory, -1),
            current_state
        )

        # Solve
        sol = self.solver(
            x0=x_init,
            lbx=lbx, ubx=ubx,
            lbg=lbg, ubg=ubg,
            p=p
        )

        # Extract solution
        solution = sol['x'].full().flatten()

        # Reshape to get control sequence
        u_solution = solution[-2*self.horizon:].reshape(2, self.horizon)

        return u_solution[:, 0]  # Return first control action

    def update_reference_trajectory(self, footstep_plan, current_time):
        """
        Update reference trajectory based on footstep plan.
        """
        reference = np.zeros((4, self.horizon + 1))  # [x, y, ẋ, ẏ, ẍ, ÿ]

        for k in range(self.horizon + 1):
            t = current_time + k * self.dt

            # Calculate reference CoM position based on footstep plan
            # This would interpolate between capture points
            ref_pos = self.interpolate_reference_com(footstep_plan, t)

            # Calculate reference velocity and acceleration
            ref_vel = self.calculate_reference_velocity(footstep_plan, t)
            ref_acc = self.calculate_reference_acceleration(footstep_plan, t)

            reference[:, k] = np.concatenate([ref_pos, ref_vel])

        return reference

    def interpolate_reference_com(self, footstep_plan, time):
        """
        Interpolate reference CoM position based on footstep plan.
        """
        # Find current and next support phases
        current_support = None
        next_support = None

        for i, step in enumerate(footstep_plan):
            if step['timing']['lift_time'] <= time < step['timing']['touchdown_time']:
                current_support = step
            elif time < step['timing']['lift_time']:
                next_support = step
                break

        if current_support is None:
            # Use last step as reference
            current_support = footstep_plan[-1]

        if next_support is None:
            # Use current support location
            return current_support['position'][:2]

        # Interpolate between current and next support
        phase_time = time - current_support['timing']['lift_time']
        step_duration = current_support['timing']['touchdown_time'] - current_support['timing']['lift_time']

        if step_duration > 0:
            progress = min(1.0, phase_time / step_duration)
        else:
            progress = 1.0

        # Smooth interpolation using quintic polynomial
        smooth_progress = 6*progress**5 - 15*progress**4 + 10*progress**3

        ref_x = ((1 - smooth_progress) * current_support['position'][0] +
                smooth_progress * next_support['position'][0])
        ref_y = ((1 - smooth_progress) * current_support['position'][1] +
                smooth_progress * next_support['position'][1])

        return np.array([ref_x, ref_y])
```

### Adaptive Control for Humanoid Robots

```python
class AdaptiveController:
    def __init__(self, initial_params=None):
        if initial_params is None:
            initial_params = {
                'mass': 50.0,  # Robot mass in kg
                'com_height': 0.8,  # Initial CoM height
                'inertia_xx': 5.0,  # Initial inertia estimates
                'inertia_yy': 5.0,
                'inertia_zz': 10.0
            }

        self.params = initial_params
        self.param_updates = {key: 0.0 for key in initial_params.keys()}

        # Adaptation gains
        self.gamma_mass = 0.01
        self.gamma_inertia = 0.001
        self.gamma_com_height = 0.005

        # Parameter bounds
        self.bounds = {
            'mass': (10.0, 100.0),
            'com_height': (0.5, 1.5),
            'inertia_xx': (1.0, 20.0),
            'inertia_yy': (1.0, 20.0),
            'inertia_zz': (2.0, 40.0)
        }

    def update_model_parameters(self, prediction_error, current_state, control_input):
        """
        Update internal model parameters based on prediction error.

        Args:
            prediction_error: Difference between predicted and actual behavior
            current_state: Current robot state
            control_input: Applied control input
        """
        # Calculate parameter sensitivities (regressor matrix)
        phi = self.calculate_regressor(current_state, control_input)

        # Parameter update law (gradient descent)
        # θ̇ = -γ * φ * e where γ is adaptation gain, φ is regressor, e is error
        for param_name, current_value in self.params.items():
            # Get corresponding regressor element
            if param_name in ['mass', 'com_height']:
                idx = 0 if param_name == 'mass' else 1  # Simplified indexing
                sensitivity = phi[idx] if idx < len(phi) else 0.0
            else:
                # Inertia parameters
                idx = 2 + list(self.bounds.keys()).index(param_name) - 2  # Adjust for non-mass params
                sensitivity = phi[idx] if idx < len(phi) else 0.0

            # Calculate parameter update
            param_update = -self.get_adaptation_gain(param_name) * sensitivity * prediction_error

            # Update parameter estimate
            new_value = current_value + param_update * 0.01  # Small time step

            # Apply bounds
            bounded_value = np.clip(new_value, self.bounds[param_name][0], self.bounds[param_name][1])

            self.params[param_name] = bounded_value
            self.param_updates[param_name] = param_update

    def calculate_regressor(self, state, control):
        """
        Calculate regressor matrix for parameter identification.
        This is a simplified example - real implementation would be more complex.
        """
        # The regressor relates parameter errors to prediction errors
        # φᵀ * θ = system_output where φ is regressor, θ is parameters

        # Simplified regressor based on dynamic equations
        com_pos = state['com_position']
        com_vel = state['com_velocity']
        com_acc = state['com_acceleration']
        joint_pos = state['joint_positions']
        joint_vel = state['joint_velocities']
        joint_acc = state['joint_accelerations']
        torques = control['joint_torques']

        # Example regressor elements (these would be derived from actual dynamics)
        regressor_elements = [
            # Mass-related terms
            np.sum(com_acc),  # Effect of mass on CoM acceleration

            # Inertia-related terms
            np.sum(joint_acc),  # Effect of inertia on joint acceleration

            # Gravity-related terms
            9.81,  # Constant gravity term

            # Centrifugal/Coriolis terms
            np.sum(joint_vel**2),  # Velocity squared terms

            # External force terms
            np.sum(torques)  # Effect of applied torques
        ]

        return np.array(regressor_elements)

    def get_adaptation_gain(self, param_name):
        """Get appropriate adaptation gain for parameter."""
        gains = {
            'mass': self.gamma_mass,
            'com_height': self.gamma_com_height,
            'inertia_xx': self.gamma_inertia,
            'inertia_yy': self.gamma_inertia,
            'inertia_zz': self.gamma_inertia
        }
        return gains.get(param_name, 0.001)

    def calculate_prediction_error(self, predicted_state, actual_state):
        """
        Calculate prediction error between model prediction and actual measurement.
        """
        # Calculate error in different state components
        pos_error = actual_state['position'] - predicted_state['position']
        vel_error = actual_state['velocity'] - predicted_state['velocity']
        acc_error = actual_state['acceleration'] - predicted_state['acceleration']

        # Weighted combination of errors
        error = (0.5 * np.sum(pos_error**2) +
                0.3 * np.sum(vel_error**2) +
                0.2 * np.sum(acc_error**2))

        return error

    def update_control_with_adaptation(self, nominal_control, state_estimate, prediction_error):
        """
        Update control input based on parameter adaptation.

        Args:
            nominal_control: Original control input
            state_estimate: Current state estimate
            prediction_error: Current prediction error

        Returns:
            adapted_control: Control input with adaptation correction
        """
        # Calculate adaptation-based correction
        adaptation_correction = self.calculate_adaptation_correction(
            state_estimate, prediction_error
        )

        # Apply correction to nominal control
        adapted_control = nominal_control + adaptation_correction

        return adapted_control

    def calculate_adaptation_correction(self, state, error):
        """
        Calculate control correction based on model parameter errors.
        """
        # Use current parameter estimates to calculate correction
        # This would involve recomputing control gains or feedforward terms
        # based on updated model parameters

        correction = np.zeros_like(state['joint_torques'])

        # Example: Adjust gravity compensation based on updated mass
        mass_correction = (self.params['mass'] - self.initial_params['mass']) * 9.81
        correction += mass_correction * np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1])  # Apply to relevant joints

        # Example: Adjust Coriolis compensation based on updated inertias
        inertia_factor = (self.params['inertia_xx'] + self.params['inertia_yy']) / 2.0
        coriolis_correction = inertia_factor * state['joint_velocities'] * 0.1  # Simplified
        correction += coriolis_correction

        return correction
```

## Safety and Fault Tolerance

### Emergency Stop and Recovery Systems

```python
class SafetyController:
    def __init__(self):
        self.emergency_stop_active = False
        self.fall_detected = False
        self.safety_thresholds = {
            'tilt_angle': 30.0,  # degrees
            'zmp_deviation': 0.1,  # meters from support polygon
            'joint_limit_violation': 0.01,  # radians
            'torque_limit': 100.0,  # Nm
            'velocity_limit': 5.0   # rad/s
        }

        self.fall_recovery_active = False
        self.recovery_state = 'standing'  # 'standing', 'crouching', 'recovering'

    def check_safety_conditions(self, robot_state):
        """
        Check all safety conditions and trigger emergency responses if needed.

        Args:
            robot_state: Current robot state dictionary

        Returns:
            safety_ok: Boolean indicating if robot is in safe state
        """
        safety_violations = []

        # Check tilt angle
        tilt_angle = self.calculate_tilt_angle(robot_state)
        if abs(tilt_angle) > self.safety_thresholds['tilt_angle']:
            safety_violations.append({
                'type': 'tilt_violation',
                'value': tilt_angle,
                'threshold': self.safety_thresholds['tilt_angle'],
                'severity': 'critical'
            })

        # Check ZMP stability
        zmp_pos = self.calculate_zmp(robot_state['com_position'], robot_state['com_acceleration'])
        support_polygon = self.get_support_polygon(robot_state)
        if not self.is_point_in_polygon(zmp_pos, support_polygon):
            zmp_deviation = self.calculate_zmp_deviation(zmp_pos, support_polygon)
            if zmp_deviation > self.safety_thresholds['zmp_deviation']:
                safety_violations.append({
                    'type': 'zmp_violation',
                    'value': zmp_deviation,
                    'threshold': self.safety_thresholds['zmp_deviation'],
                    'severity': 'critical'
                })

        # Check joint limits
        joint_positions = robot_state['joint_positions']
        joint_limits = self.get_joint_limits()
        for i, (pos, (lower, upper)) in enumerate(zip(joint_positions, joint_limits)):
            if pos < lower - self.safety_thresholds['joint_limit_violation'] or \
               pos > upper + self.safety_thresholds['joint_limit_violation']:
                safety_violations.append({
                    'type': 'joint_limit_violation',
                    'joint_index': i,
                    'value': pos,
                    'threshold': (lower, upper),
                    'severity': 'warning'
                })

        # Check torque limits
        joint_torques = robot_state.get('joint_torques', [])
        for i, torque in enumerate(joint_torques):
            if abs(torque) > self.safety_thresholds['torque_limit']:
                safety_violations.append({
                    'type': 'torque_limit_violation',
                    'joint_index': i,
                    'value': torque,
                    'threshold': self.safety_thresholds['torque_limit'],
                    'severity': 'critical'
                })

        # Check velocity limits
        joint_velocities = robot_state['joint_velocities']
        for i, vel in enumerate(joint_velocities):
            if abs(vel) > self.safety_thresholds['velocity_limit']:
                safety_violations.append({
                    'type': 'velocity_limit_violation',
                    'joint_index': i,
                    'value': vel,
                    'threshold': self.safety_thresholds['velocity_limit'],
                    'severity': 'warning'
                })

        # Process violations
        critical_violations = [v for v in safety_violations if v['severity'] == 'critical']
        if critical_violations:
            self.trigger_emergency_stop()
            return False

        return len(safety_violations) == 0

    def trigger_emergency_stop(self):
        """Activate emergency stop procedures."""
        self.emergency_stop_active = True
        self.fall_detected = True

        # Immediately stop all joint torques
        self.apply_zero_torques()

        # Activate fall protection mechanisms
        self.activate_fall_protection()

        print("EMERGENCY STOP ACTIVATED: Critical safety violation detected")

    def activate_fall_protection(self):
        """Activate fall protection mechanisms."""
        # Move to protective crouch position
        protective_joints = self.calculate_protective_posture()

        # Apply joint torques to move to protective position
        self.move_to_protective_posture(protective_joints)

        # Prepare for potential impact
        self.prepare_for_impact()

    def calculate_protective_posture(self):
        """Calculate protective joint configuration for fall prevention."""
        # Move arms to protect head and torso
        # Bend knees to absorb impact
        # Keep CoM low

        protective_angles = np.zeros(self.n_joints)

        # Protect head with arms
        protective_angles[self.left_shoulder_indices] = [0.5, 0.5, 0.0]  # Raise left arm
        protective_angles[self.right_shoulder_indices] = [0.5, -0.5, 0.0]  # Raise right arm

        # Crouch position
        protective_angles[self.left_hip_indices] = [-0.3, 0.0, 0.0]   # Flex hips
        protective_angles[self.right_hip_indices] = [-0.3, 0.0, 0.0]
        protective_angles[self.left_knee_indices] = [0.6, 0.0, 0.0]   # Bend knees
        protective_angles[self.right_knee_indices] = [0.6, 0.0, 0.0]

        # Stabilize ankles
        protective_angles[self.left_ankle_indices] = [0.0, 0.0, 0.0]  # Keep feet flat
        protective_angles[self.right_ankle_indices] = [0.0, 0.0, 0.0]

        return protective_angles

    def activate_fall_recovery(self):
        """
        Activate fall recovery procedure after impact detection.
        """
        if not self.fall_detected:
            return

        self.fall_recovery_active = True
        self.recovery_state = 'crouching'

        # First, stabilize in crouched position
        crouch_angles = self.calculate_stable_crouch()
        self.move_to_configuration(crouch_angles, duration=1.0)

        # Then, attempt to stand up
        self.recovery_state = 'standing'
        stand_angles = self.calculate_stand_posture()
        self.move_to_configuration(stand_angles, duration=3.0)

        # Finally, return to normal walking posture
        self.recovery_state = 'standing'
        self.fall_recovery_active = False
        self.fall_detected = False

        print("Fall recovery completed successfully")

    def calculate_fall_recovery_sequence(self):
        """
        Calculate complete fall recovery sequence.
        """
        recovery_sequence = []

        # Phase 1: Protective crouch
        crouch_config = self.calculate_protective_posture()
        recovery_sequence.append({
            'phase': 'crouch',
            'target_configuration': crouch_config,
            'duration': 0.5,
            'priority': 1
        })

        # Phase 2: Impact stabilization
        impact_config = self.calculate_impact_stabilization()
        recovery_sequence.append({
            'phase': 'stabilize',
            'target_configuration': impact_config,
            'duration': 1.0,
            'priority': 2
        })

        # Phase 3: Recovery movement
        recovery_config = self.calculate_recovery_movement()
        recovery_sequence.append({
            'phase': 'recover',
            'target_configuration': recovery_config,
            'duration': 2.0,
            'priority': 3
        })

        # Phase 4: Stand up
        stand_config = self.calculate_stand_posture()
        recovery_sequence.append({
            'phase': 'stand',
            'target_configuration': stand_config,
            'duration': 3.0,
            'priority': 4
        })

        return recovery_sequence

    def calculate_impact_stabilization(self):
        """
        Calculate configuration to stabilize after impact.
        """
        # Distribute weight evenly
        # Prepare for potential sliding
        # Maintain low CoM
        stabilization_angles = np.zeros(self.n_joints)

        # Even weight distribution
        stabilization_angles[self.left_hip_indices] = [-0.2, 0.0, 0.0]
        stabilization_angles[self.right_hip_indices] = [-0.2, 0.0, 0.0]
        stabilization_angles[self.left_knee_indices] = [0.4, 0.0, 0.0]
        stabilization_angles[self.right_knee_indices] = [0.4, 0.0, 0.0]

        # Arm positioning for stability
        stabilization_angles[self.left_shoulder_indices] = [0.2, 0.2, 0.0]
        stabilization_angles[self.right_shoulder_indices] = [0.2, -0.2, 0.0]

        return stabilization_angles

    def calculate_recovery_movement(self):
        """
        Calculate movement to recover from fall position.
        """
        # Gradually shift weight to feet
        # Raise torso
        # Prepare for standing
        recovery_angles = np.zeros(self.n_joints)

        # Begin weight transfer
        recovery_angles[self.left_hip_indices] = [-0.1, 0.0, 0.0]
        recovery_angles[self.right_hip_indices] = [-0.1, 0.0, 0.0]
        recovery_angles[self.left_knee_indices] = [0.2, 0.0, 0.0]
        recovery_angles[self.right_knee_indices] = [0.2, 0.0, 0.0]

        # Begin raising torso
        recovery_angles[self.torso_indices] = [0.1, 0.0, 0.0]

        # Position arms for balance
        recovery_angles[self.left_arm_indices] = [0.3, 0.3, 0.0, 0.5, 0.0, 0.0]
        recovery_angles[self.right_arm_indices] = [0.3, -0.3, 0.0, 0.5, 0.0, 0.0]

        return recovery_angles

    def calculate_stand_posture(self):
        """
        Calculate normal standing posture after recovery.
        """
        # Return to neutral standing position
        stand_angles = np.zeros(self.n_joints)

        # Neutral standing
        stand_angles[self.left_hip_indices] = [0.0, 0.0, 0.0]
        stand_angles[self.right_hip_indices] = [0.0, 0.0, 0.0]
        stand_angles[self.left_knee_indices] = [0.0, 0.0, 0.0]
        stand_angles[self.right_knee_indices] = [0.0, 0.0, 0.0]
        stand_angles[self.left_ankle_indices] = [0.0, 0.0, 0.0]
        stand_angles[self.right_ankle_indices] = [0.0, 0.0, 0.0]

        # Neutral arm position
        stand_angles[self.left_arm_indices] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        stand_angles[self.right_arm_indices] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Straight torso
        stand_angles[self.torso_indices] = [0.0, 0.0, 0.0]

        return stand_angles

    def monitor_joint_health(self):
        """
        Monitor joint health and detect potential failures.
        """
        joint_health_status = {}

        for joint_idx in range(self.n_joints):
            # Check joint temperature (if available)
            temperature = self.get_joint_temperature(joint_idx)
            if temperature > 80:  # Overheating threshold
                joint_health_status[joint_idx] = 'overheating'

            # Check joint encoder status
            encoder_status = self.get_encoder_status(joint_idx)
            if not encoder_status:
                joint_health_status[joint_idx] = 'encoder_failure'

            # Check motor current
            current = self.get_motor_current(joint_idx)
            if abs(current) > self.max_motor_current:
                joint_health_status[joint_idx] = 'overcurrent'

        return joint_health_status

    def handle_joint_failure(self, failed_joint_idx):
        """
        Handle joint failure by reconfiguring control.
        """
        # Remove failed joint from control
        self.disabled_joints.append(failed_joint_idx)

        # Reconfigure control to compensate for missing DOF
        self.reconfigure_control_for_failure(failed_joint_idx)

        # Log failure
        self.log_joint_failure(failed_joint_idx)

        # Potentially switch to degraded mode
        self.switch_to_degraded_mode()

    def reconfigure_control_for_failure(self, failed_joint_idx):
        """
        Reconfigure control system to work around joint failure.
        """
        # Adjust control algorithms to work with reduced DOF
        # This might involve:
        # - Recomputing Jacobians without failed joint
        # - Adjusting task priorities
        # - Modifying motion patterns
        pass

    def switch_to_degraded_mode(self):
        """
        Switch to degraded operational mode after failure.
        """
        # Reduce walking speed
        self.max_walk_speed *= 0.5

        # Increase safety margins
        self.safety_thresholds['zmp_deviation'] *= 0.7
        self.safety_thresholds['tilt_angle'] *= 0.8

        # Simplify behaviors
        self.allow_complex_motions = False

        print("Switched to DEGRADED MODE due to joint failure")

class HumanoidController:
    def __init__(self):
        # Initialize all subsystems
        self.zmp_controller = ZMPController()
        self.osc = OperationalSpaceController()
        self.mpc_controller = MPCWalkingController()
        self.adaptive_controller = AdaptiveController()
        self.safety_controller = SafetyController()

        # Control parameters
        self.control_frequency = 1000  # Hz
        self.dt = 1.0 / self.control_frequency

        # State variables
        self.current_state = None
        self.desired_state = None
        self.control_output = None

    def control_step(self, sensor_data, desired_behavior):
        """
        Main control step function executing all control subsystems.
        """
        # 1. Update state estimate
        self.current_state = self.estimate_state(sensor_data)

        # 2. Check safety conditions
        if not self.safety_controller.check_safety_conditions(self.current_state):
            # Safety violation - apply emergency procedures
            self.emergency_stop()
            return np.zeros(self.n_joints)

        # 3. Plan high-level behavior
        planned_trajectory = self.plan_behavior(desired_behavior)

        # 4. Execute whole-body control
        control_torques = self.execute_whole_body_control(planned_trajectory)

        # 5. Apply adaptive corrections
        if self.use_adaptive_control:
            prediction_error = self.calculate_prediction_error(control_torques)
            control_torques = self.adaptive_controller.update_control_with_adaptation(
                control_torques, self.current_state, prediction_error
            )

        # 6. Apply safety limits
        control_torques = self.apply_control_limits(control_torques)

        # 7. Send commands to robot
        self.send_control_commands(control_torques)

        return control_torques

    def estimate_state(self, sensor_data):
        """
        Estimate full robot state from sensor data.
        """
        state = {
            'joint_positions': sensor_data.get('joint_positions', np.zeros(self.n_joints)),
            'joint_velocities': sensor_data.get('joint_velocities', np.zeros(self.n_joints)),
            'joint_torques': sensor_data.get('joint_torques', np.zeros(self.n_joints)),
            'imu_data': sensor_data.get('imu', {}),
            'ft_sensors': sensor_data.get('force_torque', {}),
            'contact_sensors': sensor_data.get('contact', {}),
            'camera_data': sensor_data.get('camera', None),
            'lidar_data': sensor_data.get('lidar', None)
        }

        # Calculate derived quantities
        state['com_position'] = self.calculate_com_position(state['joint_positions'])
        state['com_velocity'] = self.calculate_com_velocity(state['joint_positions'], state['joint_velocities'])
        state['com_acceleration'] = self.calculate_com_acceleration(state['joint_positions'], state['joint_velocities'], state['joint_accelerations'])

        return state

    def plan_behavior(self, desired_behavior):
        """
        Plan robot behavior based on high-level commands.
        """
        if desired_behavior['type'] == 'walking':
            return self.plan_walking_trajectory(desired_behavior['target'])
        elif desired_behavior['type'] == 'manipulation':
            return self.plan_manipulation_trajectory(desired_behavior['target'])
        elif desired_behavior['type'] == 'balance':
            return self.plan_balance_trajectory()
        else:
            return self.plan_idle_trajectory()

    def execute_whole_body_control(self, trajectory):
        """
        Execute whole-body control to follow planned trajectory.
        """
        # Decompose complex task into multiple operational space tasks
        tasks = []

        # Balance task
        if 'balance' in trajectory:
            balance_jac, balance_acc = self.zmp_controller.balance_control_task(
                trajectory['com_position'],
                trajectory['com_velocity'],
                trajectory['com_acceleration']
            )
            tasks.append(('balance', balance_jac, balance_acc, 1, 1.0))  # High priority

        # Walking task
        if 'walking' in trajectory:
            walking_jac, walking_acc = self.mpc_controller.walking_task(
                trajectory['walking_target'],
                trajectory['support_foot']
            )
            tasks.append(('walking', walking_jac, walking_acc, 2, 0.8))

        # Manipulation task
        if 'manipulation' in trajectory:
            manip_jac, manip_acc = self.osc.end_effector_control_task(
                trajectory['ee_name'],
                trajectory['target_pose'],
                trajectory['target_twist'],
                trajectory['target_accel']
            )
            tasks.append(('manipulation', manip_jac, manip_acc, 3, 0.5))

        # Posture task
        posture_jac, posture_acc = self.osc.posture_control_task(
            self.current_state['joint_positions'],
            trajectory['desired_posture']
        )
        tasks.append(('posture', posture_jac, posture_acc, 4, 0.2))

        # Execute prioritized task control
        total_torques = np.zeros(self.n_joints)

        for task_name, jacobian, acceleration, priority, weight in sorted(tasks, key=lambda x: x[3]):
            # Calculate torques for this task
            task_torques = self.osc.compute_operational_space_control(
                self.current_state['joint_positions'],
                self.current_state['joint_velocities'],
                {task_name: acceleration}
            )

            # Apply nullspace projection for lower priority tasks
            for lower_task_name, lower_jac, lower_acc, lower_priority, lower_weight in tasks:
                if lower_priority > priority:
                    # Project into nullspace of higher priority tasks
                    pass

            total_torques += weight * task_torques

        return total_torques

    def calculate_prediction_error(self, applied_torques):
        """
        Calculate prediction error for adaptive control.
        """
        # Compare actual vs predicted robot behavior
        # This would involve comparing sensor measurements to model predictions
        pass

    def apply_control_limits(self, torques):
        """
        Apply physical and safety limits to control outputs.
        """
        # Apply torque limits
        max_torques = self.get_joint_torque_limits()
        limited_torques = np.clip(torques, -max_torques, max_torques)

        # Apply rate limits
        if hasattr(self, 'previous_torques'):
            max_rate = self.get_torque_rate_limits()
            rate_limited = np.clip(
                limited_torques - self.previous_torques,
                -max_rate * self.dt,
                max_rate * self.dt
            )
            limited_torques = self.previous_torques + rate_limited

        self.previous_torques = limited_torques.copy()
        return limited_torques

    def send_control_commands(self, torques):
        """
        Send control commands to robot hardware/simulation.
        """
        # In simulation: apply torques to physics engine
        # In real robot: send commands to motor controllers
        pass

    def emergency_stop(self):
        """
        Execute emergency stop procedure.
        """
        # Apply zero torques
        zero_torques = np.zeros(self.n_joints)
        self.send_control_commands(zero_torques)

        # Activate safety procedures
        self.safety_controller.trigger_emergency_stop()

        print("EMERGENCY STOP EXECUTED")
```

## Control Implementation Example

### Complete Humanoid Control Node

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float64MultiArray
from builtin_interfaces.msg import Duration
import numpy as np
import math

class HumanoidControlNode(Node):
    def __init__(self):
        super().__init__('humanoid_control_node')

        # Initialize control systems
        self.balance_controller = ZMPController(com_height=0.85)
        self.osc = OperationalSpaceController()
        self.walking_controller = MPCWalkingController()
        self.safety_controller = SafetyController()

        # Publishers
        self.joint_cmd_pub = self.create_publisher(Float64MultiArray, '/joint_commands', 10)
        self.com_state_pub = self.create_publisher(Vector3, '/com_state', 10)
        self.zmp_pub = self.create_publisher(Vector3, '/zmp_state', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Control timer
        self.control_timer = self.create_timer(0.001, self.control_step)  # 1000 Hz

        # Robot state
        self.joint_positions = np.zeros(28)  # Example: 28 DOF humanoid
        self.joint_velocities = np.zeros(28)
        self.joint_torques = np.zeros(28)
        self.imu_data = None

        # Control parameters
        self.com_height = 0.85
        self.control_mode = 'balance'  # 'balance', 'walking', 'manipulation'

        self.get_logger().info('Humanoid Control Node initialized')

    def joint_state_callback(self, msg):
        """Update joint state information."""
        if len(msg.position) == len(self.joint_positions):
            self.joint_positions = np.array(msg.position)
        if len(msg.velocity) == len(self.joint_velocities):
            self.joint_velocities = np.array(msg.velocity)
        if len(msg.effort) == len(self.joint_torques):
            self.joint_torques = np.array(msg.effort)

    def imu_callback(self, msg):
        """Update IMU data."""
        self.imu_data = msg

    def control_step(self):
        """Main control execution step."""
        if self.joint_positions is None or self.imu_data is None:
            return

        # Calculate current state
        com_pos = self.calculate_com_position(self.joint_positions)
        com_vel = self.calculate_com_velocity(self.joint_positions, self.joint_velocities)
        com_acc = self.calculate_com_acceleration(com_pos, com_vel)

        # Calculate current ZMP
        current_zmp = self.balance_controller.calculate_zmp(com_pos, com_acc)

        # Determine control mode based on state
        if self.safety_controller.check_safety_conditions({'com_position': com_pos, 'com_acceleration': com_acc}):
            if self.control_mode == 'balance':
                # Balance control
                desired_zmp = self.calculate_balancing_zmp(com_pos, com_vel)
                balance_torques, _ = self.balance_controller.compute_balance_correction(
                    current_zmp, desired_zmp, dt=0.001
                )

                # Publish state information
                com_msg = Vector3()
                com_msg.x, com_msg.y, com_msg.z = com_pos
                self.com_state_pub.publish(com_msg)

                zmp_msg = Vector3()
                zmp_msg.x, zmp_msg.y, zmp_msg.z = current_zmp[0], current_zmp[1], 0.0
                self.zmp_pub.publish(zmp_msg)

                # Apply control torques
                self.apply_joint_torques(balance_torques)
            elif self.control_mode == 'walking':
                # Walking control using MPC
                reference_trajectory = self.walking_controller.update_reference_trajectory(
                    self.footstep_plan, self.get_time()
                )

                zmp_commands = self.walking_controller.solve_mpc(
                    np.concatenate([com_pos[:2], com_vel[:2]]),  # Current state
                    reference_trajectory  # Reference trajectory
                )

                # Use MPC output for balance control
                balance_torques, _ = self.balance_controller.compute_balance_correction(
                    current_zmp, zmp_commands[:2], dt=0.001
                )

                self.apply_joint_torques(balance_torques)
        else:
            # Safety violation - emergency stop
            self.emergency_stop()

    def calculate_com_position(self, joint_positions):
        """Calculate center of mass position from joint positions."""
        # This would involve forward kinematics and link mass information
        # For this example, we'll use a simplified calculation
        # In practice, this would use the robot's URDF/SRDF information

        # Simplified CoM calculation assuming fixed link masses and positions
        total_mass = 50.0  # Total robot mass (kg)
        com_x = 0.0
        com_y = 0.0
        com_z = self.com_height  # Fixed height assumption

        # Calculate weighted average of link positions based on masses
        # This is a placeholder - real implementation would use FK and mass info
        for i, joint_pos in enumerate(joint_positions):
            # Each joint contributes to CoM based on its associated link mass
            # Simplified: assume uniform distribution
            link_mass = 50.0 / len(joint_positions)  # Uniform mass distribution
            com_x += joint_pos * link_mass / total_mass
            com_y += joint_pos * link_mass / total_mass  # Simplified

        return np.array([com_x, com_y, com_z])

    def calculate_com_velocity(self, joint_positions, joint_velocities):
        """Calculate center of mass velocity."""
        # Simplified - in reality would require more complex calculation
        # involving Jacobians and link velocities
        dt = 0.001  # Control timestep
        if hasattr(self, 'previous_com_pos'):
            current_com_pos = self.calculate_com_position(joint_positions)
            com_vel = (current_com_pos - self.previous_com_pos) / dt
            self.previous_com_pos = current_com_pos
            return com_vel
        else:
            self.previous_com_pos = self.calculate_com_position(joint_positions)
            return np.zeros(3)

    def calculate_com_acceleration(self, com_pos, com_vel):
        """Calculate center of mass acceleration."""
        dt = 0.001
        if hasattr(self, 'previous_com_vel'):
            com_acc = (com_vel - self.previous_com_vel) / dt
            self.previous_com_vel = com_vel
            return com_acc
        else:
            self.previous_com_vel = com_vel
            return np.zeros(3)

    def calculate_balancing_zmp(self, com_pos, com_vel):
        """Calculate desired ZMP for balancing."""
        # For balancing, desired ZMP is typically under the support polygon center
        # This would be updated based on foot positions and support state
        support_center = np.array([0.0, 0.0])  # Simplified - would use actual foot positions
        return support_center

    def apply_joint_torques(self, torques):
        """Apply computed torques to robot joints."""
        cmd_msg = Float64MultiArray()
        cmd_msg.data = torques.tolist()
        self.joint_cmd_pub.publish(cmd_msg)

    def emergency_stop(self):
        """Execute emergency stop."""
        zero_torques = Float64MultiArray()
        zero_torques.data = [0.0] * len(self.joint_positions)
        self.joint_cmd_pub.publish(zero_torques)
        self.get_logger().error('EMERGENCY STOP ACTIVATED')

    def set_control_mode(self, mode):
        """Set control mode."""
        if mode in ['balance', 'walking', 'manipulation']:
            self.control_mode = mode
            self.get_logger().info(f'Control mode set to: {mode}')
        else:
            self.get_logger().warn(f'Invalid control mode: {mode}')

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidControlNode()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down humanoid controller...')
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

Humanoid control systems require sophisticated multi-layered approaches that coordinate balance, walking, manipulation, and safety. The key components include:

1. **Balance Control**: ZMP-based control for maintaining stability
2. **Walking Control**: Pattern generation and MPC for locomotion
3. **Whole-Body Control**: Coordinated control of all DOFs
4. **Adaptive Control**: Parameter adaptation for changing conditions
5. **Safety Systems**: Emergency stop and recovery mechanisms
6. **Hierarchical Control**: Task prioritization and coordination

These systems enable humanoid robots to perform complex behaviors while maintaining stability and safety in dynamic environments.