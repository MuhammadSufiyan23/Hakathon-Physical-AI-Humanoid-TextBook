---
sidebar_label: 'Week 12 Quiz: Humanoid Control Systems'
title: 'Week 12 Quiz: Humanoid Control Systems'
---

# Week 12 Quiz: Humanoid Control Systems

## Question 1
What does ZMP stand for in humanoid robotics?
- A) Zero Motion Point
- B) Zero Moment Point
- C) Zero Momentum Point
- D) Zero Mass Point

## Question 2
In the Linear Inverted Pendulum Model (LIPM), which parameter remains constant?
- A) Robot's angular momentum
- B) Center of mass height
- C) Robot's total energy
- D) Joint angles

## Question 3
What is the primary purpose of operational space control in humanoid robots?
- A) To control joint positions only
- B) To control task-space variables while considering robot dynamics
- C) To reduce computational requirements
- D) To eliminate the need for sensors

## Question 4
Which control approach is most appropriate for maintaining balance during walking?
- A) Joint position control only
- B) ZMP-based control
- C) Open-loop control
- D) Feedforward control only

## Question 5
What is the "capture point" in humanoid locomotion?
- A) The point where the robot captures objects
- B) The point where the robot needs to step to come to rest
- C) The center of the support polygon
- D) The location of the ZMP

## Question 6
In ros2_control, what is a "hardware interface"?
- A) The physical robot hardware
- B) The software abstraction layer that defines how to communicate with hardware
- C) The simulation environment
- D) The control algorithm

## Question 7
Which sensor is most critical for real-time balance control?
- A) Camera
- B) LIDAR
- C) IMU (Inertial Measurement Unit)
- D) Force/Torque sensors

## Question 8
What does the "support polygon" represent in humanoid robotics?
- A) The robot's visual representation
- B) The area where ZMP must remain for stability
- C) The collision geometry
- D) The sensor coverage area

## Question 9
In humanoid walking, what is "double support phase"?
- A) Robot is supported by both feet
- B) Robot is supported by one foot
- C) Robot is in flight phase
- D) Robot is falling

## Question 10
Which approach is used for handling redundant degrees of freedom in humanoid robots?
- A) Joint space control only
- B) Nullspace projection and prioritization
- C) Cartesian control only
- D) PID control only

## Question 11
What is the main advantage of using impedance control for humanoid manipulation?
- A) Simpler implementation
- B) Ability to regulate interaction forces and compliance
- C) Lower computational requirements
- D) Faster execution only

## Question 12
In the equation of motion M(q)q̈ + C(q, q̇)q̇ + G(q) = τ, what does M(q) represent?
- A) The mass of the robot's base
- B) The mass/inertia matrix
- C) The gravitational effects
- D) The Coriolis forces

## Question 13
Which approach is used for whole-body control in humanoid robots?
- A) Single-task control
- B) Hierarchical task control with prioritization
- C) Joint-level control only
- D) Position control only

## Question 14
What is the typical control frequency for balance control in humanoid robots?
- A) 1-10 Hz
- B) 50-200 Hz
- C) 1000+ Hz
- D) 1 Hz

## Question 15
In humanoid control, what does "task prioritization" mean?
- A) Executing tasks in order of importance
- B) Assigning different priorities to simultaneous control tasks
- C) Choosing which task to execute first
- D) Ranking joint importance

## Answer Key
1. B) Zero Moment Point
2. B) Center of mass height
3. B) To control task-space variables while considering robot dynamics
4. B) ZMP-based control
5. B) The point where the robot needs to step to come to rest
6. B) The software abstraction layer that defines how to communicate with hardware
7. C) IMU (Inertial Measurement Unit)
8. B) The area where ZMP must remain for stability
9. A) Robot is supported by both feet
10. B) Nullspace projection and prioritization
11. B) Ability to regulate interaction forces and compliance
12. B) The mass/inertia matrix
13. B) Hierarchical task control with prioritization
14. B) 50-200 Hz
15. B) Assigning different priorities to simultaneous control tasks