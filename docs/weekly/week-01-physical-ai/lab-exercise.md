---
sidebar_label: 'Week 1 Lab Exercise: Physical AI Foundations'
title: 'Week 1 Lab Exercise: Physical AI Foundations'
---

# Week 1 Lab Exercise: Physical AI Foundations

## Objective

In this lab exercise, you will explore the fundamental concepts of Physical AI by implementing a simple physics simulator and experimenting with sensor data processing. This exercise will help you understand the differences between digital AI and Physical AI systems.

## Prerequisites

- Python 3.8 or higher
- NumPy library
- Basic understanding of physics concepts (Newton's laws, energy conservation)

## Part 1: Physics Simulation

### Task 1.1: Implement a Basic Physics Simulator

Create a Python class that simulates basic physical phenomena. Your simulator should include:

1. Free fall calculations using gravitational acceleration
2. Kinetic and potential energy calculations
3. Momentum calculations

### Task 1.2: Experiment with Parameters

Run your simulator with different parameters and observe the results:
- Vary the mass of objects (0.1kg to 100kg)
- Vary initial conditions (heights, velocities)
- Compare results with and without air resistance (bonus challenge)

### Task 1.3: Analyze Results

Document your observations about how changing parameters affects the physical behavior of your simulated objects.

## Part 2: Sensor Data Processing

### Task 2.1: LIDAR Simulation

Create a function that simulates LIDAR data for a simple environment:
- Define a 2D space with obstacles
- Simulate LIDAR beams in different directions
- Detect obstacles and return distance measurements

### Task 2.2: IMU Data Integration

Implement a simple IMU data integration to estimate position:
- Start with known initial position and velocity
- Simulate accelerometer and gyroscope readings
- Integrate these readings to estimate current position
- Compare with actual position to assess accuracy

### Task 2.3: Sensor Fusion

Combine the LIDAR and IMU data to create a more complete picture of the environment and robot state.

## Implementation Template

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

class PhysicsSimulator:
    def __init__(self):
        self.gravity = 9.81  # m/s^2

    def free_fall_position(self, initial_height: float, time: float) -> float:
        """Calculate position of an object in free fall"""
        # Your implementation here
        pass

    def kinetic_energy(self, mass: float, velocity: float) -> float:
        """Calculate kinetic energy"""
        # Your implementation here
        pass

    def potential_energy(self, mass: float, height: float) -> float:
        """Calculate potential energy"""
        # Your implementation here
        pass

class LIDARSimulator:
    def __init__(self, max_range: float = 10.0):
        self.max_range = max_range

    def simulate_scan(self, robot_pos: Tuple[float, float],
                     environment_obstacles: List[Tuple[float, float, float]]) -> List[float]:
        """Simulate LIDAR scan in a 2D environment"""
        # Your implementation here
        pass

class IMUIntegrator:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.velocity = np.array([0.0, 0.0, 0.0])

    def integrate_step(self, accel: np.ndarray, gyro: np.ndarray, dt: float):
        """Integrate IMU readings to update position and orientation"""
        # Your implementation here
        pass

def main():
    # Initialize simulators
    physics_sim = PhysicsSimulator()
    lidar_sim = LIDARSimulator()
    imu_integrator = IMUIntegrator()

    # Run your experiments here
    print("Physical AI Lab Exercise - Week 1")

    # Example: Calculate free fall
    height = physics_sim.free_fall_position(10.0, 1.5)
    print(f"Object position after 1.5s: {height:.2f}m")

if __name__ == "__main__":
    main()
```

## Deliverables

1. **Code Implementation**: Complete implementation of the physics simulator and sensor processing functions
2. **Analysis Report**: A written report (1-2 pages) that includes:
   - Description of your implementation approach
   - Results from your parameter experiments
   - Discussion of the differences between digital and physical AI systems
   - Challenges encountered and how you addressed them
3. **Visualizations**: Plots showing your simulation results (optional but recommended)

## Evaluation Criteria

- Correct implementation of physics calculations (25%)
- Proper sensor simulation and data processing (25%)
- Quality of analysis and understanding demonstrated (30%)
- Code quality and documentation (20%)

## Time Estimate

This lab exercise should take approximately 3-4 hours to complete, including implementation, experimentation, and report writing.

## Extension Challenges (Optional)

1. Implement air resistance in your physics simulator
2. Add noise to your simulated sensor data to make it more realistic
3. Implement a Kalman filter for sensor fusion
4. Create a visualization of your simulated robot moving in the environment