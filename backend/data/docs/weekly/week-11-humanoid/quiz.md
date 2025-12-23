---
sidebar_label: 'Week 11 Quiz: Humanoid Dynamics and Control'
title: 'Week 11 Quiz: Humanoid Dynamics and Control'
---

# Week 11 Quiz: Humanoid Dynamics and Control

## Question 1
What does ZMP stand for in humanoid robotics?
- A) Zero Motion Point
- B) Zero Moment Point
- C) Zero Momentum Point
- D) Zero Mass Point

## Question 2
In the Linear Inverted Pendulum Model (LIPM), what remains constant?
- A) Robot's angular momentum
- B) Center of mass height
- C) Robot's total energy
- D) Joint angles

## Question 3
Which equation represents the relationship between Center of Mass (CoM) and Zero Moment Point (ZMP)?
- A) ZMP = CoM + (h/g) * CoM_acceleration
- B) ZMP = CoM - (h/g) * CoM_acceleration
- C) ZMP = CoM * (g/h)
- D) ZMP = CoM + CoM_velocity

## Question 4
What is the primary purpose of operational space control in humanoid robots?
- A) To control joint positions only
- B) To control task-space variables while considering robot dynamics
- C) To reduce computational requirements
- D) To eliminate the need for sensors

## Question 5
In humanoid walking, what is a "capture point"?
- A) The point where the robot captures objects
- B) The point where the robot needs to step to come to rest
- C) The center of the support polygon
- D) The location of the ZMP

## Question 6
Which sensor is most critical for balance control in humanoid robots?
- A) Camera
- B) LIDAR
- C) IMU (Inertial Measurement Unit)
- D) Force/Torque sensors

## Question 7
What does the term "support polygon" refer to in humanoid robotics?
- A) The polygon formed by the robot's base
- B) The area where ZMP must remain for stability
- C) The visual representation of the robot
- D) The area covered by sensors

## Question 8
In ros2_control, what is a "hardware interface"?
- A) The physical robot hardware
- B) The software abstraction layer that defines how to communicate with hardware
- C) The simulation environment
- D) The control algorithm

## Question 9
Which physics engine is commonly used in Gazebo for humanoid simulation?
- A) PhysX
- B) Bullet
- C) ODE (Open Dynamics Engine)
- D) All of the above

## Question 10
What is the main advantage of using impedance control for humanoid manipulation?
- A) Simpler implementation
- B) Ability to regulate interaction forces and compliance
- C) Lower computational requirements
- D) Faster execution only

## Question 11
In humanoid dynamics, what does the mass matrix M(q) represent?
- A) Only the mass of the robot's base
- B) The relationship between joint accelerations and applied torques
- C) The gravitational effects
- D) The Coriolis forces

## Question 12
What is the purpose of the Coriolis and centrifugal matrix C(q, q̇) in the dynamics equation?
- A) To represent gravitational effects
- B) To account for velocity-dependent forces due to motion
- C) To represent external forces
- D) To represent joint limits

## Question 13
Which control approach is most appropriate for maintaining balance during walking?
- A) Joint position control only
- B) ZMP-based control
- C) Open-loop control
- D) Feedforward control only

## Question 14
What does the "manipulability ellipsoid" represent in humanoid robotics?
- A) The robot's visual appearance
- B) The robot's ability to move in different directions in task space
- C) The collision geometry
- D) The sensor coverage area

## Question 15
In humanoid walking pattern generation, what is the typical phase sequence?
- A) Single support → Double support → Single support
- B) Double support → Single support → Double support
- C) Single support only
- D) Double support only

## Answer Key
1. B) Zero Moment Point
2. B) Center of mass height
3. B) ZMP = CoM - (h/g) * CoM_acceleration
4. B) To control task-space variables while considering robot dynamics
5. B) The point where the robot needs to step to come to rest
6. C) IMU (Inertial Measurement Unit)
7. B) The area where ZMP must remain for stability
8. B) The software abstraction layer that defines how to communicate with hardware
9. D) All of the above
10. B) Ability to regulate interaction forces and compliance
11. B) The relationship between joint accelerations and applied torques
12. B) To account for velocity-dependent forces due to motion
13. B) ZMP-based control
14. B) The robot's ability to move in different directions in task space
15. B) Double support → Single support → Double support