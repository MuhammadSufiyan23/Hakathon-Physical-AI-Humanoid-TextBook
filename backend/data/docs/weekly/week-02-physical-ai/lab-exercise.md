---
sidebar_label: 'Week 2 Lab Exercise: Embodied Intelligence and Applications'
title: 'Week 2 Lab Exercise: Embodied Intelligence and Applications'
---

# Week 2 Lab Exercise: Embodied Intelligence and Applications

## Objective

In this lab exercise, you will explore the principles of embodied intelligence by implementing and experimenting with a simple embodied agent. You will also investigate real-world applications of Physical AI and humanoid robotics. This exercise will help you understand how physical form and environmental interaction contribute to intelligent behavior.

## Prerequisites

- Python 3.8 or higher
- NumPy library
- Matplotlib library
- Basic understanding of object-oriented programming

## Part 1: Implementing an Embodied Agent

### Task 1.1: Extend the Basic Embodied Agent

Building on the example from the chapter, implement additional behaviors for your embodied agent:

1. Implement a "curiosity" behavior that drives the agent to explore unknown areas
2. Add a "conservation" behavior that makes the agent seek energy sources when energy is low
3. Implement obstacle avoidance with memory (the agent remembers locations of obstacles)

### Task 1.2: Environmental Interaction

Create a more complex environment with multiple types of objects:

1. Food sources that replenish the agent's energy
2. Charging stations that restore energy more efficiently
3. Hazards that reduce energy when approached
4. Information sources that provide knowledge about distant parts of the environment

### Task 1.3: Behavior Emergence

Experiment with simple rules that can lead to complex behaviors:

1. Implement a "herding" behavior where multiple agents follow each other
2. Create a "foraging" pattern where agents learn to efficiently find and collect resources
3. Implement a simple learning mechanism where the agent improves its behavior over time

## Part 2: Application Simulation

### Task 2.1: Healthcare Application

Simulate a healthcare application where a robot assists an elderly person:

1. Model the physical environment of a home (rooms, furniture, obstacles)
2. Implement the robot's assistance behaviors (reminders, monitoring, emergency response)
3. Simulate the human's daily routine and needs
4. Evaluate the effectiveness of the robot's assistance

### Task 2.2: Manufacturing Application

Simulate a manufacturing scenario with collaborative robots:

1. Model an assembly line with different workstations
2. Implement robots with different capabilities (some for heavy lifting, others for precision work)
3. Simulate human workers and their interaction with robots
4. Optimize the workflow to maximize efficiency and safety

### Task 2.3: Application Comparison

Compare different approaches to the same problem:

1. A purely computational solution (no embodiment)
2. A simple embodied solution
3. A complex embodied solution with environmental interaction

Analyze the differences in performance, efficiency, and adaptability.

## Implementation Template

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
from enum import Enum
import random

class AgentState(Enum):
    EXPLORING = "exploring"
    FORAGING = "foraging"
    RESTING = "resting"
    AVOIDING = "avoiding"
    SEEKING_ENERGY = "seeking_energy"

class EnvironmentObject:
    def __init__(self, obj_type: str, position: np.ndarray, properties: Dict = None):
        self.type = obj_type  # 'food', 'obstacle', 'charger', 'hazard', 'info'
        self.position = position
        self.properties = properties or {}
        self.active = True

class EmbodiedAgent:
    def __init__(self, position: np.ndarray, energy: float = 100.0):
        self.position = np.array(position, dtype=float)
        self.energy = energy
        self.state = AgentState.EXPLORING
        self.perceptual_range = 5.0
        self.memory = {}  # Remembered locations and properties
        self.history = [self.position.copy()]
        self.known_objects = []  # Objects discovered in the environment

    def sense_environment(self, environment_objects: List[EnvironmentObject]) -> List[Dict]:
        """Sense nearby objects within perceptual range"""
        sensed = []
        for obj in environment_objects:
            if not obj.active:
                continue
            distance = np.linalg.norm(self.position - obj.position)
            if distance <= self.perceptual_range:
                relative_pos = obj.position - self.position
                angle = np.arctan2(relative_pos[1], relative_pos[0])
                sensed.append({
                    'type': obj.type,
                    'distance': distance,
                    'angle': angle,
                    'position': obj.position.copy(),
                    'properties': obj.properties
                })
        return sensed

    def update_state(self, sensed_objects: List[Dict]):
        """Update agent state based on sensed environment"""
        # Implement state transition logic based on sensed objects and energy level
        food_nearby = any(obj['type'] == 'food' and obj['distance'] < 2.0 for obj in sensed_objects)
        energy_low = self.energy < 30
        hazard_nearby = any(obj['type'] == 'hazard' and obj['distance'] < 3.0 for obj in sensed_objects)

        if hazard_nearby:
            self.state = AgentState.AVOIDING
        elif energy_low and not food_nearby:
            self.state = AgentState.SEEKING_ENERGY
        elif food_nearby:
            self.state = AgentState.FORAGING
        else:
            self.state = AgentState.EXPLORING

    def execute_behavior(self, environment_objects: List[EnvironmentObject], dt: float = 0.1):
        """Execute behavior based on current state"""
        sensed = self.sense_environment(environment_objects)
        self.update_state(sensed)

        if self.state == AgentState.AVOIDING:
            self.avoid_hazards(sensed)
        elif self.state == AgentState.SEEKING_ENERGY:
            self.seek_energy_source(sensed)
        elif self.state == AgentState.FORAGING:
            self.collect_resources(sensed)
        elif self.state == AgentState.EXPLORING:
            self.explore(sensed)

        # Energy consumption
        self.energy -= dt * 0.5  # Base energy consumption

    def avoid_hazards(self, sensed_objects: List[Dict]):
        """Move away from hazards"""
        hazards = [obj for obj in sensed_objects if obj['type'] == 'hazard']
        if hazards:
            closest_hazard = min(hazards, key=lambda x: x['distance'])
            # Move away from hazard
            angle = closest_hazard['angle']
            avoidance_direction = angle + np.pi  # Opposite direction
            self.position[0] += 0.5 * np.cos(avoidance_direction)
            self.position[1] += 0.5 * np.sin(avoidance_direction)

    def seek_energy_source(self, sensed_objects: List[Dict]):
        """Move towards energy sources"""
        energy_sources = [obj for obj in sensed_objects if obj['type'] in ['food', 'charger']]
        if energy_sources:
            closest = min(energy_sources, key=lambda x: x['distance'])
            direction_to = closest['angle']
            self.position[0] += 0.3 * np.cos(direction_to)
            self.position[1] += 0.3 * np.sin(direction_to)
        else:
            # Random walk if no known energy source
            random_angle = random.uniform(0, 2 * np.pi)
            self.position[0] += 0.2 * np.cos(random_angle)
            self.position[1] += 0.2 * np.sin(random_angle)

    def collect_resources(self, sensed_objects: List[Dict]):
        """Collect nearby resources"""
        food = [obj for obj in sensed_objects if obj['type'] == 'food' and obj['distance'] < 0.5]
        if food:
            # Consume food to gain energy
            self.energy += food[0]['properties'].get('energy_value', 10)
            # Mark food as consumed (in real implementation, remove from environment)
        else:
            # Move toward closest food
            food_all = [obj for obj in sensed_objects if obj['type'] == 'food']
            if food_all:
                closest = min(food_all, key=lambda x: x['distance'])
                direction_to = closest['angle']
                self.position[0] += 0.4 * np.cos(direction_to)
                self.position[1] += 0.4 * np.sin(direction_to)

    def explore(self, sensed_objects: List[Dict]):
        """Explore the environment"""
        # Simple exploration behavior
        random_angle = random.uniform(0, 2 * np.pi)
        self.position[0] += 0.3 * np.cos(random_angle)
        self.position[1] += 0.3 * np.sin(random_angle)

def create_healthcare_environment():
    """Create an environment simulating a home for elderly care"""
    objects = [
        EnvironmentObject('bed', np.array([2, 2]), {'function': 'rest'}),
        EnvironmentObject('kitchen', np.array([8, 3]), {'function': 'meal_preparation'}),
        EnvironmentObject('medication', np.array([5, 1]), {'function': 'medicine'}),
        EnvironmentObject('bathroom', np.array([1, 6]), {'function': 'hygiene'}),
        EnvironmentObject('sofa', np.array([6, 6]), {'function': 'sitting'}),
        EnvironmentObject('obstacle', np.array([4, 4]), {'type': 'table'}),
    ]
    return objects

def simulate_healthcare_application():
    """Simulate a healthcare application with robot assistance"""
    environment = create_healthcare_environment()
    agent = EmbodiedAgent(position=np.array([5, 5]), energy=100.0)

    # Simulate a day of activities
    for t in range(1000):  # 1000 time steps
        if agent.energy <= 0:
            print(f"Agent ran out of energy at time step {t}")
            break

        agent.execute_behavior(environment)

        # Add some random events (medication time, meal time, etc.)
        if t % 200 == 0:  # Every 200 steps, add an event
            event_obj = EnvironmentObject('medicine_reminder',
                                         np.array([random.uniform(0, 10), random.uniform(0, 8)])
            )
            environment.append(event_obj)

        # Record position periodically
        if t % 10 == 0:
            agent.history.append(agent.position.copy())

    return agent, environment

def main():
    print("Embodied Intelligence Lab Exercise - Week 2")

    # Run the healthcare simulation
    agent, environment = simulate_healthcare_application()

    print(f"Final agent position: {agent.position}")
    print(f"Final energy level: {agent.energy:.2f}")
    print(f"Path length: {len(agent.history)} steps")

    # Visualize the agent's path
    if agent.history:
        path = np.array(agent.history)
        plt.figure(figsize=(12, 8))

        # Plot path
        plt.plot(path[:, 0], path[:, 1], 'b-', linewidth=1, label='Agent Path', alpha=0.7)
        plt.scatter(path[0, 0], path[0, 1], color='green', s=100, label='Start', zorder=5)
        plt.scatter(path[-1, 0], path[-1, 1], color='red', s=100, label='End', zorder=5)

        # Plot environment objects
        for obj in environment:
            if obj.type == 'bed':
                plt.scatter(obj.position[0], obj.position[1], color='blue', s=100, marker='s', label='Bed' if obj == environment[0] else "")
            elif obj.type == 'kitchen':
                plt.scatter(obj.position[0], obj.position[1], color='orange', s=100, marker='^', label='Kitchen' if obj == environment[1] else "")
            elif obj.type == 'medication':
                plt.scatter(obj.position[0], obj.position[1], color='purple', s=100, marker='D', label='Medication' if obj == environment[2] else "")
            else:
                plt.scatter(obj.position[0], obj.position[1], color='gray', s=80, marker='X', label='Other' if obj == environment[5] else "")

        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.title('Embodied Agent Path in Healthcare Environment')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    main()
```

## Part 3: Analysis and Reflection

### Task 3.1: Compare Approaches

Implement the same problem using:
1. A purely computational approach (no physical embodiment)
2. A simple embodied approach
3. A complex embodied approach with environmental interaction

Compare the effectiveness of each approach in terms of:
- Efficiency
- Adaptability to changing conditions
- Robustness to unexpected situations

### Task 3.2: Real-World Applications

Research and analyze three real-world applications of humanoid robots or Physical AI systems. For each application:
1. Describe the system and its purpose
2. Identify how embodiment contributes to its effectiveness
3. Discuss challenges and limitations
4. Propose potential improvements

## Deliverables

1. **Code Implementation**: Complete implementation of the embodied agent with all required behaviors
2. **Simulation Results**: Visualization and analysis of agent behavior in different environments
3. **Application Analysis**: Comparison of different approaches to the same problem
4. **Real-World Research**: Analysis of three real-world applications
5. **Reflection Report**: A written report (2-3 pages) that includes:
   - Summary of implemented behaviors and their effectiveness
   - Comparison of different approaches
   - Discussion of how embodiment affects performance
   - Analysis of real-world applications
   - Challenges encountered and lessons learned

## Evaluation Criteria

- Correct implementation of embodied agent behaviors (25%)
- Quality of simulation and visualization (20%)
- Thoroughness of approach comparison (25%)
- Depth of real-world application analysis (20%)
- Quality of reflection and insights (10%)

## Time Estimate

This lab exercise should take approximately 4-5 hours to complete, including implementation, experimentation, research, and report writing.

## Extension Challenges (Optional)

1. Implement machine learning techniques for the agent to improve its behavior over time
2. Create a multi-agent system with cooperation or competition
3. Implement a more realistic physics simulation
4. Add a graphical user interface for real-time interaction
5. Research and implement a specific real-world application in detail