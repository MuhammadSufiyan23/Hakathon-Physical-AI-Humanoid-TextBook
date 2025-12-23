---
sidebar_label: 'Week 7 Quiz: Advanced Gazebo Simulation'
title: 'Week 7 Quiz: Advanced Gazebo Simulation'
---

# Week 7 Quiz: Advanced Gazebo Simulation

## Question 1
Which physics engine is NOT supported by Gazebo?
- A) ODE (Open Dynamics Engine)
- B) Bullet
- C) PhysX
- D) Simbody

## Question 2
What is the purpose of the ros2_control integration in Gazebo?
- A) To replace all other plugins
- B) To provide hardware abstraction and standardized control interfaces
- C) To improve graphics rendering
- D) To reduce simulation time

## Question 3
In Gazebo plugin configuration, what does the "remapping" element do?
- A) Changes the physical properties of objects
- B) Maps Gazebo topics to different ROS topic names
- C) Adjusts simulation speed
- D) Modifies collision detection

## Question 4
Which Gazebo plugin would you use to publish joint states to ROS 2?
- A) libgazebo_ros_diff_drive.so
- B) libgazebo_ros_joint_state_publisher.so
- C) libgazebo_ros_imu.so
- D) libgazebo_ros_camera.so

## Question 5
What is the main advantage of using heightmaps for terrain modeling?
- A) Better visual quality only
- B) Realistic elevation changes and complex terrain
- C) Faster simulation performance
- D) Reduced memory usage

## Question 6
In ros2_control, what is a "hardware interface"?
- A) The physical robot hardware
- B) The software abstraction layer that defines how to communicate with hardware
- C) The simulation environment
- D) The control algorithm

## Question 7
Which parameter in physics configuration affects simulation stability the most?
- A) real_time_factor
- B) max_step_size
- C) update_rate
- D) solver type

## Question 8
What is the purpose of the "use_sim_time" parameter in ROS 2 nodes?
- A) To enable simulation mode
- B) To use Gazebo's simulation clock instead of system time
- C) To speed up execution
- D) To reduce memory usage

## Question 9
Which tool is used to bridge messages between ROS 2 and Gazebo Garden?
- A) gazebo_ros_pkgs
- B) ros_gz_bridge
- C) ros2_control
- D) rqt

## Question 10
What is the correct order of operations when launching a Gazebo-ROS 2 integrated system?
- A) Spawn robot, launch Gazebo, start controllers
- B) Launch Gazebo, spawn robot, start controllers
- C) Start controllers, launch Gazebo, spawn robot
- D) Launch Gazebo, start controllers, spawn robot

## Answer Key
1. C) PhysX
2. B) To provide hardware abstraction and standardized control interfaces
3. B) Maps Gazebo topics to different ROS topic names
4. B) libgazebo_ros_joint_state_publisher.so
5. B) Realistic elevation changes and complex terrain
6. B) The software abstraction layer that defines how to communicate with hardware
7. B) max_step_size
8. B) To use Gazebo's simulation clock instead of system time
9. B) ros_gz_bridge
10. B) Launch Gazebo, spawn robot, start controllers