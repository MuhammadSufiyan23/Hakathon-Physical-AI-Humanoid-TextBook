---
sidebar_label: 'Humanoid Dynamics and Control'
title: 'Humanoid Dynamics and Control'
---

# Humanoid Dynamics and Control

## Introduction to Humanoid Dynamics

Humanoid dynamics involves the study of forces, torques, and motion of robots with human-like structure. Unlike simpler robots, humanoids have complex multibody systems with multiple interconnected links, requiring sophisticated dynamic modeling to understand their behavior and design effective control systems.

## Mathematical Foundation of Robot Dynamics

### Newton-Euler Equations

For each link in the humanoid robot, the Newton-Euler equations describe the relationship between forces, torques, and motion:

**Translation (Newton's equation):**
```
F = ma
```

**Rotation (Euler's equation):**
```
τ = Iα + ω × (Iω)
```

Where:
- F: Force vector
- τ: Torque vector
- m: Mass
- a: Linear acceleration
- I: Inertia tensor
- α: Angular acceleration
- ω: Angular velocity

### Lagrangian Formulation

The Lagrangian formulation provides a systematic way to derive the equations of motion:

```
L = T - V
```

Where L is the Lagrangian, T is the kinetic energy, and V is the potential energy.

The equations of motion are given by:

```
d/dt(∂L/∂q̇) - ∂L/∂q = τ
```

Where q represents the generalized coordinates (joint angles).

## Humanoid Robot Dynamics Model

### General Dynamics Equation

The general equation of motion for a humanoid robot is:

```
M(q)q̈ + C(q, q̇)q̇ + G(q) = τ + J^T F_ext
```

Where:
- M(q): Mass/inertia matrix
- C(q, q̇): Coriolis and centrifugal matrix
- G(q): Gravity vector
- τ: Joint torques
- J: Jacobian matrix
- F_ext: External forces

### Implementation of Dynamics Model

```python
import numpy as np
import math
from scipy.spatial.transform import Rotation as R

class HumanoidDynamicsModel:
    def __init__(self, robot_config):
        """
        Initialize dynamics model for humanoid robot.

        robot_config: Dictionary containing robot parameters
        """
        self.config = robot_config
        self.links = robot_config['links']
        self.joints = robot_config['joints']

        # Initialize matrices
        self.n_dofs = len(robot_config['joints'])
        self.M = np.zeros((self.n_dofs, self.n_dofs))
        self.C = np.zeros((self.n_dofs, self.n_dofs))
        self.G = np.zeros(self.n_dofs)

    def compute_mass_matrix(self, q):
        """
        Compute the mass/inertia matrix M(q) using recursive Newton-Euler algorithm.
        q: Joint angles [n_dofs x 1]
        """
        # This is a simplified version - full implementation would be complex
        # and would use the composite rigid body algorithm

        # Initialize mass matrix
        M = np.zeros((self.n_dofs, self.n_dofs))

        # For each joint, compute the contribution to the mass matrix
        for i in range(self.n_dofs):
            for j in range(self.n_dofs):
                # Compute the influence of joint j on joint i
                M[i, j] = self.compute_influence_element(i, j, q)

        return M

    def compute_coriolis_matrix(self, q, qdot):
        """
        Compute the Coriolis and centrifugal matrix C(q, qdot).
        q: Joint angles
        qdot: Joint velocities
        """
        C = np.zeros((self.n_dofs, self.n_dofs))

        # Compute Coriolis terms using Christoffel symbols
        M = self.compute_mass_matrix(q)

        for i in range(self.n_dofs):
            for j in range(self.n_dofs):
                c_sum = 0
                for k in range(self.n_dofs):
                    # Christoffel symbol of the first kind
                    christoffel = (self.partial_derivative_M(i, j, k, q) +
                                 self.partial_derivative_M(i, k, j, q) -
                                 self.partial_derivative_M(j, k, i, q)) / 2
                    c_sum += christoffel * qdot[k]

                C[i, j] = c_sum

        return C

    def compute_gravity_vector(self, q):
        """
        Compute the gravity vector G(q).
        q: Joint angles
        """
        G = np.zeros(self.n_dofs)

        # Calculate gravitational forces on each link
        gravity = np.array([0, 0, -9.81])  # Earth's gravity

        for i, link in enumerate(self.links):
            # Transform gravity vector to link frame
            # This requires forward kinematics to get link poses
            link_pose = self.forward_kinematics(q, i)
            R_link = link_pose[:3, :3]  # Rotation matrix

            # Gravity force in link frame
            gravity_link = R_link.T @ gravity

            # Calculate moment arm and torque contribution
            com_position = link['com_offset']  # Center of mass offset
            mass = link['mass']

            # Contribution to gravity vector
            for j in range(self.n_dofs):
                # Calculate how joint j affects this link's gravity
                # This requires calculating the Jacobian for gravity effects
                jacobian_elem = self.calculate_gravity_jacobian_element(i, j, q)
                G[j] += mass * gravity_link @ jacobian_elem

        return G

    def calculate_inverse_dynamics(self, q, qdot, qddot):
        """
        Calculate required joint torques using inverse dynamics.
        q: Joint angles
        qdot: Joint velocities
        qddot: Joint accelerations
        """
        # Compute dynamics matrices
        M = self.compute_mass_matrix(q)
        C = self.compute_coriolis_matrix(q, qdot)
        G = self.compute_gravity_vector(q)

        # Calculate required torques
        tau = M @ qddot + C @ qdot + G

        return tau

    def calculate_forward_dynamics(self, q, qdot, tau):
        """
        Calculate joint accelerations using forward dynamics.
        q: Joint angles
        qdot: Joint velocities
        tau: Applied joint torques
        """
        # Compute dynamics matrices
        M = self.compute_mass_matrix(q)
        C = self.compute_coriolis_matrix(q, qdot)
        G = self.compute_gravity_vector(q)

        # Solve for accelerations: M*qddot = tau - C*qdot - G
        qddot = np.linalg.solve(M, tau - C @ qdot - G)

        return qddot

    def compute_influence_element(self, i, j, q):
        """
        Compute element (i,j) of the mass matrix.
        This is a simplified implementation - real version would be much more complex.
        """
        # In reality, this would involve calculating the kinetic energy
        # contribution of each link and taking second derivatives
        # For this example, we'll return a simplified value

        # Get masses and inertias of relevant links
        link_i = self.links[min(i, len(self.links)-1)]
        link_j = self.links[min(j, len(self.links)-1)]

        # Simplified mass matrix element calculation
        if i == j:
            # Diagonal element - mainly self-inertia
            return link_i.get('mass', 1.0) + link_i.get('inertia_diag', np.eye(3))[0, 0]
        else:
            # Off-diagonal - coupling between joints
            # This would involve complex geometric relationships
            return 0.1 * (link_i.get('mass', 1.0) + link_j.get('mass', 1.0))

    def partial_derivative_M(self, i, j, k, q):
        """
        Calculate partial derivative of mass matrix element M[i,j] with respect to q[k].
        """
        # This is a complex calculation in practice
        # Would require symbolic differentiation of the mass matrix
        # For this example, return a simplified value
        return 0.01

    def calculate_gravity_jacobian_element(self, link_idx, joint_idx, q):
        """
        Calculate the Jacobian element for gravity effects.
        """
        # This would involve calculating how joint motion affects
        # the gravitational force on a particular link
        return np.array([0.1, 0.1, 0.1])  # Placeholder

# Example usage
def example_dynamics():
    # Define a simple robot configuration
    robot_config = {
        'links': [
            {'mass': 5.0, 'com_offset': [0, 0, 0.1], 'inertia_diag': np.eye(3)},
            {'mass': 2.0, 'com_offset': [0.1, 0, 0], 'inertia_diag': np.eye(3)},
            {'mass': 1.5, 'com_offset': [0.1, 0, 0], 'inertia_diag': np.eye(3)}
        ],
        'joints': [
            {'type': 'revolute', 'axis': [0, 0, 1]},
            {'type': 'revolute', 'axis': [0, 1, 0]},
            {'type': 'revolute', 'axis': [0, 1, 0]}
        ]
    }

    dynamics = HumanoidDynamicsModel(robot_config)

    # Example calculation
    q = np.array([0.0, 0.1, -0.1])  # Joint angles
    qdot = np.array([0.1, 0.2, -0.1])  # Joint velocities
    qddot = np.array([0.01, 0.02, -0.01])  # Joint accelerations

    # Calculate required torques for given motion
    tau = dynamics.calculate_inverse_dynamics(q, qdot, qddot)
    print(f"Required torques: {tau}")

    # Calculate motion for given torques
    qddot_calc = dynamics.calculate_forward_dynamics(q, qdot, tau)
    print(f"Calculated accelerations: {qddot_calc}")
```

## Balance Control and Zero Moment Point (ZMP)

### ZMP Theory

The Zero Moment Point (ZMP) is a crucial concept in humanoid balance control. It represents the point on the ground where the net moment of the ground reaction force is zero.

```
ZMP_x = x_com - (h / g) * ẍ_com
ZMP_y = y_com - (h / g) * ÿ_com
```

Where:
- (x_com, y_com): Center of mass position
- h: Height of center of mass above ground
- g: Gravitational acceleration
- (ẍ_com, ÿ_com): Center of mass accelerations

### ZMP-Based Balance Controller

```python
class ZMPController:
    def __init__(self, com_height=0.8, gravity=9.81):
        """
        Initialize ZMP controller.

        com_height: Nominal center of mass height
        gravity: Gravitational acceleration
        """
        self.com_height = com_height
        self.gravity = gravity

        # Control gains
        self.kp = 10.0  # Proportional gain
        self.kd = 2.0   # Derivative gain

        # Support polygon (area where ZMP must be located)
        self.support_polygon = self.define_support_polygon()

        # Internal state
        self.previous_zmp_error = np.zeros(2)
        self.integral_zmp_error = np.zeros(2)

    def define_support_polygon(self):
        """
        Define the support polygon based on foot positions.
        This is simplified for a single foot support.
        """
        # For single support on left foot (example)
        # In practice, this would be dynamically updated based on contact
        return {
            'vertices': np.array([
                [-0.1, -0.05],  # front-left
                [0.1, -0.05],   # front-right
                [0.1, 0.05],    # back-right
                [-0.1, 0.05]    # back-left
            ]),
            'center': np.array([0.0, 0.0])
        }

    def calculate_zmp(self, com_pos, com_acc):
        """
        Calculate ZMP from center of mass position and acceleration.

        com_pos: [x, y, z] center of mass position
        com_acc: [ẍ, ÿ, z̈] center of mass acceleration
        """
        zmp_x = com_pos[0] - (self.com_height / self.gravity) * com_acc[0]
        zmp_y = com_pos[1] - (self.com_height / self.gravity) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def is_zmp_stable(self, zmp):
        """
        Check if ZMP is within support polygon.
        """
        # Simple point-in-polygon check
        vertices = self.support_polygon['vertices']
        x, y = zmp

        # Ray casting algorithm for point-in-polygon
        inside = False
        j = len(vertices) - 1

        for i in range(len(vertices)):
            xi, yi = vertices[i]
            xj, yj = vertices[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i

        return inside

    def compute_balance_correction(self, current_zmp, desired_zmp, dt=0.01):
        """
        Compute balance correction torques using PD control on ZMP error.

        current_zmp: Current ZMP position [x, y]
        desired_zmp: Desired ZMP position [x, y]
        dt: Time step
        """
        # Calculate ZMP error
        zmp_error = desired_zmp - current_zmp

        # PID control for ZMP
        self.integral_zmp_error += zmp_error * dt

        # Calculate derivative
        derivative_error = (zmp_error - self.previous_zmp_error) / dt if dt > 0 else np.zeros(2)

        # Store current error for next iteration
        self.previous_zmp_error = zmp_error

        # PID control output
        correction = (self.kp * zmp_error +
                     self.kd * derivative_error)

        # Convert ZMP correction to joint torques
        # This would involve inverse dynamics and whole-body control
        joint_correction = self.map_zmp_to_joints(correction)

        return joint_correction, zmp_error

    def map_zmp_to_joints(self, zmp_correction):
        """
        Map ZMP correction to joint torques.
        This is a simplified mapping - real implementation would be complex.
        """
        # In practice, this would use whole-body control techniques
        # like operational space control or quadratic programming
        n_joints = 28  # Typical humanoid DOF
        joint_torques = np.zeros(n_joints)

        # Distribute correction to relevant joints (hips, ankles, etc.)
        hip_joints = [0, 1, 2, 6, 7, 8]  # Example hip joint indices
        ankle_joints = [12, 13, 18, 19]  # Example ankle joint indices

        # Apply corrections to balance joints
        for i, joint_idx in enumerate(hip_joints):
            if joint_idx < n_joints:
                joint_torques[joint_idx] = zmp_correction[0] * 0.1 + zmp_correction[1] * 0.05

        for i, joint_idx in enumerate(ankle_joints):
            if joint_idx < n_joints:
                joint_torques[joint_idx] = zmp_correction[0] * 0.05 + zmp_correction[1] * 0.1

        return joint_torques

class CapturePointController:
    """
    Capture Point (Capture Point) based balance control.
    The Capture Point is where the robot would need to step to come to rest.
    """

    def __init__(self, com_height=0.8, gravity=9.81):
        self.com_height = com_height
        self.gravity = gravity
        self.omega = math.sqrt(gravity / com_height)

    def calculate_capture_point(self, com_pos, com_vel):
        """
        Calculate the Capture Point from current CoM state.

        com_pos: [x, y, z] center of mass position
        com_vel: [ẋ, ẏ, ż] center of mass velocity
        """
        cp_x = com_pos[0] + com_vel[0] / self.omega
        cp_y = com_pos[1] + com_vel[1] / self.omega

        return np.array([cp_x, cp_y])

    def should_step(self, capture_point, foot_position, safety_margin=0.1):
        """
        Determine if a step is needed based on Capture Point.

        capture_point: Calculated capture point [x, y]
        foot_position: Current stance foot position [x, y]
        safety_margin: Safety margin around foot
        """
        # Calculate distance from capture point to foot
        dist = np.linalg.norm(capture_point - foot_position)

        # Step is needed if capture point is outside safety region
        foot_size = 0.15  # Approximate foot size
        threshold = foot_size + safety_margin

        return dist > threshold
```

## Operational Space Control

Operational space control allows controlling task-space variables (like end-effector position) while considering the robot's dynamics.

### Operational Space Dynamics

The operational space dynamics equation is:

```
Λẍ + μ + η = J M⁻¹ τ + J M⁻¹ Jᵀ F_ext
```

Where:
- Λ: Operational space inertia matrix
- μ: Operational space Coriolis matrix
- η: Operational space gravity vector
- J: Jacobian matrix
- F_ext: External forces in operational space

### Implementation

```python
class OperationalSpaceController:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.n_dofs = robot_model.n_dofs

        # Task space dimensions
        self.task_dim = 6  # 3D position + 3D orientation

    def calculate_operational_matrices(self, q, qdot):
        """
        Calculate operational space dynamics matrices.
        """
        # Calculate Jacobian
        J = self.robot.calculate_jacobian(q)

        # Calculate mass matrix
        M = self.robot.compute_mass_matrix(q)

        # Calculate operational space inertia matrix: Λ = J * M⁻¹ * Jᵀ
        M_inv = np.linalg.inv(M)
        Lambda = J @ M_inv @ J.T

        # Calculate operational space Coriolis matrix: μ = J * M⁻¹ * (C*qdot - Jᵀ*μ_task)
        C = self.robot.compute_coriolis_matrix(q, qdot)
        mu = J @ M_inv @ (C @ qdot)

        # Calculate operational space gravity vector: η = J * M⁻¹ * G
        G = self.robot.compute_gravity_vector(q)
        eta = J @ M_inv @ G

        return Lambda, mu, eta, J

    def compute_task_space_control(self, x_des, xd_des, xdd_des,
                                   x_curr, xd_curr, Kp=100, Kd=20):
        """
        Compute operational space control law.

        x_des: Desired task space position
        xd_des: Desired task space velocity
        xdd_des: Desired task space acceleration
        x_curr: Current task space position
        xd_curr: Current task space velocity
        Kp: Proportional gain
        Kd: Derivative gain
        """
        # Calculate task space error
        pos_error = x_des - x_curr
        vel_error = xd_des - xd_curr

        # Calculate desired task space acceleration
        xdd_cmd = xdd_des + Kp * pos_error + Kd * vel_error

        return xdd_cmd

    def map_task_to_joint_torques(self, xdd_task, J, Lambda, mu, eta):
        """
        Map task space acceleration to joint torques.
        """
        # Calculate joint torques using operational space control law
        # τ = Jᵀ * Λ * (xdd_task - μ - η) + gravity_compensation
        tau_task = J.T @ Lambda @ (xdd_task - mu - eta)

        # Add gravity compensation
        G = self.robot.compute_gravity_vector(self.robot.q)
        tau = tau_task + G

        return tau

class WholeBodyController:
    """
    Whole-body controller that coordinates multiple tasks simultaneously.
    """

    def __init__(self, robot_model):
        self.robot = robot_model
        self.osc = OperationalSpaceController(robot_model)
        self.zmp_controller = ZMPController()

        # Task priorities
        self.tasks = []

    def add_task(self, task_name, task_func, priority, weight=1.0):
        """
        Add a control task to the whole-body controller.

        task_name: Name of the task
        task_func: Function that computes task torques
        priority: Priority level (0 = highest)
        weight: Task weight
        """
        task = {
            'name': task_name,
            'function': task_func,
            'priority': priority,
            'weight': weight
        }

        self.tasks.append(task)
        self.tasks.sort(key=lambda x: x['priority'])

    def compute_whole_body_control(self, state):
        """
        Compute whole-body control torques.
        """
        # Initialize torques
        total_tau = np.zeros(self.robot.n_dofs)

        # Compute torques for each task based on priority
        for task in self.tasks:
            task_tau = task['function'](state)

            # Apply task weighting
            weighted_tau = task['weight'] * task_tau

            # Add to total torques
            total_tau += weighted_tau

        return total_tau

    def balance_task(self, state):
        """
        Balance maintenance task.
        """
        # Calculate current ZMP
        com_pos = state['com_position']
        com_acc = state['com_acceleration']
        current_zmp = self.zmp_controller.calculate_zmp(com_pos, com_acc)

        # Calculate desired ZMP (usually center of support polygon)
        desired_zmp = self.zmp_controller.support_polygon['center']

        # Compute balance correction
        dt = 0.001  # Control time step
        balance_tau, zmp_error = self.zmp_controller.compute_balance_correction(
            current_zmp, desired_zmp, dt
        )

        return balance_tau

    def posture_task(self, state):
        """
        Posture maintenance task.
        """
        current_q = state['joint_angles']
        desired_q = state['desired_joint_angles']

        # Simple PD control in joint space
        Kp = 100.0
        Kd = 20.0

        q_error = desired_q - current_q
        qdot_error = state['desired_joint_velocities'] - state['joint_velocities']

        tau = Kp * q_error + Kd * qdot_error

        return tau
```

## Walking Dynamics and Control

### Inverted Pendulum Model

The simplest model for walking is the Linear Inverted Pendulum Model (LIPM):

```
ẍ_com = ω² * (x_com - x_zmp)
```

Where ω² = g/h (g is gravity, h is CoM height).

### Walking Pattern Generator

```python
class WalkingPatternGenerator:
    def __init__(self, step_height=0.05, step_length=0.3, step_time=0.8):
        self.step_height = step_height
        self.step_length = step_length
        self.step_time = step_time

        # LIPM parameters
        self.com_height = 0.8
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

    def generate_com_trajectory(self, start_pos, goal_pos, step_size=0.3):
        """
        Generate CoM trajectory for walking from start to goal.
        """
        # Calculate number of steps needed
        distance = np.linalg.norm(goal_pos[:2] - start_pos[:2])
        n_steps = int(distance / step_size)

        # Generate footsteps
        footsteps = self.generate_footsteps(start_pos, goal_pos, n_steps)

        # Generate CoM trajectory using LIPM
        com_trajectory = self.generate_lipm_trajectory(footsteps)

        return com_trajectory, footsteps

    def generate_footsteps(self, start_pos, goal_pos, n_steps):
        """
        Generate sequence of footsteps for walking.
        """
        footsteps = []

        # Calculate step direction
        direction = (goal_pos[:2] - start_pos[:2]) / n_steps if n_steps > 0 else np.array([0, 0])

        for i in range(n_steps):
            # Alternate feet
            foot = 'left' if i % 2 == 0 else 'right'

            # Calculate foot position
            step_pos = start_pos[:2] + (i + 1) * direction

            # Add step timing
            timing = (i + 1) * self.step_time

            footsteps.append({
                'position': step_pos,
                'foot': foot,
                'timing': timing,
                'support_duration': self.step_time
            })

        return footsteps

    def generate_lipm_trajectory(self, footsteps):
        """
        Generate CoM trajectory using Linear Inverted Pendulum Model.
        """
        com_trajectory = []

        # Start from first foot position
        if footsteps:
            current_com = np.array([footsteps[0]['position'][0],
                                  footsteps[0]['position'][1],
                                  self.com_height])
        else:
            current_com = np.array([0, 0, self.com_height])

        # Generate trajectory for each step
        for i, footstep in enumerate(footsteps):
            # Calculate transition from current support foot to new footstep
            if i == 0:
                start_com = current_com
            else:
                # Previous step end position
                start_com = current_com

            # Target position is between current and next footstep
            if i < len(footsteps) - 1:
                target_com_x = (footstep['position'][0] + footsteps[i+1]['position'][0]) / 2
                target_com_y = (footstep['position'][1] + footsteps[i+1]['position'][1]) / 2
            else:
                target_com_x = footstep['position'][0]
                target_com_y = footstep['position'][1]

            # Generate trajectory segment using LIPM
            segment = self.generate_lipm_segment(
                start_com,
                np.array([target_com_x, target_com_y, self.com_height]),
                footstep['timing'],
                footstep['support_duration']
            )

            com_trajectory.extend(segment)

            # Update current CoM for next iteration
            if segment:
                current_com = segment[-1]['position']

        return com_trajectory

    def generate_lipm_segment(self, start_com, target_com, start_time, duration):
        """
        Generate a single LIPM trajectory segment.
        """
        trajectory = []
        n_points = int(duration / 0.01)  # 100 Hz trajectory

        for i in range(n_points):
            t = i * 0.01  # Time since start of segment
            progress = t / duration if duration > 0 else 1.0

            # LIPM solution for CoM trajectory
            # x(t) = x_zmp + (x_0 - x_zmp) * cosh(ω*t) + (ẋ_0/ω) * sinh(ω*t)

            # For simplicity, use linear interpolation with LIPM constraints
            x = start_com[0] + progress * (target_com[0] - start_com[0])
            y = start_com[1] + progress * (target_com[1] - start_com[1])
            z = self.com_height  # Keep CoM height constant

            # Add slight oscillation for natural movement
            oscillation = 0.02 * math.sin(2 * math.pi * t * 2)  # 2Hz oscillation
            z += oscillation

            trajectory.append({
                'time': start_time + t,
                'position': np.array([x, y, z]),
                'velocity': self.calculate_velocity(trajectory, -1) if len(trajectory) > 1 else np.zeros(3),
                'acceleration': self.calculate_acceleration(trajectory, -1) if len(trajectory) > 2 else np.zeros(3)
            })

        return trajectory

    def calculate_velocity(self, trajectory, index):
        """
        Calculate velocity from position trajectory.
        """
        if len(trajectory) < 2 or index < 1:
            return np.zeros(3)

        dt = trajectory[index]['time'] - trajectory[index-1]['time']
        if dt <= 0:
            return np.zeros(3)

        dx = trajectory[index]['position'] - trajectory[index-1]['position']
        return dx / dt

    def calculate_acceleration(self, trajectory, index):
        """
        Calculate acceleration from velocity trajectory.
        """
        if len(trajectory) < 3 or index < 2:
            return np.zeros(3)

        dt = trajectory[index]['time'] - trajectory[index-1]['time']
        if dt <= 0:
            return np.zeros(3)

        dv = trajectory[index]['velocity'] - trajectory[index-1]['velocity']
        return dv / dt
```

## Force Control and Impedance Control

### Impedance Control

Impedance control regulates the dynamic relationship between force and position:

```
M_d ẍ + B_d ẋ + K_d x = F_cmd - F_ext
```

Where M_d, B_d, K_d are desired mass, damping, and stiffness matrices.

```python
class ImpedanceController:
    def __init__(self, robot_model):
        self.robot = robot_model

        # Desired impedance parameters
        self.M_d = np.eye(6) * 1.0    # Desired mass matrix
        self.B_d = np.eye(6) * 10.0   # Desired damping matrix
        self.K_d = np.eye(6) * 1000.0 # Desired stiffness matrix

        # Force/torque sensors
        self.force_sensors = {}

    def compute_impedance_control(self, x_des, xd_des, xdd_des,
                                  x_curr, xd_curr, F_ext, dt=0.001):
        """
        Compute impedance control law.

        x_des: Desired position
        xd_des: Desired velocity
        xdd_des: Desired acceleration
        x_curr: Current position
        xd_curr: Current velocity
        F_ext: External forces
        dt: Time step
        """
        # Calculate position and velocity errors
        pos_error = x_des - x_curr
        vel_error = xd_des - xd_curr

        # Calculate desired force based on impedance model
        F_impedance = (self.M_d @ xdd_des +
                      self.B_d @ vel_error +
                      self.K_d @ pos_error)

        # Calculate commanded force
        F_cmd = F_impedance + F_ext

        return F_cmd

    def map_force_to_torques(self, F_task, J):
        """
        Map task space forces to joint torques using Jacobian transpose.
        """
        tau = J.T @ F_task
        return tau

    def admittance_control(self, F_ext, dt=0.001):
        """
        Admittance control - integrates external forces to generate motion.
        """
        # Admittance model: ẍ = A * F_ext
        # Where A is the admittance matrix (inverse of impedance)

        # Calculate admittance matrix
        impedance_matrix = self.M_d + dt * self.B_d + dt**2 * self.K_d
        admittance_matrix = np.linalg.inv(impedance_matrix)

        # Calculate motion from external forces
        xdd_admittance = admittance_matrix @ F_ext

        return xdd_admittance

class HybridForcePositionController:
    """
    Hybrid force/position control for manipulation tasks.
    Controls position in unconstrained directions and force in constrained directions.
    """

    def __init__(self):
        # Selection matrix for force/position control
        self.selection_matrix = np.eye(6)  # Identity initially

    def set_constraint_directions(self, force_directions):
        """
        Set directions for force control vs position control.

        force_directions: List of 6 booleans indicating which directions
                         should be force-controlled (True) vs
                         position-controlled (False)
        """
        self.selection_matrix = np.diag(force_directions).astype(float)

    def compute_hybrid_control(self, x_des, xd_des, xdd_des,
                              x_curr, xd_curr, F_des, F_curr):
        """
        Compute hybrid force/position control.
        """
        # Calculate position control component
        pos_error = x_des - x_curr
        vel_error = xd_des - xd_curr

        Kp_pos = 1000.0
        Kd_pos = 50.0

        acc_pos_control = Kp_pos * pos_error + Kd_pos * vel_error

        # Calculate force control component
        force_error = F_des - F_curr

        Kp_force = 1.0
        acc_force_control = Kp_force * force_error

        # Combine using selection matrix
        acc_total = (np.eye(6) - self.selection_matrix) @ acc_pos_control + \
                   self.selection_matrix @ acc_force_control

        return acc_total
```

## Stability Analysis and Control

### Lyapunov Stability

For nonlinear control systems, Lyapunov stability analysis ensures the system remains stable:

```python
class StabilityAnalyzer:
    def __init__(self, robot_model):
        self.robot = robot_model

    def construct_lyapunov_function(self, state):
        """
        Construct a Lyapunov function for stability analysis.
        For a humanoid, this might be based on energy or tracking error.
        """
        # Example: Lyapunov function based on tracking error
        # V = 0.5 * e^T * P * e + 0.5 * ė^T * ė
        # where e is the tracking error and P is a positive definite matrix

        # Simplified example
        tracking_error = state['error']
        error_rate = state['error_rate']

        P = np.eye(len(tracking_error)) * 10  # Positive definite matrix

        V = 0.5 * tracking_error.T @ P @ tracking_error + \
            0.5 * error_rate.T @ error_rate

        return V

    def analyze_stability(self, state_trajectory):
        """
        Analyze stability by checking if Lyapunov function decreases.
        """
        lyapunov_values = []

        for state in state_trajectory:
            V = self.construct_lyapunov_function(state)
            lyapunov_values.append(V)

        # Check if function is decreasing (stable) or increasing (unstable)
        is_stable = all(lyapunov_values[i] >= lyapunov_values[i+1]
                       for i in range(len(lyapunov_values)-1))

        return is_stable, lyapunov_values
```

## Simulation and Control Implementation

### Complete Humanoid Control System

```python
class HumanoidControlSystem:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.dynamics_model = HumanoidDynamicsModel(robot_model.config)
        self.zmp_controller = ZMPController()
        self.osc = OperationalSpaceController(robot_model)
        self.impedance_controller = ImpedanceController(robot_model)
        self.whole_body_controller = WholeBodyController(robot_model)
        self.walking_generator = WalkingPatternGenerator()

        # State estimation
        self.state_estimator = StateEstimator(robot_model)

        # Control loop timing
        self.control_dt = 0.001  # 1kHz control
        self.estimation_dt = 0.005  # 200Hz estimation

    def control_step(self, sensor_data, desired_behavior):
        """
        Main control step function.

        sensor_data: Dictionary containing sensor measurements
        desired_behavior: Dictionary containing desired robot behavior
        """
        # 1. Estimate current state
        current_state = self.state_estimator.estimate_state(sensor_data)

        # 2. Determine control tasks based on desired behavior
        control_tasks = self.determine_control_tasks(desired_behavior, current_state)

        # 3. Compute control torques
        tau_cmd = self.compute_control_torques(control_tasks, current_state)

        # 4. Apply control torques to robot simulation/real robot
        self.apply_torques(tau_cmd)

        # 5. Update state for next iteration
        self.update_internal_state(current_state, tau_cmd)

        return tau_cmd, current_state

    def determine_control_tasks(self, desired_behavior, current_state):
        """
        Determine which control tasks to execute based on desired behavior.
        """
        tasks = []

        # Balance task - always active
        if desired_behavior.get('balance', True):
            tasks.append(('balance', self.balance_task))

        # Walking task
        if desired_behavior.get('walking', False):
            tasks.append(('walking', self.walking_task))

        # Manipulation task
        if desired_behavior.get('manipulation', False):
            tasks.append(('manipulation', self.manipulation_task))

        # Posture task
        if desired_behavior.get('posture', False):
            tasks.append(('posture', self.posture_task))

        return tasks

    def balance_task(self, current_state):
        """
        Compute torques for balance maintenance.
        """
        # Calculate current ZMP
        com_pos = current_state['com_position']
        com_acc = current_state['com_acceleration']
        current_zmp = self.zmp_controller.calculate_zmp(com_pos, com_acc)

        # Desired ZMP (usually center of support polygon)
        desired_zmp = current_state['support_polygon']['center']

        # Compute balance correction
        balance_tau, zmp_error = self.zmp_controller.compute_balance_correction(
            current_zmp, desired_zmp, self.control_dt
        )

        return balance_tau

    def walking_task(self, current_state):
        """
        Compute torques for walking motion.
        """
        # This would involve following a pre-planned walking trajectory
        # and adjusting based on current state
        walking_tau = np.zeros(self.robot.n_dofs)

        # Example: Follow CoM trajectory
        if 'com_trajectory' in current_state:
            com_error = (current_state['com_trajectory']['desired'] -
                        current_state['com_position'])

            # Simple PD control
            Kp = 500.0
            Kd = 50.0
            walking_tau = Kp * com_error + Kd * (current_state['com_velocity'])

        return walking_tau

    def manipulation_task(self, current_state):
        """
        Compute torques for manipulation tasks.
        """
        # Use operational space control for end-effector tasks
        if 'manipulation_target' in current_state:
            target = current_state['manipulation_target']

            # Calculate Jacobian for end-effector
            J = self.robot.calculate_jacobian(current_state['joint_angles'],
                                           'end_effector')

            # Calculate operational space matrices
            Lambda, mu, eta, _ = self.osc.calculate_operational_matrices(
                current_state['joint_angles'],
                current_state['joint_velocities']
            )

            # Calculate task space control
            xdd_task = self.osc.compute_task_space_control(
                target['position'], target['velocity'], target['acceleration'],
                current_state['end_effector_position'],
                current_state['end_effector_velocity']
            )

            # Map to joint torques
            manipulation_tau = self.osc.map_task_to_joint_torques(
                xdd_task, J, Lambda, mu, eta
            )

            return manipulation_tau

        return np.zeros(self.robot.n_dofs)

    def compute_control_torques(self, tasks, current_state):
        """
        Compute final control torques by combining all tasks.
        """
        total_tau = np.zeros(self.robot.n_dofs)

        for task_name, task_func in tasks:
            try:
                task_tau = task_func(current_state)

                # Add task torques (with proper prioritization in real implementation)
                total_tau += task_tau

            except Exception as e:
                print(f"Error in {task_name} task: {e}")
                continue

        return total_tau

    def apply_torques(self, tau_cmd):
        """
        Apply computed torques to the robot.
        In simulation, this updates the robot model.
        In real hardware, this sends commands to motors.
        """
        # In simulation: update robot dynamics
        # self.robot.apply_torques(tau_cmd)

        # In real hardware: send commands to motor controllers
        # self.motor_interface.send_commands(tau_cmd)
        pass

    def update_internal_state(self, current_state, applied_torques):
        """
        Update internal state for next control cycle.
        """
        # Update any internal filters, estimators, or planning components
        pass

class StateEstimator:
    """
    Estimate robot state from sensor measurements.
    """

    def __init__(self, robot_model):
        self.robot = robot_model

        # Kalman filter for state estimation
        self.kalman_filter = self.initialize_kalman_filter()

    def initialize_kalman_filter(self):
        """
        Initialize Kalman filter for state estimation.
        """
        # State: [joint_positions, joint_velocities, com_position, com_velocity]
        n_states = self.robot.n_dofs * 2 + 6  # 3D com pos/vel

        # Measurement: [joint_positions, accelerometer, gyroscope, foot_sensors]
        n_measurements = self.robot.n_dofs + 6 + 4  # 6 IMU + 4 foot sensors

        # Initialize filter matrices (simplified)
        F = np.eye(n_states)  # State transition
        H = np.eye(n_measurements, n_states)  # Measurement matrix
        Q = np.eye(n_states) * 0.1  # Process noise
        R = np.eye(n_measurements) * 1.0  # Measurement noise
        P = np.eye(n_states) * 1.0  # Error covariance

        return {
            'F': F, 'H': H, 'Q': Q, 'R': R, 'P': P,
            'x': np.zeros(n_states)  # State estimate
        }

    def estimate_state(self, sensor_data):
        """
        Estimate robot state from sensor data using Kalman filter.
        """
        # This would implement the full Kalman filter prediction and update steps
        # For this example, we'll return a simplified state

        state = {
            'joint_angles': sensor_data.get('joint_positions', np.zeros(self.robot.n_dofs)),
            'joint_velocities': sensor_data.get('joint_velocities', np.zeros(self.robot.n_dofs)),
            'com_position': self.calculate_com_position(sensor_data),
            'com_velocity': self.calculate_com_velocity(sensor_data),
            'com_acceleration': self.calculate_com_acceleration(sensor_data),
            'support_polygon': self.calculate_support_polygon(sensor_data),
            'end_effector_position': self.calculate_end_effector_position(sensor_data),
            'end_effector_velocity': self.calculate_end_effector_velocity(sensor_data)
        }

        return state

    def calculate_com_position(self, sensor_data):
        """
        Calculate center of mass position from joint angles.
        """
        # This would use forward kinematics and link masses
        # Simplified for this example
        return np.array([0.0, 0.0, 0.8])

    def calculate_support_polygon(self, sensor_data):
        """
        Calculate support polygon from foot contact sensors.
        """
        # Determine which feet are in contact
        left_contact = sensor_data.get('left_foot_contact', False)
        right_contact = sensor_data.get('right_foot_contact', False)

        if left_contact and right_contact:
            # Double support - use both feet
            return self.calculate_double_support_polygon(sensor_data)
        elif left_contact:
            # Left foot support
            return self.calculate_single_support_polygon('left', sensor_data)
        elif right_contact:
            # Right foot support
            return self.calculate_single_support_polygon('right', sensor_data)
        else:
            # No support - robot is airborne
            return self.calculate_airborne_polygon()

    def calculate_double_support_polygon(self, sensor_data):
        """
        Calculate support polygon for double support phase.
        """
        # Use both feet to define support polygon
        left_foot_pos = sensor_data.get('left_foot_position', [0, -0.1, 0])
        right_foot_pos = sensor_data.get('right_foot_position', [0, 0.1, 0])

        # Define vertices of support polygon
        vertices = np.array([
            [left_foot_pos[0] - 0.1, left_foot_pos[1] - 0.05],   # Left foot back-left
            [left_foot_pos[0] + 0.1, left_foot_pos[1] - 0.05],   # Left foot front-left
            [right_foot_pos[0] + 0.1, right_foot_pos[1] + 0.05], # Right foot front-right
            [right_foot_pos[0] - 0.1, right_foot_pos[1] + 0.05], # Right foot back-right
        ])

        center = np.mean(vertices, axis=0)

        return {'vertices': vertices, 'center': center}
```

## Summary

Humanoid dynamics and control is a complex field that combines multibody dynamics, control theory, and real-time computation. The key components include:

1. **Dynamics Modeling**: Understanding the equations of motion for complex multibody systems
2. **Balance Control**: Using ZMP and Capture Point theories for stable locomotion
3. **Operational Space Control**: Controlling task-space variables while considering robot dynamics
4. **Whole-Body Control**: Coordinating multiple simultaneous tasks
5. **Walking Dynamics**: Planning and controlling bipedal locomotion
6. **Force Control**: Regulating interaction forces with the environment
7. **Stability Analysis**: Ensuring system stability during dynamic motions

These concepts form the foundation for creating stable, efficient, and safe humanoid robots capable of performing complex tasks in human environments.