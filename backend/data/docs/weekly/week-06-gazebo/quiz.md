---
sidebar_label: 'Week 6 Quiz: Gazebo Simulation'
title: 'Week 6 Quiz: Gazebo Simulation'
---

# Week 6 Quiz: Gazebo Simulation

## Question 1
What does SDF stand for in Gazebo?
- A) Simulation Description Format
- B) System Definition Framework
- C) Sensor Data Format
- D) Software Development Framework

## Question 2
Which physics engines are supported by Gazebo? (Choose all that apply)
- A) ODE (Open Dynamics Engine)
- B) Bullet
- C) Simbody
- D) All of the above

## Question 3
What is the primary difference between URDF and SDF in robotics simulation?
- A) URDF is for visualization, SDF is for physics
- B) URDF describes robot kinematics, SDF is Gazebo-specific simulation features
- C) URDF is for mobile robots, SDF is for manipulators
- D) There is no difference, they are interchangeable

## Question 4
Which Gazebo plugin would you use for a differential drive robot?
- A) libgazebo_ros_joint_state_publisher.so
- B) libgazebo_ros_diff_drive.so
- C) libgazebo_ros_imu.so
- D) libgazebo_ros_camera.so

## Question 5
What is the purpose of the `gazebo` tag in URDF files?
- A) To define visual properties only
- B) To specify collision geometry
- C) To add Gazebo-specific extensions and plugins
- D) To define joint properties

## Question 6
Which sensor type would be most appropriate for 2D mapping and navigation?
- A) Camera
- B) IMU
- C) LIDAR
- D) GPS

## Question 7
In a LIDAR sensor configuration, what does the "samples" parameter define?
- A) Number of laser beams
- B) Number of points per scan
- C) Number of measurements per second
- D) Number of data points in the output

## Question 8
What is the recommended approach for creating reusable robot models with similar components?
- A) Copy and paste URDF code
- B) Use Xacro macros
- C) Create separate files for each component
- D) Use Python scripts

## Question 9
Which parameter in a camera sensor configuration determines the field of view?
- A) width
- B) horizontal_fov
- C) range
- D) clip

## Question 10
What is the purpose of the "always_on" tag in Gazebo sensor configurations?
- A) To make the sensor run continuously
- B) To enable the sensor at startup
- C) To keep the sensor active even when no one subscribes
- D) To set the sensor update rate

## Answer Key
1. A) Simulation Description Format
2. D) All of the above
3. B) URDF describes robot kinematics, SDF is Gazebo-specific simulation features
4. B) libgazebo_ros_diff_drive.so
5. C) To add Gazebo-specific extensions and plugins
6. C) LIDAR
7. B) Number of points per scan
8. B) Use Xacro macros
9. B) horizontal_fov
10. A) To make the sensor run continuously