---
sidebar_label: 'Week 12 Lab: Humanoid Control Systems Implementation'
title: 'Week 12 Lab: Humanoid Control Systems Implementation'
---

# Week 12 Lab: Humanoid Control Systems Implementation

## Objective

In this lab, you will implement a complete humanoid control system that integrates balance control, walking control, and manipulation control using advanced control algorithms. You'll create a controller that maintains stability while performing complex tasks and demonstrate the integration of multiple control systems.

## Prerequisites

- Completion of Weeks 1-11 labs
- ROS 2 Humble with Isaac packages installed
- Understanding of robot kinematics and dynamics
- Basic knowledge of control theory and Python

## Step 1: Create a New ROS 2 Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for the humanoid control lab
ros2 pkg create --build-type ament_python humanoid_control_lab --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros builtin_interfaces message_generation

# Create necessary directories
mkdir -p ~/ros2_lab_ws/src/humanoid_control_lab/config
mkdir -p ~/ros2_lab_ws/src/humanoid_control_lab/launch
mkdir -p ~/ros2_lab_ws/src/humanoid_control_lab/worlds
mkdir -p ~/ros2_lab_ws/src/humanoid_control_lab/urdf
mkdir -p ~/ros2_lab_ws/src/humanoid_control_lab/controllers
```

## Step 2: Create the Robot Model with Control Interfaces

Create `~/ros2_lab_ws/src/humanoid_control_lab/urdf/humanoid_control_model.urdf.xacro`:

```xml
<?xml version="1.0"?>
<robot name="advanced_humanoid" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Properties -->
  <xacro:property name="pi" value="3.1415926535897931" />
  <xacro:property name="mass_head" value="2.0" />
  <xacro:property name="mass_torso" value="15.0" />
  <xacro:property name="mass_arm" value="1.5" />
  <xacro:property name="mass_forearm" value="0.8" />
  <xacro:property name="mass_hand" value="0.3" />
  <xacro:property name="mass_thigh" value="3.0" />
  <xacro:property name="mass_shin" value="2.5" />
  <xacro:property name="mass_foot" value="1.0" />

  <!-- Materials -->
  <material name="white">
    <color rgba="1 1 1 1"/>
  </material>
  <material name="blue">
    <color rgba="0 0 1 1"/>
  </material>
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>

  <!-- Base Link -->
  <link name="base_link">
    <inertial>
      <mass value="0.001"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <!-- Pelvis -->
  <joint name="pelvis_joint" type="fixed">
    <parent link="base_link"/>
    <child link="pelvis"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <link name="pelvis">
    <inertial>
      <mass value="${mass_torso * 0.3}"/>
      <origin xyz="0 0 0"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.02"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.25 0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.25 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Torso -->
  <joint name="torso_joint" type="fixed">
    <parent link="pelvis"/>
    <child link="torso"/>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
  </joint>

  <link name="torso">
    <inertial>
      <mass value="${mass_torso * 0.7}"/>
      <origin xyz="0 0 0.2"/>
      <inertia ixx="0.08" ixy="0" ixz="0" iyy="0.06" iyz="0" izz="0.04"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <box size="0.18 0.25 0.4"/>
      </geometry>
      <material name="white"/>
    </visual>

    <collision>
      <origin xyz="0 0 0.2" rpy="0 0 0"/>
      <geometry>
        <box size="0.18 0.25 0.4"/>
      </geometry>
    </collision>
  </link>

  <!-- Head -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/3}" upper="${pi/3}" effort="50" velocity="3.0"/>
  </joint>

  <link name="head">
    <inertial>
      <mass value="${mass_head}"/>
      <origin xyz="0 0 0.05"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="white"/>
    </visual>

    <collision>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Left Arm -->
  <joint name="left_shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.05 0.15 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="${pi/2}" effort="50" velocity="3.0"/>
  </joint>

  <link name="left_upper_arm">
    <inertial>
      <mass value="${mass_arm}"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_elbow_pitch" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_forearm"/>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/2}" upper="${pi/2}" effort="30" velocity="3.0"/>
  </joint>

  <link name="left_forearm">
    <inertial>
      <mass value="${mass_forearm}"/>
      <origin xyz="0 0 -0.075"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.002"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_wrist_yaw" type="revolute">
    <parent link="left_forearm"/>
    <child link="left_hand"/>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/4}" upper="${pi/4}" effort="10" velocity="3.0"/>
  </joint>

  <link name="left_hand">
    <inertial>
      <mass value="${mass_hand}"/>
      <origin xyz="0 0 -0.025"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
      <material name="white"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Right Arm (mirror of left) -->
  <joint name="right_shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="right_upper_arm"/>
    <origin xyz="0.05 -0.15 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="${pi/2}" effort="50" velocity="3.0"/>
  </joint>

  <link name="right_upper_arm">
    <inertial>
      <mass value="${mass_arm}"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_elbow_pitch" type="revolute">
    <parent link="right_upper_arm"/>
    <child link="right_forearm"/>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/2}" upper="${pi/2}" effort="30" velocity="3.0"/>
  </joint>

  <link name="right_forearm">
    <inertial>
      <mass value="${mass_forearm}"/>
      <origin xyz="0 0 -0.075"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.002"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.15"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_wrist_yaw" type="revolute">
    <parent link="right_forearm"/>
    <child link="right_hand"/>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/4}" upper="${pi/4}" effort="10" velocity="3.0"/>
  </joint>

  <link name="right_hand">
    <inertial>
      <mass value="${mass_hand}"/>
      <origin xyz="0 0 -0.025"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
      <material name="white"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Left Leg -->
  <joint name="left_hip_yaw" type="revolute">
    <parent link="pelvis"/>
    <child link="left_thigh"/>
    <origin xyz="0 0.05 -0.075" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/6}" upper="${pi/6}" effort="100" velocity="3.0"/>
  </joint>

  <link name="left_thigh">
    <inertial>
      <mass value="${mass_thigh}"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.06" length="0.3"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.06" length="0.3"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_hip_roll" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_thigh_upper"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="${-pi/4}" upper="${pi/4}" effort="100" velocity="3.0"/>
  </joint>

  <link name="left_thigh_upper">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="left_hip_pitch" type="revolute">
    <parent link="left_thigh_upper"/>
    <child link="left_shin"/>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="${pi/4}" effort="100" velocity="3.0"/>
  </joint>

  <link name="left_shin">
    <inertial>
      <mass value="${mass_shin}"/>
      <origin xyz="0 0 -0.125"/>
      <inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.008"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.25"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.25"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_knee_pitch" type="revolute">
    <parent link="left_shin"/>
    <child link="left_ankle"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="0" effort="100" velocity="3.0"/>
  </joint>

  <link name="left_ankle">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 -0.025"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_ankle_pitch" type="revolute">
    <parent link="left_ankle"/>
    <child link="left_foot"/>
    <origin xyz="0 0 -0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/6}" upper="${pi/3}" effort="50" velocity="3.0"/>
  </joint>

  <link name="left_foot">
    <inertial>
      <mass value="${mass_foot}"/>
      <origin xyz="0.05 0 -0.025"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Right Leg (mirror of left) -->
  <joint name="right_hip_yaw" type="revolute">
    <parent link="pelvis"/>
    <child link="right_thigh"/>
    <origin xyz="0 -0.05 -0.075" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/6}" upper="${pi/6}" effort="100" velocity="3.0"/>
  </joint>

  <link name="right_thigh">
    <inertial>
      <mass value="${mass_thigh}"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.06" length="0.3"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.06" length="0.3"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_hip_roll" type="revolute">
    <parent link="right_thigh"/>
    <child link="right_thigh_upper"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="${-pi/4}" upper="${pi/4}" effort="100" velocity="3.0"/>
  </joint>

  <link name="right_thigh_upper">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="right_hip_pitch" type="revolute">
    <parent link="right_thigh_upper"/>
    <child link="right_shin"/>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="${pi/4}" effort="100" velocity="3.0"/>
  </joint>

  <link name="right_shin">
    <inertial>
      <mass value="${mass_shin}"/>
      <origin xyz="0 0 -0.125"/>
      <inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.008"/>
    </inertial>

    <visual>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.25"/>
      </geometry>
      <material name="blue"/>
    </visual>

    <collision>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.25"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_knee_pitch" type="revolute">
    <parent link="right_shin"/>
    <child link="right_ankle"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/2}" upper="0" effort="100" velocity="3.0"/>
  </joint>

  <link name="right_ankle">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 -0.025"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="right_ankle_pitch" type="revolute">
    <parent link="right_ankle"/>
    <child link="right_foot"/>
    <origin xyz="0 0 -0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-pi/6}" upper="${pi/3}" effort="50" velocity="3.0"/>
  </joint>

  <link name="right_foot">
    <inertial>
      <mass value="${mass_foot}"/>
      <origin xyz="0.05 0 -0.025"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>

    <collision>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- ros2_control interface -->
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>

    <!-- Joint interfaces -->
    <joint name="neck_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_shoulder_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_elbow_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_wrist_yaw">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_shoulder_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_elbow_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_wrist_yaw">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_hip_yaw">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_hip_roll">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_hip_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_knee_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="left_ankle_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_hip_yaw">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_hip_roll">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_hip_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_knee_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="right_ankle_pitch">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <command_interface name="effort"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
  </ros2_control>

  <!-- Gazebo plugins -->
  <gazebo>
    <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
      <parameters>$(find humanoid_control_lab)/config/humanoid_control.yaml</parameters>
    </plugin>
  </gazebo>

  <!-- Sensors -->
  <gazebo reference="head">
    <sensor name="head_camera" type="camera">
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>
        <image><width>640</width><height>480</height><format>R8G8B8</format></image>
        <clip><near>0.1</near><far>100</far></clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>image_raw:=camera/image_raw</remapping>
          <remapping>camera_info:=camera/camera_info</remapping>
        </ros>
        <camera_name>camera</camera_name>
        <image_topic_name>image_raw</image_topic_name>
        <camera_info_topic_name>camera_info</camera_info_topic_name>
        <frame_name>head</frame_name>
      </plugin>
    </sensor>

    <sensor name="head_imu" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="imu_controller" filename="libgazebo_ros_imu.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>imu:=imu/data</remapping>
        </ros>
        <topic_name>imu</topic_name>
        <body_name>head</body_name>
        <frame_name>head</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo reference="left_foot">
    <sensor name="left_foot_ft" type="force_torque">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="left_foot_ft_controller" filename="libgazebo_ros_force_torque.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>wrench:=left_foot/wrench</remapping>
        </ros>
        <topic_name>left_foot/wrench</topic_name>
        <frame_name>left_foot</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo reference="right_foot">
    <sensor name="right_foot_ft" type="force_torque">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="right_foot_ft_controller" filename="libgazebo_ros_force_torque.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>wrench:=right_foot/wrench</remapping>
        </ros>
        <topic_name>right_foot/wrench</topic_name>
        <frame_name>right_foot</frame_name>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

## Step 3: Create Control Configuration Files

Create `~/ros2_lab_ws/src/humanoid_control_lab/config/humanoid_control.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 1000  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    # Balance controller
    balance_controller:
      type: effort_controllers/JointGroupEffortController

    # Walking controller
    walking_controller:
      type: position_controllers/JointGroupPositionController

    # Manipulation controllers
    left_arm_controller:
      type: position_controllers/JointGroupPositionController

    right_arm_controller:
      type: position_controllers/JointGroupPositionController

    # Whole body controller
    whole_body_controller:
      type: velocity_controllers/JointGroupVelocityController

# Balance controller
balance_controller:
  ros__parameters:
    joints:
      - left_ankle_pitch
      - left_ankle_roll
      - right_ankle_pitch
      - right_ankle_roll
      - left_hip_roll
      - right_hip_roll
      - torso_pitch
      - torso_roll

    # Control parameters
    kp_position: 1000.0
    ki_position: 0.0
    kd_position: 50.0
    kp_orientation: 500.0
    ki_orientation: 0.0
    kd_orientation: 25.0

    # ZMP control parameters
    zmp_tolerance: 0.05
    com_height: 0.85
    gravity: 9.81

# Walking controller
walking_controller:
  ros__parameters:
    joints:
      - left_hip_yaw
      - left_hip_roll
      - left_hip_pitch
      - left_knee_pitch
      - left_ankle_pitch
      - left_ankle_roll
      - right_hip_yaw
      - right_hip_roll
      - right_hip_pitch
      - right_knee_pitch
      - right_ankle_pitch
      - right_ankle_roll

    # Walking pattern parameters
    step_height: 0.05
    step_length: 0.3
    step_width: 0.2
    step_duration: 0.8
    double_support_ratio: 0.2

    # Control gains
    kp: 200.0
    ki: 10.0
    kd: 30.0

# Left arm controller
left_arm_controller:
  ros__parameters:
    joints:
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_shoulder_yaw
      - left_elbow_pitch
      - left_wrist_yaw
      - left_wrist_pitch

    # Control parameters for manipulation
    kp: 100.0
    ki: 5.0
    kd: 15.0

# Right arm controller
right_arm_controller:
  ros__parameters:
    joints:
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_shoulder_yaw
      - right_elbow_pitch
      - right_wrist_yaw
      - right_wrist_pitch

    # Control parameters for manipulation
    kp: 100.0
    ki: 5.0
    kd: 15.0

# Whole body controller
whole_body_controller:
  ros__parameters:
    joints:
      - neck_joint
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_elbow_pitch
      - left_wrist_yaw
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_elbow_pitch
      - right_wrist_yaw
      - left_hip_yaw
      - left_hip_roll
      - left_hip_pitch
      - left_knee_pitch
      - left_ankle_pitch
      - left_ankle_roll
      - right_hip_yaw
      - right_hip_roll
      - right_hip_pitch
      - right_knee_pitch
      - right_ankle_pitch
      - right_ankle_roll

    # Whole body control parameters
    control_frequency: 100
    balance_priority: 100.0
    walking_priority: 50.0
    manipulation_priority: 30.0
    posture_priority: 10.0

# Safety controller parameters
safety_controller:
  ros__parameters:
    tilt_angle_threshold: 30.0  # degrees
    zmp_deviation_threshold: 0.15  # meters
    joint_limit_margin: 0.05  # radians
    velocity_limit: 5.0  # rad/s
    torque_limit: 100.0  # Nm
    emergency_stop_timeout: 0.5  # seconds
```

## Step 4: Create the Main Control Node

Create `~/ros2_lab_ws/src/humanoid_control_lab/humanoid_control_lab/main_controller.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import JointState, Imu, Image, LaserScan
from geometry_msgs.msg import Twist, Vector3, WrenchStamped, Pose
from std_msgs.msg import String, Float64MultiArray
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from visualization_msgs.msg import Marker, MarkerArray
from nav_msgs.msg import Odometry
import numpy as np
import math
import time
from collections import deque
from enum import Enum
import threading

class ControlMode(Enum):
    IDLE = "idle"
    BALANCING = "balancing"
    WALKING = "walking"
    MANIPULATING = "manipulating"
    DEMONSTRATING = "demonstrating"
    SAFETY = "safety"

class HumanoidMainController(Node):
    def __init__(self):
        super().__init__('humanoid_main_controller')

        # Initialize control mode
        self.control_mode = ControlMode.IDLE
        self.previous_control_mode = ControlMode.IDLE

        # Robot state
        self.joint_positions = {}
        self.joint_velocities = {}
        self.joint_efforts = {}
        self.imu_data = None
        self.foot_force_data = {'left': None, 'right': None}
        self.camera_data = None
        self.lidar_data = None
        self.odom_data = None

        # Control parameters
        self.com_height = 0.85
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Publishers
        self.joint_trajectory_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10
        )
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.zmp_pub = self.create_publisher(Vector3, '/zmp', 10)
        self.com_pub = self.create_publisher(Vector3, '/com', 10)
        self.control_mode_pub = self.create_publisher(String, '/control_mode', 10)
        self.visualization_pub = self.create_publisher(MarkerArray, '/control_visualization', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/humanoid/imu/data',
            self.imu_callback,
            10
        )

        self.left_foot_ft_sub = self.create_subscription(
            WrenchStamped,
            '/humanoid/left_foot/wrench',
            self.left_foot_force_callback,
            10
        )

        self.right_foot_ft_sub = self.create_subscription(
            WrenchStamped,
            '/humanoid/right_foot/wrench',
            self.right_foot_force_callback,
            10
        )

        self.camera_sub = self.create_subscription(
            Image,
            '/humanoid/camera/image_raw',
            self.camera_callback,
            QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Command subscribers
        self.command_sub = self.create_subscription(
            String,
            '/robot_command',
            self.command_callback,
            10
        )

        # Timer for control loop
        self.control_timer = self.create_timer(0.01, self.control_step)  # 100 Hz
        self.high_freq_timer = self.create_timer(0.001, self.high_frequency_step)  # 1000 Hz

        # Control systems
        self.balance_controller = BalanceController(self.com_height)
        self.walking_controller = WalkingController()
        self.manipulation_controller = ManipulationController()
        self.safety_controller = SafetyController()

        # Control history
        self.zmp_history = deque(maxlen=100)
        self.com_history = deque(maxlen=100)
        self.control_history = deque(maxlen=50)

        # Task management
        self.active_tasks = []
        self.task_queue = []
        self.task_execution_lock = threading.Lock()

        # Performance monitoring
        self.performance_metrics = {
            'balance_stability': 0.0,
            'walking_efficiency': 0.0,
            'manipulation_accuracy': 0.0,
            'computation_time': 0.0
        }

        self.get_logger().info('Humanoid Main Controller initialized')

    def joint_state_callback(self, msg):
        """Update joint state information."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]
            if i < len(msg.velocity):
                self.joint_velocities[name] = msg.velocity[i]
            if i < len(msg.effort):
                self.joint_efforts[name] = msg.effort[i]

    def imu_callback(self, msg):
        """Update IMU data."""
        self.imu_data = msg

    def left_foot_force_callback(self, msg):
        """Update left foot force data."""
        self.foot_force_data['left'] = msg.wrench

    def right_foot_force_callback(self, msg):
        """Update right foot force data."""
        self.foot_force_data['right'] = msg.wrench

    def camera_callback(self, msg):
        """Update camera data."""
        self.camera_data = msg

    def lidar_callback(self, msg):
        """Update LIDAR data."""
        self.lidar_data = msg

    def odom_callback(self, msg):
        """Update odometry data."""
        self.odom_data = msg

    def command_callback(self, msg):
        """Handle high-level commands."""
        command = msg.data.lower()

        if command == 'start_balancing':
            self.set_control_mode(ControlMode.BALANCING)
        elif command == 'start_walking':
            self.set_control_mode(ControlMode.WALKING)
        elif command == 'start_manipulation':
            self.set_control_mode(ControlMode.MANIPULATING)
        elif command == 'start_demonstration':
            self.set_control_mode(ControlMode.DEMONSTRATING)
        elif command == 'stop':
            self.set_control_mode(ControlMode.IDLE)
        elif command.startswith('walk_to '):
            # Parse destination coordinates
            try:
                coords = command.split(' ')[1:]  # Get coordinates after 'walk_to'
                if len(coords) >= 2:
                    target_x = float(coords[0])
                    target_y = float(coords[1])
                    self.start_walking_to_target([target_x, target_y])
            except (ValueError, IndexError):
                self.get_logger().warn(f'Invalid walk_to command format: {command}')
        elif command.startswith('grasp_object'):
            # Handle grasp command
            self.start_grasp_task(command)
        elif command == 'emergency_stop':
            self.set_control_mode(ControlMode.SAFETY)

    def control_step(self):
        """Main control step executed at 100 Hz."""
        start_time = time.time()

        if not self.joint_positions:
            return

        # Update state estimation
        self.update_state_estimation()

        # Determine appropriate control mode
        self.update_control_mode()

        # Execute mode-specific control
        if self.control_mode == ControlMode.BALANCING:
            torques = self.balance_controller.compute_balance_control(
                self.joint_positions, self.joint_velocities, self.imu_data
            )
        elif self.control_mode == ControlMode.WALKING:
            torques = self.walking_controller.compute_walking_control(
                self.joint_positions, self.joint_velocities, self.foot_force_data
            )
        elif self.control_mode == ControlMode.MANIPULATING:
            torques = self.manipulation_controller.compute_manipulation_control(
                self.joint_positions, self.joint_velocities, self.camera_data
            )
        elif self.control_mode == ControlMode.DEMONSTRATING:
            torques = self.execute_demonstration_sequence()
        elif self.control_mode == ControlMode.SAFETY:
            torques = self.safety_controller.emergency_stop()
        else:  # IDLE
            torques = self.balance_controller.compute_idle_balance(
                self.joint_positions, self.joint_velocities
            )

        # Apply computed torques
        self.apply_joint_torques(torques)

        # Publish visualization
        self.publish_visualization()

        # Update performance metrics
        self.performance_metrics['computation_time'] = time.time() - start_time

    def high_frequency_step(self):
        """High-frequency control step for safety and immediate responses."""
        # Check for immediate safety issues
        if self.safety_controller.check_immediate_dangers(self.imu_data, self.foot_force_data):
            self.set_control_mode(ControlMode.SAFETY)

    def update_state_estimation(self):
        """Update robot state estimation."""
        if not self.joint_positions or not self.imu_data:
            return

        # Estimate center of mass
        com_pos, com_vel = self.estimate_com_state()

        # Calculate Zero Moment Point
        zmp_pos = self.calculate_zmp(com_pos, com_vel)

        # Store in history
        self.com_history.append(com_pos)
        self.zmp_history.append(zmp_pos)

        # Publish for monitoring
        self.publish_com_zmp(com_pos, zmp_pos)

    def estimate_com_state(self):
        """Estimate center of mass position and velocity."""
        # Simplified CoM estimation
        # In reality, this would use forward kinematics and link masses
        if self.joint_positions:
            # Use torso position as approximate CoM
            return np.array([0.0, 0.0, self.com_height]), np.array([0.0, 0.0, 0.0])
        else:
            return np.array([0.0, 0.0, self.com_height]), np.array([0.0, 0.0, 0.0])

    def calculate_zmp(self, com_pos, com_vel):
        """Calculate Zero Moment Point."""
        if not self.imu_data:
            return np.array([0.0, 0.0])

        linear_acc = np.array([
            self.imu_data.linear_acceleration.x,
            self.imu_data.linear_acceleration.y,
            self.imu_data.linear_acceleration.z
        ])

        zmp_x = com_pos[0] - (com_pos[2] / self.gravity) * linear_acc[0]
        zmp_y = com_pos[1] - (com_pos[2] / self.gravity) * linear_acc[1]

        return np.array([zmp_x, zmp_y])

    def publish_com_zmp(self, com_pos, zmp_pos):
        """Publish CoM and ZMP for monitoring."""
        com_msg = Vector3()
        com_msg.x, com_msg.y, com_msg.z = com_pos
        self.com_pub.publish(com_msg)

        zmp_msg = Vector3()
        zmp_msg.x, zmp_msg.y, zmp_msg.z = zmp_pos[0], zmp_pos[1], 0.0
        self.zmp_pub.publish(zmp_msg)

    def update_control_mode(self):
        """Update control mode based on current state and conditions."""
        # Check safety first (highest priority)
        if self.safety_controller.is_emergency_situation(self.imu_data, self.foot_force_data):
            self.set_control_mode(ControlMode.SAFETY)
            return

        # Mode-specific logic
        if self.control_mode == ControlMode.IDLE:
            if self.is_balance_needed():
                self.set_control_mode(ControlMode.BALANCING)
        elif self.control_mode == ControlMode.BALANCING:
            if self.is_walking_requested():
                self.set_control_mode(ControlMode.WALKING)
            elif not self.is_balance_needed():
                self.set_control_mode(ControlMode.IDLE)
        elif self.control_mode == ControlMode.WALKING:
            if self.is_walking_completed() or not self.is_walking_feasible():
                self.set_control_mode(ControlMode.BALANCING)
        elif self.control_mode == ControlMode.MANIPULATING:
            if self.is_manipulation_completed():
                self.set_control_mode(ControlMode.BALANCING)
        elif self.control_mode == ControlMode.DEMONSTRATING:
            if self.is_demonstration_completed():
                self.set_control_mode(ControlMode.IDLE)

    def is_balance_needed(self):
        """Check if balance control is needed."""
        # This would check for stability conditions
        return True  # For this example, always need balance

    def is_walking_requested(self):
        """Check if walking is requested."""
        # This would check for navigation goals
        return hasattr(self, 'walking_target')

    def is_walking_completed(self):
        """Check if walking task is completed."""
        # This would check if robot reached target
        return False

    def is_walking_feasible(self):
        """Check if walking is still feasible."""
        # This would check for obstacles, balance, etc.
        return True

    def is_manipulation_completed(self):
        """Check if manipulation task is completed."""
        # This would check manipulation status
        return False

    def is_demonstration_completed(self):
        """Check if demonstration is completed."""
        # This would check demonstration progress
        return False

    def set_control_mode(self, new_mode):
        """Safely transition to new control mode."""
        if self.control_mode != new_mode:
            old_mode = self.control_mode
            self.previous_control_mode = old_mode
            self.control_mode = new_mode

            self.get_logger().info(f'Control mode transition: {old_mode.value} -> {new_mode.value}')

            # Mode-specific initialization
            if new_mode == ControlMode.BALANCING:
                self.balance_controller.initialize()
            elif new_mode == ControlMode.WALKING:
                self.walking_controller.initialize()
            elif new_mode == ControlMode.MANIPULATING:
                self.manipulation_controller.initialize()
            elif new_mode == ControlMode.SAFETY:
                self.safety_controller.activate_safety_mode()

            # Publish mode change
            mode_msg = String()
            mode_msg.data = new_mode.value
            self.control_mode_pub.publish(mode_msg)

    def apply_joint_torques(self, torques):
        """Apply joint torques to robot."""
        if len(torques) == 0:
            return

        # Create joint trajectory message
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.header.frame_id = 'base_link'

        # Set joint names
        joint_names = list(self.joint_positions.keys())[:len(torques)]
        trajectory_msg.joint_names = joint_names

        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = [0.0] * len(torques)  # Use position control with PD
        point.velocities = [0.0] * len(torques)
        point.accelerations = [0.0] * len(torques)
        point.effort = torques.tolist()
        point.time_from_start = Duration(sec=0, nanosec=int(10000000))  # 10ms

        trajectory_msg.points = [point]
        self.joint_trajectory_pub.publish(trajectory_msg)

    def publish_visualization(self):
        """Publish visualization markers."""
        marker_array = MarkerArray()

        # Visualize CoM
        com_marker = Marker()
        com_marker.header.frame_id = 'map'
        com_marker.header.stamp = self.get_clock().now().to_msg()
        com_marker.ns = 'com'
        com_marker.id = 0
        com_marker.type = Marker.SPHERE
        com_marker.action = Marker.ADD

        if self.com_history:
            latest_com = self.com_history[-1]
            com_marker.pose.position.x = latest_com[0]
            com_marker.pose.position.y = latest_com[1]
            com_marker.pose.position.z = latest_com[2]
            com_marker.pose.orientation.w = 1.0

            com_marker.scale.x = 0.05
            com_marker.scale.y = 0.05
            com_marker.scale.z = 0.05

            com_marker.color.r = 0.0
            com_marker.color.g = 1.0
            com_marker.color.b = 0.0
            com_marker.color.a = 0.8

            marker_array.markers.append(com_marker)

        # Visualize ZMP
        if self.zmp_history:
            latest_zmp = self.zmp_history[-1]
            zmp_marker = Marker()
            zmp_marker.header = com_marker.header
            zmp_marker.ns = 'zmp'
            zmp_marker.id = 1
            zmp_marker.type = Marker.CYLINDER
            zmp_marker.action = Marker.ADD

            zmp_marker.pose.position.x = latest_zmp[0]
            zmp_marker.pose.position.y = latest_zmp[1]
            zmp_marker.pose.position.z = 0.02  # Slightly above ground
            zmp_marker.pose.orientation.w = 1.0

            zmp_marker.scale.x = 0.03
            zmp_marker.scale.y = 0.03
            zmp_marker.scale.z = 0.04

            zmp_marker.color.r = 1.0
            zmp_marker.color.g = 0.0
            zmp_marker.color.b = 0.0
            zmp_marker.color.a = 0.8

            marker_array.markers.append(zmp_marker)

        # Visualize support polygon
        support_polygon = self.calculate_support_polygon()
        if len(support_polygon) > 2:
            poly_marker = Marker()
            poly_marker.header = com_marker.header
            poly_marker.ns = 'support_polygon'
            poly_marker.id = 2
            poly_marker.type = Marker.LINE_STRIP
            poly_marker.action = Marker.ADD

            for vertex in support_polygon:
                point = Vector3()
                point.x = vertex[0]
                point.y = vertex[1]
                point.z = 0.01  # Slightly above ground
                poly_marker.points.append(point)

            # Close the polygon
            if len(poly_marker.points) > 0:
                poly_marker.points.append(poly_marker.points[0])

            poly_marker.scale.x = 0.02
            poly_marker.color.g = 1.0
            poly_marker.color.a = 0.6

            marker_array.markers.append(poly_marker)

        self.visualization_pub.publish(marker_array)

    def calculate_support_polygon(self):
        """Calculate current support polygon."""
        # Determine which feet are in contact
        left_contact = self.foot_force_data['left'] and abs(self.foot_force_data['left'].force.z) > 5.0
        right_contact = self.foot_force_data['right'] and abs(self.foot_force_data['right'].force.z) > 5.0

        vertices = []

        if left_contact and right_contact:
            # Double support polygon
            left_pos = self.get_foot_position('left')
            right_pos = self.get_foot_position('right')

            # Create polygon around both feet
            vertices = np.array([
                [left_pos[0] - 0.1, left_pos[1] - 0.05],   # Left foot back-left
                [left_pos[0] + 0.1, left_pos[1] - 0.05],   # Left foot front-left
                [right_pos[0] + 0.1, right_pos[1] + 0.05],  # Right foot front-right
                [right_pos[0] - 0.1, right_pos[1] + 0.05]   # Right foot back-right
            ])
        elif left_contact:
            # Single support - left foot
            left_pos = self.get_foot_position('left')
            vertices = np.array([
                [left_pos[0] - 0.1, left_pos[1] - 0.05],
                [left_pos[0] + 0.1, left_pos[1] - 0.05],
                [left_pos[0] + 0.1, left_pos[1] + 0.05],
                [left_pos[0] - 0.1, left_pos[1] + 0.05]
            ])
        elif right_contact:
            # Single support - right foot
            right_pos = self.get_foot_position('right')
            vertices = np.array([
                [right_pos[0] - 0.1, right_pos[1] - 0.05],
                [right_pos[0] + 0.1, right_pos[1] - 0.05],
                [right_pos[0] + 0.1, right_pos[1] + 0.05],
                [right_pos[0] - 0.1, right_pos[1] + 0.05]
            ])

        return vertices

    def get_foot_position(self, foot):
        """Get foot position from forward kinematics."""
        # This would use actual forward kinematics
        # For this example, return a simplified position
        if foot == 'left':
            return np.array([0.0, 0.1, 0.0])
        else:  # right
            return np.array([0.0, -0.1, 0.0])

    def start_walking_to_target(self, target_pos):
        """Start walking to specified target position."""
        self.walking_target = target_pos
        self.walking_controller.set_target(target_pos)
        self.set_control_mode(ControlMode.WALKING)

    def start_grasp_task(self, command):
        """Start object grasping task."""
        # Parse object information from command
        # This would be more sophisticated in practice
        self.manipulation_target = command
        self.set_control_mode(ControlMode.MANIPULATING)

    def execute_demonstration_sequence(self):
        """Execute demonstration sequence."""
        # This would execute predefined movement sequences
        # For this example, return zero torques
        return np.zeros(len(self.joint_positions))

    def get_performance_metrics(self):
        """Get current performance metrics."""
        return self.performance_metrics.copy()

class BalanceController:
    def __init__(self, com_height):
        self.com_height = com_height
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / com_height)

        # Control gains
        self.gains = {
            'kp': 100.0,
            'ki': 10.0,
            'kd': 20.0
        }

        # Balance state
        self.zmp_error_integral = np.zeros(2)
        self.previous_zmp_error = np.zeros(2)

    def initialize(self):
        """Initialize balance controller."""
        self.zmp_error_integral = np.zeros(2)
        self.previous_zmp_error = np.zeros(2)

    def compute_balance_control(self, joint_positions, joint_velocities, imu_data):
        """Compute balance control torques."""
        if not imu_data:
            return np.zeros(len(joint_positions))

        # Calculate current ZMP from IMU and CoM estimation
        # In a real implementation, this would use more sophisticated state estimation
        zmp_current = np.array([0.0, 0.0])  # Simplified
        zmp_desired = np.array([0.0, 0.0])  # For balance, keep ZMP centered

        # Calculate ZMP error
        zmp_error = zmp_desired - zmp_current

        # PID control for balance
        dt = 0.01  # 100 Hz
        p_term = self.gains['kp'] * zmp_error
        self.zmp_error_integral += zmp_error * dt
        i_term = self.gains['ki'] * self.zmp_error_integral
        d_term = self.gains['kd'] * (zmp_error - self.previous_zmp_error) / dt if dt > 0 else np.zeros(2)

        self.previous_zmp_error = zmp_error

        # Combine PID terms
        pid_output = p_term + i_term + d_term

        # Map to joint torques (simplified mapping)
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Distribute balance correction to relevant joints
        balance_joints = {
            'left_ankle_pitch': 0.3,
            'right_ankle_pitch': 0.3,
            'left_ankle_roll': 0.2,
            'right_ankle_roll': 0.2,
            'left_hip_pitch': 0.1,
            'right_hip_pitch': 0.1,
            'left_hip_roll': 0.05,
            'right_hip_roll': 0.05
        }

        joint_names = list(joint_positions.keys())
        for joint_name, weight in balance_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply correction based on ZMP error direction
                    torques[joint_idx] = weight * (pid_output[0] + pid_output[1])  # Combined X,Y correction

        return torques

    def compute_idle_balance(self, joint_positions, joint_velocities):
        """Compute balance control for idle state."""
        # Return to neutral position with PD control
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Define neutral positions for balance-critical joints
        neutral_positions = {
            'left_ankle_pitch': 0.0,
            'right_ankle_pitch': 0.0,
            'left_ankle_roll': 0.0,
            'right_ankle_roll': 0.0,
            'left_hip_pitch': 0.0,
            'right_hip_pitch': 0.0,
            'left_hip_roll': 0.0,
            'right_hip_roll': 0.0,
            'torso_pitch': 0.0,
            'torso_roll': 0.0
        }

        joint_names = list(joint_positions.keys())
        for joint_name, neutral_pos in neutral_positions.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    current_pos = joint_positions[joint_name]
                    current_vel = joint_velocities.get(joint_name, 0.0)

                    # PD control to neutral position
                    kp = 50.0
                    kd = 10.0
                    pos_error = neutral_pos - current_pos
                    torques[joint_idx] = kp * pos_error - kd * current_vel

        return torques

class WalkingController:
    def __init__(self):
        self.target_position = None
        self.current_step = 0
        self.support_foot = 'left'
        self.step_phase = 0.0

        # Walking parameters
        self.step_height = 0.05
        self.step_length = 0.3
        self.step_width = 0.2
        self.step_duration = 0.8

    def initialize(self):
        """Initialize walking controller."""
        self.current_step = 0
        self.support_foot = 'left'
        self.step_phase = 0.0

    def set_target(self, target_pos):
        """Set walking target position."""
        self.target_position = target_pos

    def compute_walking_control(self, joint_positions, joint_velocities, foot_force_data):
        """Compute walking control torques."""
        # Generate walking pattern
        walking_pattern = self.generate_walking_pattern()

        # Calculate required joint torques for walking
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # This would involve complex walking control algorithms
        # For this example, return simplified walking torques
        walking_torques = self.calculate_walking_torques(walking_pattern, joint_positions, joint_velocities)

        return walking_torques

    def generate_walking_pattern(self):
        """Generate walking pattern based on target."""
        # This would generate complete walking pattern
        # For this example, return simplified pattern
        pattern = {
            'left_foot_trajectory': [],
            'right_foot_trajectory': [],
            'com_trajectory': [],
            'zmp_trajectory': []
        }
        return pattern

    def calculate_walking_torques(self, walking_pattern, joint_positions, joint_velocities):
        """Calculate joint torques for walking pattern."""
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Simplified walking control - in reality this would be much more complex
        # involving ZMP tracking, footstep planning, and whole-body control
        walking_joints = {
            'left_hip_pitch': 0.2,
            'left_knee_pitch': 0.2,
            'left_ankle_pitch': 0.1,
            'right_hip_pitch': 0.2,
            'right_knee_pitch': 0.2,
            'right_ankle_pitch': 0.1
        }

        joint_names = list(joint_positions.keys())
        for joint_name, weight in walking_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply simple rhythmic walking pattern
                    walking_torques[joint_idx] = weight * math.sin(time.time() * 2)  # 2 Hz walking rhythm

        return walking_torques

class ManipulationController:
    def __init__(self):
        self.target_object = None
        self.manipulation_state = 'idle'

    def initialize(self):
        """Initialize manipulation controller."""
        self.manipulation_state = 'idle'

    def compute_manipulation_control(self, joint_positions, joint_velocities, camera_data):
        """Compute manipulation control torques."""
        # This would implement complex manipulation algorithms
        # For this example, return simplified manipulation torques
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        if self.manipulation_state == 'reaching':
            # Calculate reaching motion
            reaching_torques = self.calculate_reaching_torques(joint_positions, joint_velocities)
            return reaching_torques
        elif self.manipulation_state == 'grasping':
            # Calculate grasping motion
            grasping_torques = self.calculate_grasping_torques(joint_positions, joint_velocities)
            return grasping_torques
        else:
            # Return to neutral position
            return self.compute_idle_manipulation(joint_positions, joint_velocities)

    def calculate_reaching_torques(self, joint_positions, joint_velocities):
        """Calculate torques for reaching motion."""
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Simplified reaching control
        # In reality, this would use inverse kinematics
        arm_joints = {
            'left_shoulder_pitch': 0.3,
            'left_shoulder_roll': 0.2,
            'left_elbow_pitch': 0.3,
            'right_shoulder_pitch': 0.3,
            'right_shoulder_roll': 0.2,
            'right_elbow_pitch': 0.3
        }

        joint_names = list(joint_positions.keys())
        for joint_name, weight in arm_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply reaching motion
                    torques[joint_idx] = weight * 0.5  # Simple reaching motion

        return torques

    def calculate_grasping_torques(self, joint_positions, joint_velocities):
        """Calculate torques for grasping motion."""
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Simplified grasping control
        hand_joints = {
            'left_wrist_yaw': 0.1,
            'left_wrist_pitch': 0.1,
            'right_wrist_yaw': 0.1,
            'right_wrist_pitch': 0.1
        }

        joint_names = list(joint_positions.keys())
        for joint_name, weight in hand_joints.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    # Apply grasping motion
                    torques[joint_idx] = weight * 0.3  # Simple grasping motion

        return torques

    def compute_idle_manipulation(self, joint_positions, joint_velocities):
        """Return manipulation joints to idle position."""
        n_joints = len(joint_positions)
        torques = np.zeros(n_joints)

        # Return arms to neutral positions
        neutral_positions = {
            'left_shoulder_pitch': 0.0,
            'left_shoulder_roll': 0.0,
            'left_elbow_pitch': 0.0,
            'right_shoulder_pitch': 0.0,
            'right_shoulder_roll': 0.0,
            'right_elbow_pitch': 0.0
        }

        joint_names = list(joint_positions.keys())
        for joint_name, neutral_pos in neutral_positions.items():
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    current_pos = joint_positions[joint_name]
                    current_vel = joint_velocities.get(joint_name, 0.0)

                    # PD control to neutral position
                    kp = 50.0
                    kd = 10.0
                    pos_error = neutral_pos - current_pos
                    torques[joint_idx] = kp * pos_error - kd * current_vel

        return torques

class SafetyController:
    def __init__(self):
        self.safety_active = False
        self.emergency_stop_active = False

        # Safety thresholds
        self.thresholds = {
            'tilt_angle': math.radians(30),  # 30 degrees
            'zmp_deviation': 0.15,  # 15cm
            'joint_limit_violation': 0.05,  # 5 degrees
            'velocity_limit': 5.0,  # 5 rad/s
            'torque_limit': 100.0  # 100 Nm
        }

    def check_immediate_dangers(self, imu_data, foot_force_data):
        """Check for immediate safety dangers."""
        if not imu_data:
            return False

        # Check for dangerous tilt angles
        tilt_angle = self.calculate_tilt_angle(imu_data)
        if tilt_angle > self.thresholds['tilt_angle']:
            return True

        # Check for contact loss (falling)
        left_contact = foot_force_data['left'] and abs(foot_force_data['left'].force.z) > 5.0
        right_contact = foot_force_data['right'] and abs(foot_force_data['right'].force.z) > 5.0

        if not left_contact and not right_contact:
            # No contact with ground - possibly falling
            return True

        return False

    def is_emergency_situation(self, imu_data, foot_force_data):
        """Check if robot is in emergency situation."""
        return self.check_immediate_dangers(imu_data, foot_force_data)

    def calculate_tilt_angle(self, imu_data):
        """Calculate robot tilt angle from IMU data."""
        # Extract roll and pitch from quaternion
        w, x, y, z = (imu_data.orientation.w, imu_data.orientation.x,
                     imu_data.orientation.y, imu_data.orientation.z)

        # Convert quaternion to roll and pitch
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        # Combined tilt angle
        tilt_angle = math.sqrt(roll**2 + pitch**2)
        return tilt_angle

    def activate_safety_mode(self):
        """Activate safety mode."""
        self.safety_active = True
        self.emergency_stop_active = True
        self.get_logger().error('SAFETY MODE ACTIVATED - EMERGENCY STOP')

    def emergency_stop(self):
        """Return zero torques for emergency stop."""
        if not self.joint_positions:
            return np.zeros(28)  # Assuming 28 DOF
        return np.zeros(len(self.joint_positions))

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidMainController()

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

## Step 5: Create Launch Files

Create `~/ros2_lab_ws/src/humanoid_control_lab/launch/humanoid_control_system_launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    robot_name = LaunchConfiguration('robot_name', default='advanced_humanoid')
    world = LaunchConfiguration('world', default='simple_room')

    # Package names
    pkg_humanoid_control_lab = FindPackageShare('humanoid_control_lab')
    pkg_gazebo_ros = FindPackageShare('gazebo_ros')

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('humanoid_control_lab'),
                'worlds',
                world
            ]),
            'verbose': 'true',
            'use_sim_time': use_sim_time
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': open(
                PathJoinSubstitution([
                    FindPackageShare('humanoid_control_lab'),
                    'urdf',
                    'advanced_humanoid.urdf.xacro'
                ]).perform({}),
                'r'
            ).read()
        }]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', robot_name,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.85'  # Start above ground to allow settling
        ],
        output='screen'
    )

    # Load ros2_control controllers
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    load_balance_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['balance_controller'],
        output='screen',
    )

    load_walking_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['walking_controller'],
        output='screen',
    )

    load_left_arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['left_arm_controller'],
        output='screen',
    )

    load_right_arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['right_arm_controller'],
        output='screen',
    )

    # Main humanoid controller
    humanoid_controller = Node(
        package='humanoid_control_lab',
        executable='main_controller',
        name='humanoid_main_controller',
        parameters=[{
            'use_sim_time': use_sim_time,
            'com_height': 0.85,
            'gravity': 9.81
        }],
        output='screen'
    )

    # RViz for visualization
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('humanoid_control_lab'),
        'rviz',
        'humanoid_control.rviz'
    ])

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Isaac Sight for visualization (if available)
    try:
        isaac_sight = Node(
            package='isaac_sight',
            executable='sight_node',
            name='isaac_sight',
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        )
    except:
        # Isaac Sight not available, skip
        isaac_sight = None

    ld = LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'robot_name',
            default_value='advanced_humanoid',
            description='Name of the robot to spawn'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='simple_room',
            description='Choose one of the world files from `/humanoid_control_lab/worlds`'
        ),

        # Launch Gazebo
        gazebo,

        # Launch robot state publisher after Gazebo starts
        TimerAction(
            period=3.0,
            actions=[robot_state_publisher]
        ),

        # Spawn robot after robot state publisher starts
        TimerAction(
            period=5.0,
            actions=[spawn_entity]
        ),

        # Load controllers after robot spawns
        TimerAction(
            period=7.0,
            actions=[
                load_joint_state_broadcaster,
                load_balance_controller,
                load_walking_controller,
                load_left_arm_controller,
                load_right_arm_controller
            ]
        ),

        # Launch controllers after they're loaded
        TimerAction(
            period=9.0,
            actions=[humanoid_controller]
        ),

        # Launch RViz
        TimerAction(
            period=11.0,
            actions=[rviz]
        )
    ])

    if isaac_sight:
        ld.add_action(
            TimerAction(
                period=13.0,
                actions=[isaac_sight]
            )
        )

    return ld
```

## Step 6: Create the Lab Exercise Implementation

Create `~/ros2_lab_ws/src/humanoid_control_lab/humanoid_control_lab/lab_exercise.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu, Image
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import String, Bool
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np
import math
import time
from enum import Enum

class LabState(Enum):
    INITIALIZING = "initializing"
    CALIBRATING = "calibrating"
    TESTING_BALANCE = "testing_balance"
    TESTING_WALKING = "testing_walking"
    TESTING_MANIPULATION = "testing_manipulation"
    TESTING_INTEGRATION = "testing_integration"
    EVALUATING = "evaluating"
    COMPLETE = "complete"

class HumanoidControlLab(Node):
    def __init__(self):
        super().__init__('humanoid_control_lab')

        # Initialize lab state
        self.lab_state = LabState.INITIALIZING
        self.lab_step = 0
        self.lab_results = {}

        # Robot state
        self.joint_positions = {}
        self.joint_velocities = {}
        self.joint_efforts = {}
        self.imu_data = None
        self.camera_data = None

        # Publishers
        self.joint_trajectory_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10
        )
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lab_state_pub = self.create_publisher(String, '/lab/state', 10)
        self.lab_result_pub = self.create_publisher(String, '/lab/results', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )
        self.imu_sub = self.create_subscription(
            Imu, '/humanoid/imu/data', self.imu_callback, 10
        )
        self.camera_sub = self.create_subscription(
            Image, '/humanoid/camera/image_raw', self.camera_callback, 10
        )

        # Timer for lab execution
        self.lab_timer = self.create_timer(0.1, self.lab_step_execution)
        self.state_timer = self.create_timer(1.0, self.publish_lab_state)

        # Lab parameters
        self.com_height = 0.85
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Test parameters
        self.balance_test_duration = 10.0  # seconds
        self.walking_test_duration = 15.0
        self.manipulation_test_duration = 10.0
        self.integration_test_duration = 20.0

        # Performance metrics
        self.performance_metrics = {
            'balance_stability': 0.0,
            'walking_smoothness': 0.0,
            'manipulation_accuracy': 0.0,
            'system_integration': 0.0
        }

        self.get_logger().info('Humanoid Control Lab initialized')

    def joint_state_callback(self, msg):
        """Update joint state information."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]
            if i < len(msg.velocity):
                self.joint_velocities[name] = msg.velocity[i]
            if i < len(msg.effort):
                self.joint_efforts[name] = msg.effort[i]

    def imu_callback(self, msg):
        """Update IMU data."""
        self.imu_data = msg

    def camera_callback(self, msg):
        """Update camera data."""
        self.camera_data = msg

    def lab_step_execution(self):
        """Execute lab steps based on current state."""
        if self.lab_state == LabState.INITIALIZING:
            self.execute_initialization()
        elif self.lab_state == LabState.CALIBRATING:
            self.execute_calibration()
        elif self.lab_state == LabState.TESTING_BALANCE:
            self.execute_balance_test()
        elif self.lab_state == LabState.TESTING_WALKING:
            self.execute_walking_test()
        elif self.lab_state == LabState.TESTING_MANIPULATION:
            self.execute_manipulation_test()
        elif self.lab_state == LabState.TESTING_INTEGRATION:
            self.execute_integration_test()
        elif self.lab_state == LabState.EVALUATING:
            self.execute_evaluation()
        elif self.lab_state == LabState.COMPLETE:
            self.execute_completion()

    def execute_initialization(self):
        """Initialize the lab environment and robot."""
        self.get_logger().info('Initializing lab environment and robot...')

        # Verify robot is in simulation and responding
        if self.joint_positions:
            self.get_logger().info('Robot connection verified')
            self.lab_state = LabState.CALIBRATING
            self.lab_step = 0
        else:
            self.get_logger().warn('Waiting for robot connection...')

    def execute_calibration(self):
        """Calibrate sensors and establish baseline."""
        self.get_logger().info('Calibrating sensors and establishing baseline...')

        # Calibrate IMU by averaging readings over time
        if self.imu_data:
            # Store baseline IMU readings
            self.imu_baseline = {
                'linear_acceleration': np.array([
                    self.imu_data.linear_acceleration.x,
                    self.imu_data.linear_acceleration.y,
                    self.imu_data.linear_acceleration.z
                ]),
                'angular_velocity': np.array([
                    self.imu_data.angular_velocity.x,
                    self.imu_data.angular_velocity.y,
                    self.imu_data.angular_velocity.z
                ]),
                'orientation': np.array([
                    self.imu_data.orientation.x,
                    self.imu_data.orientation.y,
                    self.imu_data.orientation.z,
                    self.imu_data.orientation.w
                ])
            }

            self.get_logger().info('IMU calibrated successfully')

            # Move to neutral standing position
            neutral_pos = self.calculate_neutral_standing_position()
            self.move_to_configuration(neutral_pos, duration=2.0)

            self.lab_state = LabState.TESTING_BALANCE
            self.lab_step = 0
            self.balance_test_start_time = time.time()

    def execute_balance_test(self):
        """Test balance control system."""
        elapsed_time = time.time() - self.balance_test_start_time

        if elapsed_time > self.balance_test_duration:
            # Evaluate balance performance
            stability_score = self.evaluate_balance_performance()
            self.performance_metrics['balance_stability'] = stability_score

            self.get_logger().info(f'Balance test completed. Stability score: {stability_score:.2f}')
            self.lab_state = LabState.TESTING_WALKING
            self.lab_step = 0
            self.walking_test_start_time = time.time()
            return

        # Continue balance test
        if self.joint_positions and self.imu_data:
            # Apply balance control
            balance_torques = self.test_balance_control()
            self.apply_joint_torques(balance_torques)

            # Occasionally apply small disturbances to test robustness
            if int(elapsed_time) % 5 == 0 and elapsed_time % 1 > 0.5:  # Every 5 seconds, for 0.5s
                disturbance = self.generate_balance_disturbance()
                self.apply_disturbance(disturbance)

    def execute_walking_test(self):
        """Test walking control system."""
        elapsed_time = time.time() - self.walking_test_start_time

        if elapsed_time > self.walking_test_duration:
            # Evaluate walking performance
            walking_score = self.evaluate_walking_performance()
            self.performance_metrics['walking_smoothness'] = walking_score

            self.get_logger().info(f'Walking test completed. Smoothness score: {walking_score:.2f}')
            self.lab_state = LabState.TESTING_MANIPULATION
            self.lab_step = 0
            self.manipulation_test_start_time = time.time()
            return

        # Continue walking test
        if self.joint_positions:
            # Generate walking motion
            walking_torques = self.test_walking_control()
            self.apply_joint_torques(walking_torques)

    def execute_manipulation_test(self):
        """Test manipulation control system."""
        elapsed_time = time.time() - self.manipulation_test_start_time

        if elapsed_time > self.manipulation_test_duration:
            # Evaluate manipulation performance
            manipulation_score = self.evaluate_manipulation_performance()
            self.performance_metrics['manipulation_accuracy'] = manipulation_score

            self.get_logger().info(f'Manipulation test completed. Accuracy score: {manipulation_score:.2f}')
            self.lab_state = LabState.TESTING_INTEGRATION
            self.lab_step = 0
            self.integration_test_start_time = time.time()
            return

        # Continue manipulation test
        if self.joint_positions:
            # Generate manipulation motion
            manipulation_torques = self.test_manipulation_control()
            self.apply_joint_torques(manipulation_torques)

    def execute_integration_test(self):
        """Test system integration."""
        elapsed_time = time.time() - self.integration_test_start_time

        if elapsed_time > self.integration_test_duration:
            # Evaluate integration performance
            integration_score = self.evaluate_integration_performance()
            self.performance_metrics['system_integration'] = integration_score

            self.get_logger().info(f'Integration test completed. Integration score: {integration_score:.2f}')
            self.lab_state = LabState.EVALUATING
            return

        # Continue integration test - combine balance, walking, and manipulation
        if self.joint_positions and self.imu_data:
            # Apply integrated control
            integrated_torques = self.test_integrated_control()
            self.apply_joint_torques(integrated_torques)

    def execute_evaluation(self):
        """Evaluate overall performance."""
        self.get_logger().info('Evaluating overall performance...')

        # Calculate overall score
        overall_score = np.mean(list(self.performance_metrics.values()))

        evaluation_results = {
            'overall_score': overall_score,
            'metrics': self.performance_metrics,
            'recommendations': self.generate_recommendations()
        }

        self.lab_results = evaluation_results

        self.get_logger().info(f'Overall performance score: {overall_score:.2f}')
        self.get_logger().info(f'Balance stability: {self.performance_metrics["balance_stability"]:.2f}')
        self.get_logger().info(f'Walking smoothness: {self.performance_metrics["walking_smoothness"]:.2f}')
        self.get_logger().info(f'Manipulation accuracy: {self.performance_metrics["manipulation_accuracy"]:.2f}')
        self.get_logger().info(f'System integration: {self.performance_metrics["system_integration"]:.2f}')

        self.lab_state = LabState.COMPLETE

    def execute_completion(self):
        """Complete the lab exercise."""
        self.get_logger().info('Lab exercise completed successfully!')
        self.get_logger().info(f'Final results: {self.lab_results}')

        # Publish final results
        result_msg = String()
        result_msg.data = str(self.lab_results)
        self.lab_result_pub.publish(result_msg)

        # Stop all motion
        self.apply_zero_torques()

    def test_balance_control(self):
        """Test balance control algorithm."""
        # Calculate current ZMP from IMU and joint positions
        current_zmp = self.calculate_current_zmp()

        # Desired ZMP (for balance, should be centered)
        desired_zmp = np.array([0.0, 0.0])

        # Calculate ZMP error
        zmp_error = desired_zmp - current_zmp

        # PID control for balance
        kp = 100.0
        ki = 10.0
        kd = 20.0

        p_term = kp * zmp_error
        self.zmp_error_integral += zmp_error * 0.1  # 10 Hz
        i_term = ki * self.zmp_error_integral
        d_term = kd * (zmp_error - self.previous_zmp_error) / 0.1
        self.previous_zmp_error = zmp_error

        pid_output = p_term + i_term + d_term

        # Map to joint torques
        n_joints = len(self.joint_positions) if self.joint_positions else 28
        torques = np.zeros(n_joints)

        # Apply to balance-critical joints
        balance_joints = ['left_ankle_pitch', 'right_ankle_pitch', 'left_hip_pitch', 'right_hip_pitch']
        joint_names = list(self.joint_positions.keys()) if self.joint_positions else []

        for i, joint_name in enumerate(balance_joints):
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    torques[joint_idx] = pid_output[0] * 0.3  # X correction

        return torques

    def test_walking_control(self):
        """Test walking control algorithm."""
        n_joints = len(self.joint_positions) if self.joint_positions else 28
        torques = np.zeros(n_joints)

        # Generate simple walking pattern
        walking_freq = 1.0  # Hz
        walking_amplitude = 0.5

        current_time = time.time()
        left_hip = walking_amplitude * math.sin(2 * math.pi * walking_freq * current_time)
        right_hip = walking_amplitude * math.sin(2 * math.pi * walking_freq * current_time + math.pi)  # Opposite phase

        # Apply to walking joints
        walking_joints = ['left_hip_pitch', 'right_hip_pitch', 'left_knee_pitch', 'right_knee_pitch']
        joint_names = list(self.joint_positions.keys()) if self.joint_positions else []

        for i, joint_name in enumerate(walking_joints):
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    if 'left' in joint_name:
                        torques[joint_idx] = left_hip * (0.5 if 'hip' in joint_name else 0.3)
                    else:  # right
                        torques[joint_idx] = right_hip * (0.5 if 'hip' in joint_name else 0.3)

        return torques

    def test_manipulation_control(self):
        """Test manipulation control algorithm."""
        n_joints = len(self.joint_positions) if self.joint_positions else 28
        torques = np.zeros(n_joints)

        # Generate simple manipulation pattern
        manipulation_freq = 0.5  # Hz
        manipulation_amplitude = 0.3

        current_time = time.time()
        left_arm = manipulation_amplitude * math.sin(2 * math.pi * manipulation_freq * current_time)
        right_arm = manipulation_amplitude * math.cos(2 * math.pi * manipulation_freq * current_time)

        # Apply to manipulation joints
        manipulation_joints = ['left_shoulder_pitch', 'left_elbow_pitch', 'right_shoulder_pitch', 'right_elbow_pitch']
        joint_names = list(self.joint_positions.keys()) if self.joint_positions else []

        for i, joint_name in enumerate(manipulation_joints):
            if joint_name in joint_names:
                joint_idx = joint_names.index(joint_name)
                if joint_idx < n_joints:
                    if 'left' in joint_name:
                        torques[joint_idx] = left_arm
                    else:  # right
                        torques[joint_idx] = right_arm

        return torques

    def test_integrated_control(self):
        """Test integrated control combining all systems."""
        # Combine all control strategies
        balance_torques = self.test_balance_control()
        walking_torques = self.test_walking_control() * 0.5  # Reduce walking intensity for integration
        manipulation_torques = self.test_manipulation_control() * 0.3  # Reduce manipulation intensity

        n_joints = len(balance_torques)
        integrated_torques = np.zeros(n_joints)

        # Weighted combination of all control signals
        for i in range(n_joints):
            integrated_torques[i] = (
                0.6 * balance_torques[i] +  # Prioritize balance
                0.3 * walking_torques[i] +  # Secondary: walking
                0.1 * manipulation_torques[i]  # Tertiary: manipulation
            )

        return integrated_torques

    def calculate_current_zmp(self):
        """Calculate current ZMP from sensor data."""
        if not self.imu_data:
            return np.array([0.0, 0.0])

        # Simplified ZMP calculation from IMU data
        linear_acc = np.array([
            self.imu_data.linear_acceleration.x,
            self.imu_data.linear_acceleration.y,
            self.imu_data.linear_acceleration.z
        ])

        zmp_x = 0.0 - (self.com_height / self.gravity) * linear_acc[0]  # Simplified
        zmp_y = 0.0 - (self.com_height / self.gravity) * linear_acc[1]  # Simplified

        return np.array([zmp_x, zmp_y])

    def evaluate_balance_performance(self):
        """Evaluate balance control performance."""
        # In a real implementation, this would analyze stability metrics
        # For this example, return a simplified score
        return 0.85  # Good balance performance

    def evaluate_walking_performance(self):
        """Evaluate walking control performance."""
        # In a real implementation, this would analyze gait metrics
        # For this example, return a simplified score
        return 0.78  # Good walking performance

    def evaluate_manipulation_performance(self):
        """Evaluate manipulation control performance."""
        # In a real implementation, this would analyze precision metrics
        # For this example, return a simplified score
        return 0.82  # Good manipulation performance

    def evaluate_integration_performance(self):
        """Evaluate system integration performance."""
        # In a real implementation, this would analyze coordination metrics
        # For this example, return a simplified score
        return 0.75  # Good integration performance

    def generate_balance_disturbance(self):
        """Generate balance disturbance for testing robustness."""
        # Create small force disturbance to test balance recovery
        disturbance = Twist()
        disturbance.linear.x = 0.1 * np.random.randn()  # Random disturbance in X
        disturbance.linear.y = 0.1 * np.random.randn()  # Random disturbance in Y
        return disturbance

    def apply_disturbance(self, disturbance):
        """Apply external disturbance to test robustness."""
        # This would apply external forces in simulation
        # For this example, we'll just log the disturbance
        self.get_logger().info(f'Applied disturbance: {disturbance}')

    def calculate_neutral_standing_position(self):
        """Calculate neutral standing joint configuration."""
        n_joints = len(self.joint_positions) if self.joint_positions else 28
        neutral_pos = np.zeros(n_joints)

        # Standing position with relaxed joints
        joint_names = list(self.joint_positions.keys()) if self.joint_positions else [f'joint_{i}' for i in range(n_joints)]

        # Set leg joints to standing position
        if 'left_hip_pitch' in joint_names:
            idx = joint_names.index('left_hip_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'right_hip_pitch' in joint_names:
            idx = joint_names.index('right_hip_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'left_knee_pitch' in joint_names:
            idx = joint_names.index('left_knee_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'right_knee_pitch' in joint_names:
            idx = joint_names.index('right_knee_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'left_ankle_pitch' in joint_names:
            idx = joint_names.index('left_ankle_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'right_ankle_pitch' in joint_names:
            idx = joint_names.index('right_ankle_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0

        # Set arm joints to relaxed position
        if 'left_shoulder_pitch' in joint_names:
            idx = joint_names.index('left_shoulder_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0
        if 'right_shoulder_pitch' in joint_names:
            idx = joint_names.index('right_shoulder_pitch')
            if idx < n_joints:
                neutral_pos[idx] = 0.0

        return neutral_pos

    def move_to_configuration(self, target_angles, duration=1.0):
        """Move robot to target configuration smoothly."""
        if not self.joint_positions:
            return

        current_angles = list(self.joint_positions.values())
        n_joints = min(len(current_angles), len(target_angles))

        # Generate trajectory
        n_points = int(duration * 50)  # 50 Hz
        dt = duration / n_points

        for i in range(n_points + 1):
            progress = i / n_points
            current_target = []

            for j in range(n_joints):
                # Linear interpolation
                angle = current_angles[j] + progress * (target_angles[j] - current_angles[j])
                current_target.append(angle)

            self.apply_joint_positions(current_target)
            time.sleep(dt)

    def apply_joint_torques(self, torques):
        """Apply joint torques to robot."""
        if len(torques) == 0:
            return

        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.header.frame_id = 'base_link'

        joint_names = list(self.joint_positions.keys())[:len(torques)] if self.joint_positions else [f'joint_{i}' for i in range(len(torques))]
        trajectory_msg.joint_names = joint_names

        point = JointTrajectoryPoint()
        point.positions = [0.0] * len(torques)
        point.velocities = [0.0] * len(torques)
        point.accelerations = [0.0] * len(torques)
        point.effort = torques.tolist()
        point.time_from_start = Duration(sec=0, nanosec=int(10000000))  # 10ms

        trajectory_msg.points = [point]
        self.joint_trajectory_pub.publish(trajectory_msg)

    def apply_zero_torques(self):
        """Apply zero torques to all joints."""
        if self.joint_positions:
            zero_torques = [0.0] * len(self.joint_positions)
            self.apply_joint_torques(zero_torques)

    def apply_joint_positions(self, positions):
        """Apply joint positions for trajectory following."""
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.header.frame_id = 'base_link'
        trajectory_msg.joint_names = list(self.joint_positions.keys())[:len(positions)] if self.joint_positions else [f'joint_{i}' for i in range(len(positions))]

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=0, nanosec=int(10000000))  # 10ms

        trajectory_msg.points = [point]
        self.joint_trajectory_pub.publish(trajectory_msg)

    def publish_lab_state(self):
        """Publish current lab state."""
        state_msg = String()
        state_msg.data = f"{self.lab_state.value}_{self.lab_step}"
        self.lab_state_pub.publish(state_msg)

    def generate_recommendations(self):
        """Generate recommendations based on performance."""
        recommendations = []

        if self.performance_metrics['balance_stability'] < 0.8:
            recommendations.append("Balance control needs improvement - consider adjusting PID gains")
        if self.performance_metrics['walking_smoothness'] < 0.8:
            recommendations.append("Walking control needs refinement - smoother trajectories required")
        if self.performance_metrics['manipulation_accuracy'] < 0.8:
            recommendations.append("Manipulation control needs calibration - improve precision")
        if self.performance_metrics['system_integration'] < 0.8:
            recommendations.append("System integration needs better coordination - adjust task priorities")

        return recommendations

def main(args=None):
    rclpy.init(args=args)
    lab_node = HumanoidControlLab()

    try:
        rclpy.spin(lab_node)
    except KeyboardInterrupt:
        lab_node.get_logger().info('Shutting down humanoid control lab...')
    finally:
        lab_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 7: Create Setup Files

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'humanoid_control_lab'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/urdf', glob('urdf/*.xacro')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.world')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Humanoid Control Laboratory Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'main_controller = humanoid_control_lab.main_controller:main',
            'lab_exercise = humanoid_control_lab.lab_exercise:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_control_lab</name>
  <version>0.0.0</version>
  <description>Humanoid Control Laboratory Package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake_python</buildtool_depend>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>tf2_ros</depend>
  <depend>cv_bridge</depend>
  <depend>message_runtime</depend>

  <exec_depend>gazebo_ros_pkgs</exec_depend>
  <exec_depend>gazebo_ros2_control</exec_depend>
  <exec_depend>joint_state_publisher</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <exec_depend>isaac_ros_common</exec_depend>
  <exec_depend>isaac_ros_image_pipeline</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Step 8: Build and Test the Package

```bash
# Go to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select humanoid_control_lab

# Source the workspace
source install/setup.bash
```

## Lab Exercise Steps

1. **Build the complete control system**: Build all components of the humanoid control system
2. **Test individual control modules**: Verify that balance, walking, and manipulation controllers work independently
3. **Integrate and test**: Combine all control systems and test coordinated behavior
4. **Tune control parameters**: Adjust gains for stable and responsive control
5. **Validate performance**: Test in various scenarios and evaluate metrics

## Lab Questions

1. How does the ZMP-based balance control ensure stable walking?
2. What are the key challenges in coordinating multiple control tasks simultaneously?
3. How does the operational space control handle redundant DOFs?
4. What role does the control hierarchy play in humanoid stability?
5. How could you extend this system to handle dynamic environments?

## Summary

Humanoid control systems require sophisticated integration of multiple control approaches to achieve stable, coordinated motion. The key components include balance control, walking control, manipulation control, and whole-body coordination. Understanding these control systems is essential for developing effective humanoid robots capable of performing complex tasks in human environments.