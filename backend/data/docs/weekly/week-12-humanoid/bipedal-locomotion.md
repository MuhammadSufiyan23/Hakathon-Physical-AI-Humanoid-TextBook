---
sidebar_label: 'Bipedal Locomotion and Walking Control'
title: 'Bipedal Locomotion and Walking Control'
---

# Bipedal Locomotion and Walking Control

## Introduction to Bipedal Locomotion

Bipedal locomotion is one of the most complex challenges in humanoid robotics, requiring sophisticated control strategies to maintain balance while achieving stable, efficient walking. Unlike wheeled robots, bipedal robots must manage underactuation, maintain balance during single-support phases, and coordinate complex multi-joint movements.

## Fundamentals of Humanoid Walking

### Walking Phases

Humanoid walking consists of distinct phases:

```
Single Support Phase (SSP)
├── Swing Foot: Moving through air
├── Stance Foot: Supporting robot weight
└── Control: Focus on balance and foot trajectory

Double Support Phase (DSP)
├── Both Feet: In contact with ground
├── Weight Transfer: Shift from one foot to other
└── Control: CoM trajectory adjustment
```

### Gait Parameters

Key parameters that define walking gait:

- **Step Length**: Forward distance between consecutive foot placements
- **Step Width**: Lateral distance between feet
- **Step Height**: Maximum foot lift during swing phase
- **Step Duration**: Time for complete step cycle
- **Stride Length**: Distance between same foot placements (2 steps)
- **Walking Speed**: Forward velocity achieved
- **Cadence**: Steps per minute

## Walking Pattern Generation

### Inverted Pendulum Models

#### Linear Inverted Pendulum Model (LIPM)

The Linear Inverted Pendulum Model simplifies humanoid walking dynamics:

```python
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class LinearInvertedPendulumModel:
    def __init__(self, com_height=0.85, gravity=9.81):
        self.com_height = com_height
        self.gravity = gravity
        self.omega = math.sqrt(gravity / com_height)

    def lipm_dynamics(self, t, state):
        """
        LIPM dynamics: ẍ_com = ω² * (x_com - x_zmp)

        State: [x_com, ẋ_com, y_com, ẏ_com]
        """
        x_com, xdot_com, y_com, ydot_com = state

        # Calculate current ZMP (simplified - would come from control)
        # In practice, this would be calculated from CoM and its derivatives
        x_zmp = 0.0  # This would be controlled by walking controller
        y_zmp = 0.0

        # LIPM equations of motion
        xddot_com = self.omega**2 * (x_com - x_zmp)
        yddot_com = self.omega**2 * (y_com - y_zmp)

        return [xdot_com, xddot_com, ydot_com, yddot_com]

    def simulate_walking_step(self, initial_com_state, step_length=0.3, step_duration=0.8):
        """
        Simulate one complete walking step.

        Args:
            initial_com_state: [x_com, ẋ_com, y_com, ẏ_com]
            step_length: Forward step length (m)
            step_duration: Duration of step (s)
        """
        # Time span for simulation
        t_span = (0, step_duration)
        t_eval = np.linspace(0, step_duration, int(step_duration * 100))  # 100 Hz sampling

        # Solve the differential equation
        solution = solve_ivp(
            self.lipm_dynamics,
            t_span,
            initial_com_state,
            t_eval=t_eval,
            method='RK45'
        )

        if solution.success:
            # Extract CoM trajectory
            com_trajectory = {
                'time': solution.t,
                'x_position': solution.y[0],
                'x_velocity': solution.y[1],
                'y_position': solution.y[2],
                'y_velocity': solution.y[3],
                'z_position': np.full_like(solution.t, self.com_height)  # Constant height
            }

            # Calculate corresponding ZMP trajectory
            zmp_trajectory = self.calculate_zmp_trajectory(com_trajectory)

            return com_trajectory, zmp_trajectory
        else:
            raise RuntimeError(f"LIPM simulation failed: {solution.message}")

    def calculate_zmp_trajectory(self, com_trajectory):
        """
        Calculate ZMP trajectory from CoM trajectory using LIPM relationship.

        ZMP = CoM - (h/g) * CoM_acceleration
        """
        zmp_x = com_trajectory['x_position'] - (
            self.com_height / self.gravity
        ) * np.gradient(com_trajectory['x_velocity'], com_trajectory['time'])

        zmp_y = com_trajectory['y_position'] - (
            self.com_height / self.gravity
        ) * np.gradient(com_trajectory['y_velocity'], com_trajectory['time'])

        return {
            'time': com_trajectory['time'],
            'x_position': zmp_x,
            'y_position': zmp_y
        }

    def generate_footstep_plan(self, n_steps=10, step_length=0.3, step_width=0.2):
        """
        Generate footstep plan for walking.

        Args:
            n_steps: Number of steps to generate
            step_length: Forward step length
            step_width: Lateral step width

        Returns:
            footstep_plan: List of footstep positions and timing
        """
        footstep_plan = []

        for i in range(n_steps):
            # Determine which foot is swing foot
            if i % 2 == 0:  # Even steps - right foot swings (assuming started with left stance)
                foot = 'right'
                x = (i + 1) * step_length
                y = -step_width / 2  # Right foot offset
            else:  # Odd steps - left foot swings
                foot = 'left'
                x = (i + 1) * step_length
                y = step_width / 2  # Left foot offset

            # Calculate timing
            step_start_time = i * step_duration
            step_end_time = (i + 1) * step_duration

            footstep_plan.append({
                'step_number': i,
                'foot': foot,
                'position': np.array([x, y, 0.0]),
                'timing': {
                    'lift_time': step_start_time,
                    'touchdown_time': step_end_time,
                    'support_switch_time': step_start_time + step_duration * 0.5
                },
                'support_foot': 'left' if foot == 'right' else 'right'
            })

        return footstep_plan

    def calculate_capture_point(self, com_pos, com_vel):
        """
        Calculate capture point - where to step to come to rest.

        Args:
            com_pos: [x, y] CoM position
            com_vel: [ẋ, ẏ] CoM velocity

        Returns:
            capture_point: [x, y] capture point position
        """
        capture_point_x = com_pos[0] + com_vel[0] / self.omega
        capture_point_y = com_pos[1] + com_vel[1] / self.omega

        return np.array([capture_point_x, capture_point_y])

    def is_step_stable(self, step_position, com_pos, com_vel):
        """
        Check if a step position will result in stable walking.

        Args:
            step_position: [x, y] proposed step position
            com_pos: [x, y] current CoM position
            com_vel: [ẋ, ẏ] current CoM velocity

        Returns:
            is_stable: Boolean indicating if step is stable
        """
        capture_point = self.calculate_capture_point(com_pos, com_vel)

        # For stability, step should be near the capture point
        distance_to_capture = np.linalg.norm(step_position[:2] - capture_point)

        # Define stability threshold (typically 5-10 cm)
        stability_threshold = 0.1  # 10cm

        return distance_to_capture < stability_threshold
```

### Walking Pattern Generation with Preview Control

```python
class PreviewController:
    def __init__(self, preview_horizon=20, dt=0.01):
        self.preview_horizon = preview_horizon
        self.dt = dt
        self.com_height = 0.85
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # State space representation for LIPM
        # x = [x_com, ẋ_com, y_com, ẏ_com]
        self.A = np.array([
            [1, self.dt, 0, 0],
            [self.omega**2 * self.dt**2, 1, 0, 0],
            [0, 0, 1, self.dt],
            [0, 0, self.omega**2 * self.dt**2, 1]
        ])

        self.B = np.array([
            [-self.omega**2 * self.dt**2 / 2, 0],
            [-self.omega**2 * self.dt, 0],
            [0, -self.omega**2 * self.dt**2 / 2],
            [0, -self.omega**2 * self.dt]
        ])

        # Cost function weights
        self.Q = np.diag([10.0, 1.0, 10.0, 1.0])  # State weights (CoM position more important)
        self.R = np.diag([0.1, 0.1])              # Control weights (ZMP control)

    def generate_preview_control(self, current_state, reference_trajectory):
        """
        Generate preview control for walking.

        Args:
            current_state: Current CoM state [x, ẋ, y, ẏ]
            reference_trajectory: Reference trajectory over preview horizon

        Returns:
            zmp_command: Next ZMP command
        """
        # Calculate LQR gain matrix (would be precomputed in practice)
        K = self.calculate_lqr_gain()

        # Calculate preview gain matrix
        F = self.calculate_preview_gain()

        # Calculate control command with preview
        zmp_command = -K @ current_state

        for k in range(self.preview_horizon):
            if k < len(reference_trajectory):
                ref_error = reference_trajectory[k] - current_state
                zmp_command += F[:, k] @ ref_error

        return zmp_command

    def calculate_lqr_gain(self):
        """
        Calculate LQR gain matrix for LIPM.
        """
        # This would solve the discrete-time algebraic Riccati equation
        # For this example, return a precomputed gain
        return np.array([[-3.1623, -4.4721, 0, 0], [0, 0, -3.1623, -4.4721]])

    def calculate_preview_gain(self):
        """
        Calculate preview gain matrix.
        """
        # This would be computed based on the system dynamics and cost function
        # For this example, return a simplified preview gain
        F = np.zeros((2, self.preview_horizon))
        for i in range(self.preview_horizon):
            F[0, i] = 0.1 * math.exp(-i * 0.1)  # Exponentially decaying preview
            F[1, i] = 0.1 * math.exp(-i * 0.1)
        return F

    def generate_com_trajectory(self, footsteps, initial_com_pos):
        """
        Generate CoM trajectory for walking using preview control.

        Args:
            footsteps: Planned footstep positions and timing
            initial_com_pos: Initial CoM position

        Returns:
            com_trajectory: CoM trajectory over time
        """
        com_trajectory = []
        current_state = np.array([initial_com_pos[0], 0.0, initial_com_pos[1], 0.0])  # [x, ẋ, y, ẏ]

        for i in range(len(footsteps)):
            # Get support polygon for this step
            support_polygon = self.calculate_support_polygon(footsteps, i)

            # Generate reference trajectory for preview horizon
            reference_trajectory = self.generate_reference_for_preview(footsteps, i)

            # Calculate ZMP command using preview control
            zmp_command = self.generate_preview_control(current_state, reference_trajectory)

            # Simulate one step
            step_trajectory = self.simulate_step(current_state, zmp_command, footsteps[i]['timing']['support_switch_time'])

            com_trajectory.extend(step_trajectory)

            # Update current state to end of step
            if step_trajectory:
                final_state = step_trajectory[-1]
                current_state = np.array([final_state['x'], final_state['xdot'], final_state['y'], final_state['ydot']])

        return com_trajectory

    def calculate_support_polygon(self, footsteps, step_idx):
        """
        Calculate support polygon for current step.

        Args:
            footsteps: Planned footstep sequence
            step_idx: Current step index

        Returns:
            polygon: Support polygon vertices
        """
        if step_idx == 0:
            # First step - use initial stance
            return np.array([[-0.1, -0.05], [0.1, -0.05], [0.1, 0.05], [-0.1, 0.05]])
        else:
            # Use current and previous foot positions
            current_foot = footsteps[step_idx]
            prev_foot = footsteps[step_idx - 1]

            if current_foot['foot'] == 'left':
                # Current foot is left, previous was right
                vertices = np.array([
                    [prev_foot['position'][0] - 0.1, prev_foot['position'][1] - 0.05],
                    [current_foot['position'][0] + 0.1, current_foot['position'][1] - 0.05],
                    [current_foot['position'][0] + 0.1, current_foot['position'][1] + 0.05],
                    [prev_foot['position'][0] - 0.1, prev_foot['position'][1] + 0.05]
                ])
            else:
                # Current foot is right, previous was left
                vertices = np.array([
                    [prev_foot['position'][0] - 0.1, prev_foot['position'][1] - 0.05],
                    [current_foot['position'][0] + 0.1, current_foot['position'][1] - 0.05],
                    [current_foot['position'][0] + 0.1, current_foot['position'][1] + 0.05],
                    [prev_foot['position'][0] - 0.1, prev_foot['position'][1] + 0.05]
                ])

            return vertices

    def generate_reference_for_preview(self, footsteps, step_idx):
        """
        Generate reference trajectory for preview control.
        """
        # This would generate a reference trajectory based on planned footsteps
        # For this example, return a simplified reference
        reference = []
        for i in range(self.preview_horizon):
            # Calculate reference based on upcoming footsteps
            future_idx = min(step_idx + i, len(footsteps) - 1)
            ref_pos = footsteps[future_idx]['position'][:2]  # x, y position
            reference.append(ref_pos)

        return np.array(reference)

    def simulate_step(self, initial_state, zmp_command, step_duration):
        """
        Simulate one walking step.

        Args:
            initial_state: Initial state [x, ẋ, y, ẏ]
            zmp_command: ZMP command for the step
            step_duration: Duration of the step

        Returns:
            step_trajectory: State trajectory for the step
        """
        trajectory = []
        state = initial_state.copy()

        n_points = int(step_duration / self.dt)

        for i in range(n_points):
            # Apply LIPM dynamics
            A = self.A
            B = self.B

            # Update state: x(k+1) = A*x(k) + B*u(k)
            new_state = A @ state + B @ zmp_command

            trajectory.append({
                'time': i * self.dt,
                'x': new_state[0],
                'xdot': new_state[1],
                'y': new_state[2],
                'ydot': new_state[3],
                'zmp_x': zmp_command[0],
                'zmp_y': zmp_command[1]
            })

            state = new_state

        return trajectory
```

## Walking Control Algorithms

### Footstep Planning

```python
class FootstepPlanner:
    def __init__(self):
        # Walking parameters
        self.step_length = 0.3
        self.step_width = 0.2
        self.step_height = 0.05
        self.step_duration = 0.8
        self.dsp_ratio = 0.2  # Double support phase ratio

        # Robot parameters
        self.com_height = 0.85
        self.foot_size = [0.2, 0.1]  # [length, width]

    def plan_walk_to_goal(self, start_pos, goal_pos, start_yaw=0.0):
        """
        Plan footstep sequence to walk from start to goal position.

        Args:
            start_pos: [x, y] starting position
            goal_pos: [x, y] goal position
            start_yaw: Starting orientation

        Returns:
            footsteps: List of planned footstep positions and timing
        """
        # Calculate distance and direction
        dx = goal_pos[0] - start_pos[0]
        dy = goal_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        direction = math.atan2(dy, dx)

        # Calculate number of steps needed
        n_steps = max(1, int(distance / self.step_length))

        # Generate footsteps
        footsteps = []
        current_x, current_y = start_pos
        current_yaw = start_yaw

        # Start with left foot support (robot will step with right first)
        support_foot = 'left'
        swing_foot = 'right'

        for i in range(n_steps):
            # Calculate step position
            step_x = current_x + self.step_length * math.cos(current_yaw)
            step_y = current_y + self.step_length * math.sin(current_yaw)

            # Add lateral offset based on swing foot
            lateral_offset = self.step_width / 2
            if swing_foot == 'left':
                step_y += lateral_offset
            else:  # right
                step_y -= lateral_offset

            # Calculate step orientation (may turn during step)
            step_yaw = current_yaw + (direction - current_yaw) * (i + 1) / n_steps

            # Create footstep
            footstep = {
                'step_number': i,
                'foot': swing_foot,
                'position': [step_x, step_y, 0.0],
                'orientation': step_yaw,
                'timing': {
                    'lift_time': i * self.step_duration,
                    'touchdown_time': (i + 1) * self.step_duration,
                    'dsp_start': i * self.step_duration,
                    'dsp_end': (i + self.dsp_ratio) * self.step_duration,
                    'ssp_start': (i + self.dsp_ratio) * self.step_duration,
                    'ssp_end': (i + 1 - self.dsp_ratio) * self.step_duration,
                    'final_dsp_start': (i + 1 - self.dsp_ratio) * self.step_duration,
                    'final_dsp_end': (i + 1) * self.step_duration
                },
                'support_foot': support_foot
            }

            footsteps.append(footstep)

            # Update for next step
            current_x, current_y = step_x, step_y
            current_yaw = step_yaw

            # Swap support and swing feet
            support_foot, swing_foot = swing_foot, support_foot

        return footsteps

    def plan_turning_steps(self, start_yaw, target_yaw, n_half_steps=4):
        """
        Plan footstep sequence for turning in place.

        Args:
            start_yaw: Starting orientation
            target_yaw: Target orientation
            n_half_steps: Number of half-steps (each full step is 2 half-steps)

        Returns:
            turning_steps: List of turning footstep positions
        """
        turning_steps = []
        angle_diff = target_yaw - start_yaw
        angle_per_half_step = angle_diff / n_half_steps

        # Start with feet in standard walking position
        left_foot_pos = np.array([0.0, self.step_width/2, 0.0])
        right_foot_pos = np.array([0.0, -self.step_width/2, 0.0])

        current_left_pos = left_foot_pos.copy()
        current_right_pos = right_foot_pos.copy()

        for i in range(n_half_steps):
            if i % 2 == 0:  # Left foot moves
                # Rotate left foot around robot center
                rotation_matrix = np.array([
                    [math.cos(angle_per_half_step), -math.sin(angle_per_half_step)],
                    [math.sin(angle_per_half_step), math.cos(angle_per_half_step)]
                ])
                new_pos = rotation_matrix @ current_left_pos[:2]
                current_left_pos[0:2] = new_pos
                swing_foot = 'left'
                support_foot = 'right'
            else:  # Right foot moves
                # Rotate right foot around robot center
                rotation_matrix = np.array([
                    [math.cos(angle_per_half_step), -math.sin(angle_per_half_step)],
                    [math.sin(angle_per_half_step), math.cos(angle_per_half_step)]
                ])
                new_pos = rotation_matrix @ current_right_pos[:2]
                current_right_pos[0:2] = new_pos
                swing_foot = 'right'
                support_foot = 'left'

            # Create footstep
            footstep = {
                'step_number': i,
                'foot': swing_foot,
                'position': current_left_pos if swing_foot == 'left' else current_right_pos,
                'orientation': start_yaw + (i + 1) * angle_per_half_step,
                'timing': {
                    'lift_time': i * self.step_duration / 2,
                    'touchdown_time': (i + 1) * self.step_duration / 2
                },
                'support_foot': support_foot
            }

            turning_steps.append(footstep)

        return turning_steps

    def plan_sidestepping(self, direction='left', n_steps=2):
        """
        Plan footstep sequence for sidestepping.

        Args:
            direction: 'left' or 'right' side step direction
            n_steps: Number of steps

        Returns:
            side_steps: List of sidestepping footstep positions
        """
        side_steps = []
        step_direction = 1.0 if direction == 'left' else -1.0

        for i in range(n_steps):
            # Alternate feet for sidestepping
            if i % 2 == 0:  # Even steps - move in specified direction
                foot = 'left' if step_direction > 0 else 'right'
            else:  # Odd steps - move back toward center
                foot = 'right' if step_direction > 0 else 'left'

            # Calculate step position
            step_y = (i + 1) * 0.1 * step_direction * (-1 if i % 2 == 1 else 1)

            footstep = {
                'step_number': i,
                'foot': foot,
                'position': [0.0, step_y, 0.0],
                'orientation': 0.0,
                'timing': {
                    'lift_time': i * self.step_duration,
                    'touchdown_time': (i + 1) * self.step_duration
                },
                'support_foot': 'right' if foot == 'left' else 'left'
            }

            side_steps.append(footstep)

        return side_steps

    def validate_footstep_plan(self, footsteps):
        """
        Validate footstep plan for stability and feasibility.

        Args:
            footsteps: Planned footstep sequence

        Returns:
            is_valid: Boolean indicating if plan is valid
            issues: List of validation issues
        """
        issues = []

        # Check for collision between feet
        for i in range(1, len(footsteps)):
            current_pos = np.array(footsteps[i]['position'][:2])
            previous_pos = np.array(footsteps[i-1]['position'][:2])

            distance = np.linalg.norm(current_pos - previous_pos)
            if distance < 0.1:  # Feet too close together
                issues.append(f"Step {i}: Feet too close ({distance:.2f}m), minimum should be 0.1m")

        # Check for step size feasibility
        for i in range(1, len(footsteps)):
            current_pos = np.array(footsteps[i]['position'][:2])
            previous_pos = np.array(footsteps[i-2]['position'][:2] if i >= 2 else footsteps[i-1]['position'][:2])

            step_size = np.linalg.norm(current_pos - previous_pos)
            if step_size > 0.5:  # Too large step
                issues.append(f"Step {i}: Step size too large ({step_size:.2f}m), maximum should be 0.5m")

        # Check for ZMP feasibility
        for i, footstep in enumerate(footsteps):
            zmp_pos = footstep['position'][:2]
            support_polygon = self.calculate_support_polygon(footsteps, i)

            if not self.is_zmp_in_support_polygon(zmp_pos, support_polygon):
                issues.append(f"Step {i}: ZMP outside support polygon")

        return len(issues) == 0, issues

    def calculate_support_polygon(self, footsteps, step_idx):
        """
        Calculate support polygon for given step.
        """
        if step_idx == 0:
            # Initial support polygon (both feet if starting from standing)
            return np.array([[-0.1, -0.1], [0.1, -0.1], [0.1, 0.1], [-0.1, 0.1]])
        else:
            # Use current and previous foot positions
            current_foot = footsteps[step_idx]
            prev_foot = footsteps[step_idx - 1]

            if current_foot['foot'] == 'left':
                # Left foot is swing foot, right foot is support
                support_pos = prev_foot['position'][:2]
                swing_pos = current_foot['position'][:2]
            else:
                # Right foot is swing foot, left foot is support
                support_pos = prev_foot['position'][:2]
                swing_pos = current_foot['position'][:2]

            # Create support polygon based on support foot position
            foot_size_x, foot_size_y = self.foot_size
            return np.array([
                [support_pos[0] - foot_size_x/2, support_pos[1] - foot_size_y/2],
                [support_pos[0] + foot_size_x/2, support_pos[1] - foot_size_y/2],
                [support_pos[0] + foot_size_x/2, support_pos[1] + foot_size_y/2],
                [support_pos[0] - foot_size_x/2, support_pos[1] + foot_size_y/2]
            ])

    def is_zmp_in_support_polygon(self, zmp_pos, support_polygon):
        """
        Check if ZMP is within support polygon using ray casting.
        """
        x, y = zmp_pos
        n = len(support_polygon)
        inside = False

        p1x, p1y = support_polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = support_polygon[i % n]
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

### Walking Pattern Execution

```python
class WalkingPatternExecutor:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.footstep_planner = FootstepPlanner()
        self.preview_controller = PreviewController()
        self.com_height = 0.85
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Walking state
        self.current_support_foot = 'left'
        self.swing_phase = 0.0
        self.step_count = 0
        self.current_step = 0
        self.step_trajectory = []
        self.foot_trajectories = {'left': [], 'right': []}

        # Control parameters
        self.kp_balance = 100.0
        self.kd_balance = 20.0
        self.kp_swing = 50.0
        self.kd_swing = 10.0

    def execute_walking_pattern(self, footstep_plan, control_frequency=100.0):
        """
        Execute walking pattern with real-time control.

        Args:
            footstep_plan: Planned footstep sequence
            control_frequency: Control frequency (Hz)
        """
        dt = 1.0 / control_frequency
        self.footstep_plan = footstep_plan

        # Initialize robot position
        self.initialize_walking_state(footstep_plan[0])

        for step_idx, footstep in enumerate(footstep_plan):
            self.current_step = step_idx
            self.execute_single_step(footstep, dt)

    def initialize_walking_state(self, first_footstep):
        """
        Initialize walking state with first footstep.
        """
        # Position robot at start position
        # This would involve setting joint angles to initial stance
        initial_com_pos = np.array([0.0, 0.0, self.com_height])
        initial_com_vel = np.array([0.0, 0.0, 0.0])

        # Position feet appropriately
        support_foot_pos = first_footstep['support_foot']
        swing_foot_pos = first_footstep['position']

        self.get_logger().info(f'Initialized walking state with support foot: {support_foot_pos}')

    def execute_single_step(self, footstep, dt):
        """
        Execute a single walking step.

        Args:
            footstep: Footstep information
            dt: Control time step
        """
        # Calculate step duration
        step_duration = footstep['timing']['touchdown_time'] - footstep['timing']['lift_time']
        n_steps = int(step_duration / dt)

        swing_foot = footstep['foot']
        support_foot = footstep['support_foot']
        target_position = footstep['position']

        for i in range(n_steps):
            current_time = footstep['timing']['lift_time'] + i * dt

            # Generate swing foot trajectory
            progress = i / n_steps
            swing_pos = self.generate_swing_trajectory(
                swing_foot, target_position, progress, current_time
            )

            # Generate balance control for support foot
            balance_torques = self.generate_balance_control(support_foot, current_time)

            # Execute control
            self.apply_walking_control(swing_pos, balance_torques, swing_foot)

            # Sleep for control timing
            time.sleep(dt)

        # Complete step - swap support feet
        self.current_support_foot = swing_foot

    def generate_swing_trajectory(self, foot, target_pos, progress, time):
        """
        Generate swing foot trajectory for current step.

        Args:
            foot: Foot name ('left' or 'right')
            target_pos: Target position for the foot
            progress: Progress in step (0.0 to 1.0)
            time: Current simulation time

        Returns:
            foot_pos: Current foot position
        """
        # Get current foot position
        current_pos = self.get_current_foot_position(foot)

        # Calculate swing trajectory using polynomial interpolation
        if 0.2 < progress < 0.8:  # Lift phase
            lift_progress = (progress - 0.2) / 0.6  # Normalize to 0-1 for lift phase

            # Horizontal interpolation
            x = current_pos[0] + progress * (target_pos[0] - current_pos[0])
            y = current_pos[1] + progress * (target_pos[1] - current_pos[1])

            # Vertical lift (sinusoidal)
            z = current_pos[2] + self.footstep_planner.step_height * math.sin(math.pi * lift_progress)
        else:  # Support phase
            # Linear interpolation for horizontal movement
            x = current_pos[0] + progress * (target_pos[0] - current_pos[0])
            y = current_pos[1] + progress * (target_pos[1] - current_pos[1])
            z = current_pos[2]  # Keep foot on ground

        # Add smooth transition
        smooth_progress = self.smooth_interpolation(progress)
        final_x = current_pos[0] + smooth_progress * (target_pos[0] - current_pos[0])
        final_y = current_pos[1] + smooth_progress * (target_pos[1] - current_pos[1])

        return np.array([final_x, final_y, z])

    def smooth_interpolation(self, t):
        """
        Smooth interpolation using quintic polynomial.
        """
        # Ensure t is between 0 and 1
        t = max(0.0, min(1.0, t))

        # Quintic polynomial for smooth motion (zero velocity and acceleration at start/end)
        return 6*t**5 - 15*t**4 + 10*t**3

    def get_current_foot_position(self, foot):
        """
        Get current foot position from forward kinematics.
        """
        # This would use the robot's forward kinematics to get foot position
        # For this example, return a placeholder
        if foot == 'left':
            return np.array([0.0, 0.1, 0.0])
        else:  # right
            return np.array([0.0, -0.1, 0.0)

    def generate_balance_control(self, support_foot, time):
        """
        Generate balance control for support foot phase.

        Args:
            support_foot: Current support foot ('left' or 'right')
            time: Current time

        Returns:
            balance_torques: Joint torques for balance control
        """
        # Calculate current CoM state
        current_com_pos, current_com_vel = self.estimate_com_state()
        current_com_acc = self.estimate_com_acceleration()

        # Calculate current ZMP
        current_zmp = self.calculate_zmp(current_com_pos, current_com_vel, current_com_acc)

        # Calculate desired ZMP based on support polygon
        support_polygon = self.calculate_support_polygon(support_foot)
        desired_zmp = self.calculate_desired_zmp(support_polygon, time)

        # Calculate ZMP error
        zmp_error = desired_zmp - current_zmp

        # Generate balance control torques using PID
        balance_torques = self.pid_balance_control(zmp_error)

        return balance_torques

    def estimate_com_state(self):
        """
        Estimate current center of mass position and velocity.
        """
        # This would use forward kinematics and link masses
        # For this example, return simplified estimate
        return np.array([0.0, 0.0, self.com_height]), np.array([0.0, 0.0, 0.0])

    def estimate_com_acceleration(self):
        """
        Estimate center of mass acceleration.
        """
        # This would use IMU data or numerical differentiation
        # For this example, return zero acceleration
        return np.array([0.0, 0.0, 0.0])

    def calculate_zmp(self, com_pos, com_vel, com_acc):
        """
        Calculate Zero Moment Point from CoM information.
        """
        zmp_x = com_pos[0] - (self.com_height / self.gravity) * com_acc[0]
        zmp_y = com_pos[1] - (self.com_height / self.gravity) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def calculate_support_polygon(self, support_foot):
        """
        Calculate current support polygon.
        """
        # This would use actual foot positions and contact information
        # For this example, return a simplified polygon
        if support_foot == 'left':
            return np.array([[-0.1, -0.05], [0.1, -0.05], [0.1, 0.05], [-0.1, 0.05]])
        else:  # right
            return np.array([[-0.1, -0.05], [0.1, -0.05], [0.1, 0.05], [-0.1, 0.05]])

    def calculate_desired_zmp(self, support_polygon, time):
        """
        Calculate desired ZMP position within support polygon.
        """
        # For walking, desired ZMP typically follows a trajectory
        # from previous support foot to current support foot
        if len(support_polygon) > 0:
            # Use center of support polygon as starting point
            center = np.mean(support_polygon, axis=0)
            return center
        else:
            return np.array([0.0, 0.0])

    def pid_balance_control(self, zmp_error):
        """
        PID control for balance based on ZMP error.
        """
        # Simple PID implementation for balance control
        # In reality, this would be much more complex involving whole-body control
        n_joints = self.robot.get_num_joints() if self.robot else 28
        torques = np.zeros(n_joints)

        # Apply proportional control to balance-critical joints
        balance_joints = {
            'left_ankle_pitch': 0.3,
            'left_ankle_roll': 0.2,
            'right_ankle_pitch': 0.3,
            'right_ankle_roll': 0.2,
            'left_hip_pitch': 0.1,
            'right_hip_pitch': 0.1,
            'left_hip_roll': 0.05,
            'right_hip_roll': 0.05
        }

        joint_names = self.robot.get_joint_names() if self.robot else [f'joint_{i}' for i in range(n_joints)]

        for joint_name, weight in balance_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply correction based on ZMP error
                    torques[joint_idx] = weight * self.kp_balance * (zmp_error[0] + zmp_error[1])

        return torques

    def apply_walking_control(self, swing_pos, balance_torques, swing_foot):
        """
        Apply walking control commands to robot.

        Args:
            swing_pos: Desired swing foot position
            balance_torques: Balance control torques
            swing_foot: Swing foot name
        """
        # This would send commands to the robot's joint controllers
        # In simulation, this would update the robot model
        # For this example, we'll just log the commands

        self.get_logger().debug(f'Swing foot {swing_foot} to position: {swing_pos}')

        # In a real implementation, this would:
        # 1. Send position commands to swing foot joints
        # 2. Send balance torques to support foot joints
        # 3. Coordinate with CoM trajectory following
        pass

    def execute_turning_pattern(self, turning_steps, turn_speed=0.5):
        """
        Execute turning pattern.

        Args:
            turning_steps: Turning footstep sequence
            turn_speed: Turning speed factor
        """
        # Similar to walking but with rotational components
        for step in turning_steps:
            # Execute turn step
            self.execute_single_turn_step(step, turn_speed)

    def execute_single_turn_step(self, step, turn_speed):
        """
        Execute a single turning step.
        """
        # Calculate turning trajectory
        # Apply turning-specific balance control
        pass

    def execute_sidestepping_pattern(self, side_steps):
        """
        Execute sidestepping pattern.
        """
        for step in side_steps:
            # Execute side step
            self.execute_single_side_step(step)

    def execute_single_side_step(self, step):
        """
        Execute a single sidestep.
        """
        # Calculate side step trajectory
        # Apply side step-specific balance control
        pass
```

## Advanced Walking Control

### Capture Point-Based Walking Control

```python
class CapturePointWalkingController:
    def __init__(self, com_height=0.85, gravity=9.81):
        self.com_height = com_height
        self.gravity = gravity
        self.omega = math.sqrt(gravity / com_height)

        # Walking parameters
        self.step_duration = 0.8
        self.step_height = 0.05
        self.step_width = 0.2
        self.step_length = 0.3

        # Capture point control parameters
        self.cp_kp = 5.0
        self.cp_kd = 2.0
        self.zmp_margin = 0.05  # Safety margin for ZMP

        # Walking state
        self.current_support_foot = 'left'
        self.swing_foot = 'right'
        self.cp_trajectory = []
        self.zmp_trajectory = []

    def calculate_capture_point(self, com_pos, com_vel):
        """
        Calculate capture point where robot needs to step to come to rest.

        Args:
            com_pos: [x, y] center of mass position
            com_vel: [ẋ, ẏ] center of mass velocity

        Returns:
            capture_point: [x, y] capture point position
        """
        cp_x = com_pos[0] + com_vel[0] / self.omega
        cp_y = com_pos[1] + com_vel[1] / self.omega

        return np.array([cp_x, cp_y])

    def plan_capture_point_trajectory(self, start_pos, goal_pos, n_steps):
        """
        Plan capture point trajectory for walking.

        Args:
            start_pos: Starting position
            goal_pos: Goal position
            n_steps: Number of steps

        Returns:
            cp_trajectory: Planned capture point trajectory
        """
        cp_trajectory = []

        # For walking, the capture point should move from current CoM position
        # toward the goal position in a controlled manner
        for i in range(n_steps):
            # Calculate progress along trajectory
            progress = (i + 1) / n_steps

            # Interpolate between start and goal
            target_x = start_pos[0] + progress * (goal_pos[0] - start_pos[0])
            target_y = start_pos[1] + progress * (goal_pos[1] - start_pos[1])

            # Add some stability margin - keep capture point slightly ahead of CoM
            stability_margin = 0.05  # 5cm stability margin
            cp_x = target_x - stability_margin * math.cos(math.atan2(goal_pos[1] - start_pos[1], goal_pos[0] - start_pos[0]))
            cp_y = target_y - stability_margin * math.sin(math.atan2(goal_pos[1] - start_pos[1], goal_pos[0] - start_pos[0]))

            cp_trajectory.append(np.array([cp_x, cp_y]))

        return cp_trajectory

    def generate_step_location_from_capture_point(self, capture_point, support_foot_pos):
        """
        Generate appropriate step location based on capture point.

        Args:
            capture_point: [x, y] capture point position
            support_foot_pos: [x, y] current support foot position

        Returns:
            step_location: [x, y] recommended step location
        """
        # The step should be placed to move the capture point toward stability
        # This is a simplified approach - real implementation would be more complex

        # Calculate vector from support foot to capture point
        cp_to_foot = capture_point - support_foot_pos[:2]

        # Step should be in direction of capture point but with safety considerations
        step_direction = cp_to_foot / (np.linalg.norm(cp_to_foot) + 1e-6)  # Normalize

        # Calculate step distance (don't step too far or too close)
        step_distance = min(0.4, max(0.1, np.linalg.norm(cp_to_foot)))

        # Calculate step location
        step_x = support_foot_pos[0] + step_distance * step_direction[0]
        step_y = support_foot_pos[1] + step_distance * step_direction[1]

        # Apply foot placement constraints
        if self.current_support_foot == 'left':
            # Right foot should be placed with appropriate lateral offset
            step_y = min(support_foot_pos[1] - 0.15, step_y)  # Don't cross over
        else:  # right support
            # Left foot should be placed with appropriate lateral offset
            step_y = max(support_foot_pos[1] + 0.15, step_y)  # Don't cross over

        return np.array([step_x, step_y])

    def execute_capture_point_control(self, current_com_pos, current_com_vel,
                                     support_foot_pos, target_position):
        """
        Execute walking control based on capture point.

        Args:
            current_com_pos: Current CoM position
            current_com_vel: Current CoM velocity
            support_foot_pos: Current support foot position
            target_position: Walking target position

        Returns:
            step_location: Recommended next step location
            balance_correction: Balance correction torques
        """
        # Calculate current capture point
        current_cp = self.calculate_capture_point(current_com_pos[:2], current_com_vel[:2])

        # Determine where next step should be placed
        next_step_location = self.generate_step_location_from_capture_point(
            current_cp, support_foot_pos
        )

        # Calculate desired ZMP to move capture point toward next foot placement
        desired_zmp = self.calculate_desired_zmp_for_stability(
            next_step_location, current_com_pos[:2], current_com_vel[:2]
        )

        # Calculate balance correction
        balance_correction = self.calculate_balance_correction(
            current_com_pos, current_com_vel, desired_zmp
        )

        # Log for visualization/debugging
        self.cp_trajectory.append(current_cp)
        self.zmp_trajectory.append(desired_zmp)

        return next_step_location, balance_correction

    def calculate_desired_zmp_for_stability(self, next_step_pos, com_pos, com_vel):
        """
        Calculate desired ZMP to achieve stable walking toward next step.

        Args:
            next_step_pos: Position of next foot placement
            com_pos: Current CoM position
            com_vel: Current CoM velocity

        Returns:
            desired_zmp: Desired ZMP position
        """
        # For stable walking, ZMP should be positioned to move capture point
        # toward the next foot placement location

        # Calculate the ZMP that would move the capture point toward the next step
        # This uses the relationship: cp_next = com_pos + com_vel/ω + (step_pos - com_pos) * exp(-ω*dt)
        # Rearranging for ZMP control: we want the CoM to move in a way that the
        # capture point ends up near the next step location

        # Simplified approach: ZMP should be positioned to move CoM appropriately
        # toward the next step location
        desired_zmp = next_step_pos - 0.05  # Small offset toward next step

        return desired_zmp

    def calculate_balance_correction(self, com_pos, com_vel, desired_zmp):
        """
        Calculate balance correction torques using ZMP feedback.

        Args:
            com_pos: Current CoM position
            com_vel: Current CoM velocity
            desired_zmp: Desired ZMP position

        Returns:
            balance_torques: Joint torques for balance correction
        """
        # Calculate current ZMP
        current_zmp = self.calculate_current_zmp(com_pos, com_vel)

        # Calculate ZMP error
        zmp_error = desired_zmp - current_zmp[:2]

        # PID control for balance
        kp = self.cp_kp
        kd = self.cp_kd

        # Proportional term
        p_term = kp * zmp_error

        # Derivative term (based on CoM velocity)
        d_term = kd * com_vel[:2]

        # Combine terms
        correction_command = p_term + d_term

        # Map to joint torques (simplified mapping)
        n_joints = 28  # Example humanoid DOF
        balance_torques = np.zeros(n_joints)

        # Distribute correction to balance-critical joints
        balance_joints = {
            'left_ankle_pitch': 0.3,
            'left_ankle_roll': 0.2,
            'right_ankle_pitch': 0.3,
            'right_ankle_roll': 0.2,
            'left_hip_pitch': 0.1,
            'right_hip_pitch': 0.1,
            'left_hip_roll': 0.05,
            'right_hip_roll': 0.05
        }

        joint_names = [f'joint_{i}' for i in range(n_joints)]  # Placeholder

        for joint_name, weight in balance_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply correction based on direction
                    balance_torques[joint_idx] = weight * (correction_command[0] + correction_command[1])

        return balance_torques

    def calculate_current_zmp(self, com_pos, com_vel):
        """
        Calculate current ZMP from CoM information.
        This would typically use IMU data in practice.
        """
        # Simplified calculation - in reality, this would use force/torque sensors
        # or IMU data to calculate actual ZMP
        return com_pos[:2]  # Placeholder

    def adapt_walking_parameters(self, terrain_type='flat'):
        """
        Adapt walking parameters based on terrain type.

        Args:
            terrain_type: Type of terrain ('flat', 'rough', 'slippery', 'stairs', etc.)
        """
        if terrain_type == 'rough':
            # Reduce step length and height for stability
            self.step_length = 0.2
            self.step_height = 0.08
            self.step_duration = 1.0
        elif terrain_type == 'slippery':
            # Reduce step length and increase double support
            self.step_length = 0.2
            self.dsp_ratio = 0.3
        elif terrain_type == 'stairs':
            # Adapt for stair climbing
            self.step_height = 0.15  # Higher steps
            self.step_length = 0.2   # Shorter steps
            self.step_duration = 1.2  # Slower
        else:  # flat terrain
            # Restore normal parameters
            self.step_length = 0.3
            self.step_height = 0.05
            self.step_duration = 0.8
            self.dsp_ratio = 0.2

        self.get_logger().info(f'Walking parameters adapted for {terrain_type} terrain')

    def check_walking_stability(self, current_zmp, support_polygon):
        """
        Check if current walking state is stable.

        Args:
            current_zmp: Current ZMP position
            support_polygon: Current support polygon

        Returns:
            is_stable: Boolean indicating if walking is stable
            stability_margin: Distance from ZMP to polygon boundary
        """
        if len(support_polygon) < 3:
            return False, 0.0

        # Check if ZMP is inside support polygon
        is_inside = self.is_point_in_polygon(current_zmp[:2], support_polygon)

        if not is_inside:
            return False, 0.0

        # Calculate distance to nearest boundary (simplified)
        min_distance = float('inf')
        for i in range(len(support_polygon)):
            p1 = support_polygon[i]
            p2 = support_polygon[(i + 1) % len(support_polygon)]

            # Calculate distance from ZMP to edge
            distance = self.point_to_line_distance(current_zmp[:2], p1[:2], p2[:2])
            min_distance = min(min_distance, distance)

        return True, min_distance

    def is_point_in_polygon(self, point, polygon):
        """
        Check if point is inside polygon using ray casting algorithm.
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0][0], polygon[0][1]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n][0], polygon[i % n][1]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def point_to_line_distance(self, point, line_start, line_end):
        """
        Calculate distance from point to line segment.
        """
        # Convert to numpy arrays
        point = np.array(point)
        line_start = np.array(line_start)
        line_end = np.array(line_end)

        # Vector from line start to end
        line_vec = line_end - line_start
        point_vec = point - line_start

        # Calculate line length squared
        line_len_sq = np.dot(line_vec, line_vec)

        if line_len_sq == 0:  # Line is actually a point
            return np.linalg.norm(point - line_start)

        # Calculate projection of point_vec onto line_vec
        t = max(0, min(1, np.dot(point_vec, line_vec) / line_len_sq))

        # Calculate projection point
        projection = line_start + t * line_vec

        # Calculate distance to projection
        distance = np.linalg.norm(point - projection)
        return distance

    def handle_terrain_changes(self, terrain_data):
        """
        Handle terrain changes during walking.

        Args:
            terrain_data: Information about current terrain
        """
        terrain_type = terrain_data.get('type', 'flat')
        slope = terrain_data.get('slope', 0.0)
        friction = terrain_data.get('friction', 1.0)

        # Adapt walking parameters based on terrain
        self.adapt_walking_parameters(terrain_type)

        # If significant slope, adjust CoM position
        if abs(slope) > 0.1:  # 10% slope
            self.adjust_com_for_slope(slope)

        # If low friction, reduce walking speed
        if friction < 0.5:
            self.reduce_walking_speed()

    def adjust_com_for_slope(self, slope):
        """
        Adjust CoM position for walking on slopes.
        """
        # Move CoM forward/backward based on slope
        # Forward on uphill, backward on downhill
        com_adjustment = slope * 0.1  # 10cm per 10% slope
        self.get_logger().info(f'Adjusting CoM for slope: {slope:.2f}, adjustment: {com_adjustment:.3f}')

    def reduce_walking_speed(self):
        """
        Reduce walking speed for safety.
        """
        self.step_length *= 0.8  # Reduce step length
        self.step_duration *= 1.2  # Increase step duration
        self.get_logger().info('Reducing walking speed for safety')
```

## Summary

Bipedal locomotion for humanoid robots requires sophisticated control strategies that integrate multiple approaches:

1. **Dynamic Models**: LIPM and other simplified models for real-time control
2. **Balance Control**: ZMP-based control for maintaining stability
3. **Gait Generation**: Step timing and trajectory planning
4. **Adaptive Control**: Terrain adaptation and parameter tuning
5. **Whole-Body Coordination**: Integration of arms, torso, and legs for stable walking
6. **Prediction and Planning**: Capture point and preview control methods

These systems enable humanoid robots to achieve stable, efficient walking that can be adapted to various terrains and conditions, making them suitable for real-world deployment in human environments.