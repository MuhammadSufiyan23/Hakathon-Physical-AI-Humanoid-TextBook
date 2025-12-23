---
sidebar_label: 'Week 11 Lab: Isaac Sim Humanoid Development'
title: 'Week 11 Lab: Isaac Sim Humanoid Development'
---

# Week 11 Lab: Isaac Sim Humanoid Development

## Objective

In this lab, you will create a complete humanoid robot simulation in Isaac Sim, implement advanced control systems including balance control and whole-body control, and develop a walking pattern generator. You'll learn to integrate perception, control, and learning systems in a unified humanoid platform.

## Prerequisites

- Completion of Weeks 1-10 labs
- Isaac Sim installed with Omniverse
- Basic understanding of ROS 2 and control theory
- Python programming experience

## Step 1: Create a New Isaac Sim Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for Isaac Sim humanoid development
ros2 pkg create --build-type ament_python isaac_humanoid_lab --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros cv_bridge builtin_interfaces message_generation

# Create necessary directories
mkdir -p ~/ros2_lab_ws/src/isaac_humanoid_lab/config
mkdir -p ~/ros2_lab_ws/src/isaac_humanoid_lab/launch
mkdir -p ~/ros2_lab_ws/src/isaac_humanoid_lab/worlds
mkdir -p ~/ros2_lab_ws/src/isaac_humanoid_lab/urdf
mkdir -p ~/ros2_lab_ws/src/isaac_humanoid_lab/models
```

## Step 2: Create the Humanoid Robot Model

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/urdf/humanoid_robot.urdf.xacro`:

```xml
<?xml version="1.0"?>
<robot name="isaac_humanoid" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Constants -->
  <xacro:property name="pi" value="3.1415926535897931" />
  <xacro:property name="mass_head" value="2.0" />
  <xacro:property name="mass_torso" value="10.0" />
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
  <joint name="left_shoulder_joint" type="revolute">
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
        <capsule radius="0.05" length="0.1"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_elbow_joint" type="revolute">
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
        <capsule radius="0.04" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_wrist_joint" type="revolute">
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
  <joint name="right_shoulder_joint" type="revolute">
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
        <capsule radius="0.05" length="0.1"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_elbow_joint" type="revolute">
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
        <capsule radius="0.04" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.075" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_wrist_joint" type="revolute">
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
  <joint name="left_hip_joint" type="revolute">
    <parent link="pelvis"/>
    <child link="left_thigh"/>
    <origin xyz="0 0.05 -0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/4}" upper="${pi/2}" effort="100" velocity="3.0"/>
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
        <capsule radius="0.06" length="0.2"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_knee_joint" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_shin"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/2}" upper="0" effort="100" velocity="3.0"/>
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
        <capsule radius="0.05" length="0.15"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.15"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_ankle_joint" type="revolute">
    <parent link="left_shin"/>
    <child link="left_foot"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
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
        <box size="0.18 0.08 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.18 0.08 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Right Leg -->
  <joint name="right_hip_joint" type="revolute">
    <parent link="pelvis"/>
    <child link="right_thigh"/>
    <origin xyz="0 -0.05 -0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/2}" upper="${pi/4}" effort="100" velocity="3.0"/>
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
        <capsule radius="0.06" length="0.2"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_knee_joint" type="revolute">
    <parent link="right_thigh"/>
    <child link="right_shin"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-pi/2}" upper="0" effort="100" velocity="3.0"/>
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
        <capsule radius="0.05" length="0.15"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.15"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_ankle_joint" type="revolute">
    <parent link="right_shin"/>
    <child link="right_foot"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
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
        <box size="0.18 0.08 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0.05 0 -0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.18 0.08 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- ros2_control configuration -->
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>

    <!-- Joints -->
    <joint name="neck_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_shoulder_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_elbow_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_wrist_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_shoulder_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_elbow_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_wrist_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_hip_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_knee_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="left_ankle_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_hip_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_knee_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>

    <joint name="right_ankle_joint">
      <command_interface name="position"/>
      <command_interface name="velocity"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>

  <!-- Gazebo plugins -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find isaac_humanoid_lab)/config/humanoid_control.yaml</parameters>
    </plugin>
  </gazebo>

  <!-- Sensors -->
  <gazebo reference="head">
    <!-- Camera for head -->
    <sensor name="head_camera" type="camera">
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.1</near>
          <far>100</far>
        </clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>image_raw:=camera/image_raw</remapping>
          <remapping>camera_info:=camera/camera_info</remapping>
        </ros>
        <frame_name>head</frame_name>
      </plugin>
    </sensor>

    <!-- IMU in head -->
    <sensor name="head_imu" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="imu_controller" filename="libgazebo_ros_imu.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>imu:=imu/data</remapping>
        </ros>
        <frame_name>head</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <!-- Force/Torque sensors in feet -->
  <gazebo reference="left_foot">
    <sensor name="left_foot_ft" type="force_torque">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="left_foot_ft_controller" filename="libgazebo_ros_force_torque.so">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>wrench:=left_foot/wrench</remapping>
        </ros>
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
        <frame_name>right_foot</frame_name>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

## Step 3: Create Control Configuration

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/config/humanoid_control.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    # Joint trajectory controllers for different parts
    neck_controller:
      type: position_controllers/JointGroupPositionController

    left_arm_controller:
      type: position_controllers/JointGroupPositionController

    right_arm_controller:
      type: position_controllers/JointGroupPositionController

    left_leg_controller:
      type: position_controllers/JointGroupPositionController

    right_leg_controller:
      type: position_controllers/JointGroupPositionController

    # Whole body controller
    whole_body_controller:
      type: velocity_controllers/JointGroupVelocityController

# Neck controller
neck_controller:
  ros__parameters:
    joints:
      - neck_joint

# Left arm controller
left_arm_controller:
  ros__parameters:
    joints:
      - left_shoulder_joint
      - left_elbow_joint
      - left_wrist_joint

# Right arm controller
right_arm_controller:
  ros__parameters:
    joints:
      - right_shoulder_joint
      - right_elbow_joint
      - right_wrist_joint

# Left leg controller
left_leg_controller:
  ros__parameters:
    joints:
      - left_hip_joint
      - left_knee_joint
      - left_ankle_joint

# Right leg controller
right_leg_controller:
  ros__parameters:
    joints:
      - right_hip_joint
      - right_knee_joint
      - right_ankle_joint

# Whole body controller
whole_body_controller:
  ros__parameters:
    joints:
      - neck_joint
      - left_shoulder_joint
      - left_elbow_joint
      - left_wrist_joint
      - right_shoulder_joint
      - right_elbow_joint
      - right_wrist_joint
      - left_hip_joint
      - left_knee_joint
      - left_ankle_joint
      - right_hip_joint
      - right_knee_joint
      - right_ankle_joint
```

## Step 4: Create the Main Controller Node

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/isaac_humanoid_lab/humanoid_controller.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import JointState, Imu, Image, LaserScan
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float64MultiArray
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.msg import JointTrajectoryControllerState
import numpy as np
import math
from collections import deque
import time

class IsaacHumanoidController(Node):
    def __init__(self):
        super().__init__('isaac_humanoid_controller')

        # Initialize robot state
        self.joint_positions = {}
        self.joint_velocities = {}
        self.joint_efforts = {}
        self.imu_data = None
        self.foot_force_data = {'left': None, 'right': None}
        self.camera_data = None

        # Balance control parameters
        self.com_height = 0.85  # Estimated CoM height
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Walking parameters
        self.step_height = 0.05
        self.step_length = 0.3
        self.step_duration = 0.8
        self.support_foot = 'left'  # Which foot is currently supporting
        self.swing_phase = 0.0  # Phase of swing leg (0.0 to 1.0)

        # Control parameters
        self.balance_kp = 100.0
        self.balance_kd = 10.0
        self.walking_kp = 50.0
        self.walking_kd = 5.0

        # Publishers
        self.joint_trajectory_pub = self.create_publisher(
            JointTrajectory, '/whole_body_controller/joint_trajectory', 10
        )

        self.cmd_vel_pub = self.create_publisher(
            Twist, '/humanoid/cmd_vel', 10
        )

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

        # Timer for control loop
        self.control_timer = self.create_timer(0.01, self.control_step)  # 100 Hz
        self.walking_timer = self.create_timer(0.001, self.walking_step)  # 1000 Hz for walking

        # State tracking
        self.balance_active = True
        self.walking_active = False
        self.standing_active = True

        # Walking trajectory generation
        self.walking_trajectory = deque(maxlen=100)
        self.step_counter = 0

        self.get_logger().info('Isaac Humanoid Controller initialized')

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

    def control_step(self):
        """Main control step executed at 100 Hz."""
        if not self.joint_positions:
            return

        # Calculate center of mass position and velocity
        com_pos, com_vel = self.calculate_com_state()

        # Balance control
        if self.balance_active:
            balance_torques = self.balance_control_step(com_pos, com_vel)
        else:
            balance_torques = np.zeros(12)  # 12 DOF for legs

        # Walking control
        if self.walking_active:
            walking_torques = self.walking_control_step()
        else:
            walking_torques = np.zeros(12)

        # Standing control
        if self.standing_active:
            standing_torques = self.standing_control_step()
        else:
            standing_torques = np.zeros(12)

        # Combine control efforts
        combined_torques = balance_torques + walking_torques + standing_torques

        # Publish joint commands
        self.publish_joint_commands(combined_torques)

    def calculate_com_state(self):
        """Calculate center of mass position and velocity."""
        # This would involve complex forward kinematics and center of mass calculation
        # For this example, we'll use a simplified approach

        # Get positions of key links (simplified)
        pelvis_pos = np.array([0.0, 0.0, 0.1])  # Simplified pelvis position
        torso_pos = np.array([0.0, 0.0, 0.35])  # Simplified torso position
        head_pos = np.array([0.0, 0.0, 0.75])   # Simplified head position

        # Calculate approximate CoM (weighted average)
        total_mass = 20.0  # Simplified total mass
        com_pos = (pelvis_pos * 5.0 + torso_pos * 10.0 + head_pos * 2.0) / total_mass

        # Calculate velocity (simplified)
        com_vel = np.array([0.0, 0.0, 0.0])  # Would need previous positions

        return com_pos, com_vel

    def balance_control_step(self, com_pos, com_vel):
        """Execute balance control step using ZMP control."""
        # Calculate current ZMP (simplified)
        zmp_x = com_pos[0] - (com_pos[2] / self.gravity) * com_vel[0]
        zmp_y = com_pos[1] - (com_pos[2] / self.gravity) * com_vel[1]

        # Desired ZMP (should be within support polygon)
        desired_zmp_x, desired_zmp_y = self.calculate_desired_zmp()

        # Calculate ZMP error
        zmp_error_x = desired_zmp_x - zmp_x
        zmp_error_y = desired_zmp_y - zmp_y

        # Balance control (simplified - in reality this would involve complex whole-body control)
        balance_torques = np.zeros(12)

        # Apply corrective torques to hip joints for balance
        balance_torques[0] = self.balance_kp * zmp_error_x  # Left hip roll
        balance_torques[3] = self.balance_kp * zmp_error_x  # Right hip roll
        balance_torques[1] = self.balance_kp * zmp_error_y  # Left hip pitch
        balance_torques[4] = self.balance_kp * zmp_error_y  # Right hip pitch

        return balance_torques

    def calculate_desired_zmp(self):
        """Calculate desired ZMP based on support polygon."""
        # Determine support polygon based on contact feet
        left_contact = self.foot_force_data['left'] is not None and abs(self.foot_force_data['left'].force.z) > 10.0
        right_contact = self.foot_force_data['right'] is not None and abs(self.foot_force_data['right'].force.z) > 10.0

        if left_contact and right_contact:
            # Double support - average of both feet
            left_foot_pos = self.get_foot_position('left')
            right_foot_pos = self.get_foot_position('right')
            desired_zmp = (left_foot_pos + right_foot_pos) / 2.0
        elif left_contact:
            # Left foot support
            desired_zmp = self.get_foot_position('left')
        elif right_contact:
            # Right foot support
            desired_zmp = self.get_foot_position('right')
        else:
            # No support (flying phase in walking)
            desired_zmp = np.array([0.0, 0.0])

        return desired_zmp[0], desired_zmp[1]

    def get_foot_position(self, foot):
        """Get foot position from forward kinematics."""
        # This would involve calculating forward kinematics
        # For this example, we'll return a simplified position
        if foot == 'left':
            return np.array([-0.05, 0.1, 0.0])  # Simplified left foot position
        else:  # right
            return np.array([-0.05, -0.1, 0.0])  # Simplified right foot position

    def walking_control_step(self):
        """Execute walking control step."""
        walking_torques = np.zeros(12)

        if not self.walking_active:
            return walking_torques

        # Generate walking pattern
        left_foot_traj, right_foot_traj = self.generate_walking_trajectory()

        # Calculate foot position errors
        current_left_pos = self.get_foot_position('left')
        current_right_pos = self.get_foot_position('right')

        left_error = left_foot_traj - current_left_pos
        right_error = right_foot_traj - current_right_pos

        # Apply walking control (simplified)
        walking_torques[0:3] = self.walking_kp * left_error[:3]  # Left leg
        walking_torques[3:6] = self.walking_kp * right_error[:3]  # Right leg

        return walking_torques

    def generate_walking_trajectory(self):
        """Generate walking trajectory for feet."""
        # This would implement a walking pattern generator
        # For this example, we'll use a simplified approach

        # Calculate time in gait cycle
        gait_phase = (time.time() / self.step_duration) % 2.0

        # Left foot trajectory
        if gait_phase < 1.0:  # Left foot is swing foot
            left_x = 0.0
            left_y = 0.1
            left_z = 0.05 * math.sin(math.pi * gait_phase)  # Swing motion
        else:  # Left foot is stance foot
            left_x = 0.3 * (gait_phase - 1.0)  # Forward progression
            left_y = 0.1
            left_z = 0.0

        # Right foot trajectory
        if gait_phase < 1.0:  # Right foot is stance foot
            right_x = 0.3 * gait_phase  # Forward progression
            right_y = -0.1
            right_z = 0.0
        else:  # Right foot is swing foot
            right_x = 0.3 * (gait_phase - 1.0)
            right_y = -0.1
            right_z = 0.05 * math.sin(math.pi * (gait_phase - 1.0))  # Swing motion

        left_foot_pos = np.array([left_x, left_y, left_z])
        right_foot_pos = np.array([right_x, right_y, right_z])

        return left_foot_pos, right_foot_pos

    def standing_control_step(self):
        """Execute standing control step."""
        standing_torques = np.zeros(12)

        # Maintain zero position for arms
        arm_joints = ['left_shoulder', 'left_elbow', 'left_wrist',
                     'right_shoulder', 'right_elbow', 'right_wrist']

        for i, joint in enumerate(arm_joints):
            if joint in self.joint_positions:
                current_pos = self.joint_positions[joint]
                # Simple PD control to maintain zero position
                pos_error = 0.0 - current_pos
                vel = self.joint_velocities.get(joint, 0.0)

                standing_torques[i + 6] = 50.0 * pos_error - 5.0 * vel  # Apply to arm joints (indices 6-11)

        return standing_torques

    def publish_joint_commands(self, torques):
        """Publish joint trajectory commands."""
        if not self.joint_positions:
            return

        # Create joint trajectory message
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.header.frame_id = 'base_link'

        # Define joint names
        joint_names = [
            'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
            'right_hip_joint', 'right_knee_joint', 'right_ankle_joint',
            'left_shoulder_joint', 'left_elbow_joint', 'left_wrist_joint',
            'right_shoulder_joint', 'right_elbow_joint', 'right_wrist_joint'
        ]

        trajectory_msg.joint_names = joint_names

        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = [0.0] * len(joint_names)  # Position commands
        point.velocities = [0.0] * len(joint_names)  # Velocity commands
        point.accelerations = [0.0] * len(joint_names)  # Acceleration commands
        point.effort = torques.tolist()  # Torque commands

        point.time_from_start = Duration(sec=0, nanosec=10000000)  # 10ms duration

        trajectory_msg.points = [point]

        self.joint_trajectory_pub.publish(trajectory_msg)

    def start_walking(self):
        """Start walking mode."""
        self.walking_active = True
        self.standing_active = False
        self.get_logger().info('Walking mode started')

    def stop_walking(self):
        """Stop walking mode."""
        self.walking_active = False
        self.standing_active = True
        self.get_logger().info('Walking mode stopped')

    def enable_balance_control(self):
        """Enable balance control."""
        self.balance_active = True
        self.get_logger().info('Balance control enabled')

    def disable_balance_control(self):
        """Disable balance control."""
        self.balance_active = False
        self.get_logger().info('Balance control disabled')

def main(args=None):
    rclpy.init(args=args)
    controller = IsaacHumanoidController()

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

## Step 5: Create Walking Pattern Generator

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/isaac_humanoid_lab/walking_pattern_generator.py`:

```python
import numpy as np
import math
from scipy import interpolate
from scipy.optimize import minimize

class WalkingPatternGenerator:
    def __init__(self):
        # Walking parameters
        self.step_height = 0.05  # meters
        self.step_length = 0.3   # meters
        self.step_width = 0.2    # meters (distance between feet)
        self.step_duration = 0.8 # seconds
        self.double_support_ratio = 0.2  # 20% of step in double support

        # Robot parameters
        self.com_height = 0.85   # Center of mass height
        self.gravity = 9.81
        self.omega = math.sqrt(self.gravity / self.com_height)

        # Current state
        self.current_support_foot = 'left'
        self.current_com_x = 0.0
        self.current_com_y = 0.0
        self.current_yaw = 0.0
        self.step_counter = 0

        # Generated trajectories
        self.com_trajectory = []
        self.foot_trajectories = {'left': [], 'right': []}
        self.zmp_trajectory = []

    def generate_walking_trajectory(self, steps, step_length=0.3, step_width=0.2, turn_angle=0.0):
        """
        Generate complete walking trajectory for a specified number of steps.

        Args:
            steps: Number of steps to generate
            step_length: Forward step length (m)
            step_width: Lateral step width (m)
            turn_angle: Turning angle per step (rad)
        """
        # Initialize trajectory containers
        self.com_trajectory = []
        self.foot_trajectories = {'left': [], 'right': []}
        self.zmp_trajectory = []

        # Start position
        com_x, com_y, com_z = 0.0, 0.0, self.com_height
        support_foot = 'left'  # Start with left foot support

        for step in range(steps):
            # Determine swing foot
            swing_foot = 'right' if support_foot == 'left' else 'left'

            # Calculate step destination
            target_x = com_x + step_length * math.cos(self.current_yaw)
            target_y = com_y + step_length * math.sin(self.current_yaw)
            target_yaw = self.current_yaw + turn_angle

            # Generate single step trajectory
            step_data = self.generate_single_step(
                support_foot, swing_foot,
                (com_x, com_y), (target_x, target_y),
                self.current_yaw, target_yaw
            )

            # Update current state
            com_x, com_y = target_x, target_y
            self.current_yaw = target_yaw

            # Toggle support foot
            support_foot = 'right' if support_foot == 'left' else 'left'

            # Append to overall trajectories
            self.append_step_to_trajectories(step_data)

        return {
            'com_trajectory': self.com_trajectory,
            'foot_trajectories': self.foot_trajectories,
            'zmp_trajectory': self.zmp_trajectory
        }

    def generate_single_step(self, support_foot, swing_foot, start_pos, end_pos, start_yaw, end_yaw):
        """
        Generate trajectory for a single step.
        """
        # Calculate step midpoint and apex
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2

        # Swing foot trajectory (elliptical arc for lifting and lowering)
        swing_trajectory = self.generate_swing_foot_trajectory(
            start_pos, end_pos, self.step_height, support_foot
        )

        # Calculate CoM trajectory using inverted pendulum model
        com_trajectory = self.calculate_com_trajectory(
            start_pos, end_pos, self.com_height
        )

        # Calculate ZMP trajectory
        zmp_trajectory = self.calculate_zmp_trajectory(com_trajectory)

        return {
            'swing_foot_trajectory': swing_trajectory,
            'com_trajectory': com_trajectory,
            'zmp_trajectory': zmp_trajectory,
            'support_foot': support_foot,
            'swing_foot': swing_foot
        }

    def generate_swing_foot_trajectory(self, start_pos, end_pos, step_height, support_foot):
        """
        Generate swing foot trajectory using elliptical arc.
        """
        trajectory = []

        # Determine support foot lateral position
        support_lateral = self.step_width / 2 if support_foot == 'right' else -self.step_width / 2

        # Time steps
        n_points = int(self.step_duration * 100)  # 100 Hz resolution
        dt = self.step_duration / n_points

        for i in range(n_points + 1):
            t = i / n_points  # Normalized time (0 to 1)

            # Calculate swing foot position
            # Lateral movement (side-to-side)
            lateral_pos = support_lateral

            # Forward movement (using cubic interpolation)
            forward_pos = start_pos[0] + (end_pos[0] - start_pos[0]) * t

            # Lateral movement (for turning)
            if start_pos[1] != end_pos[1]:
                lateral_pos = start_pos[1] + (end_pos[1] - start_pos[1]) * t

            # Vertical movement (elliptical arc)
            vertical_offset = 0.0
            if 0.2 < t < 0.8:  # Lift foot during middle portion
                lift_phase = (t - 0.2) / 0.6  # Normalize to 0-1 for lift phase
                # Use sine function for smooth lift and land
                vertical_offset = step_height * math.sin(math.pi * lift_phase)

            foot_pos = np.array([forward_pos, lateral_pos, vertical_offset])
            trajectory.append({
                'time': i * dt,
                'position': foot_pos,
                'velocity': self.calculate_foot_velocity(trajectory, i, dt) if i > 0 else np.zeros(3)
            })

        return trajectory

    def calculate_com_trajectory(self, start_pos, end_pos, height):
        """
        Calculate CoM trajectory using Linear Inverted Pendulum Model (LIPM).
        """
        trajectory = []

        # For LIPM, CoM follows a curved path between steps
        # Using the fact that CoM moves in a straight line in the ZMP space
        n_points = int(self.step_duration * 100)  # 100 Hz resolution
        dt = self.step_duration / n_points

        for i in range(n_points + 1):
            t = i / n_points  # Normalized time (0 to 1)

            # CoM moves from current position toward target
            # Using exponential decay toward capture point
            cp_x = end_pos[0] - 0.1  # Capture point slightly behind target
            cp_y = end_pos[1]

            # LIPM solution: CoM position follows exponential trajectory
            exp_factor = math.exp(self.omega * (t * self.step_duration))

            # Calculate CoM position using LIPM
            com_x = cp_x + (start_pos[0] - cp_x) * math.exp(-self.omega * t * self.step_duration/2)
            com_y = cp_y + (start_pos[1] - cp_y) * math.exp(-self.omega * t * self.step_duration/2)
            com_z = height  # Keep CoM height constant (simplified)

            trajectory.append({
                'time': i * dt,
                'position': np.array([com_x, com_y, com_z]),
                'velocity': self.calculate_com_velocity(trajectory, i, dt) if i > 0 else np.zeros(3)
            })

        return trajectory

    def calculate_zmp_trajectory(self, com_trajectory):
        """
        Calculate ZMP trajectory from CoM trajectory.
        ZMP = CoM - (h/g) * CoM_acceleration
        """
        zmp_trajectory = []

        for i, com_point in enumerate(com_trajectory):
            if i < 2:  # Need at least 2 previous points for acceleration
                zmp_trajectory.append({
                    'time': com_point['time'],
                    'position': com_point['position'][:2]  # Start with CoM position
                })
                continue

            # Calculate CoM acceleration using finite differences
            dt = com_trajectory[i]['time'] - com_trajectory[i-1]['time']
            if dt <= 0:
                dt = 0.01  # Default time step

            # Velocity from position differences
            com_vel_current = (com_trajectory[i]['position'] - com_trajectory[i-1]['position']) / dt
            com_vel_prev = (com_trajectory[i-1]['position'] - com_trajectory[i-2]['position']) / dt

            # Acceleration from velocity differences
            com_acc = (com_vel_current - com_vel_prev) / dt

            # Calculate ZMP
            zmp_x = com_trajectory[i]['position'][0] - (self.com_height / self.gravity) * com_acc[0]
            zmp_y = com_trajectory[i]['position'][1] - (self.com_height / self.gravity) * com_acc[1]

            zmp_trajectory.append({
                'time': com_point['time'],
                'position': np.array([zmp_x, zmp_y])
            })

        return zmp_trajectory

    def calculate_foot_velocity(self, trajectory, index, dt):
        """Calculate foot velocity from position trajectory."""
        if index == 0 or len(trajectory) < 2:
            return np.zeros(3)

        pos_current = trajectory[index]['position']
        pos_previous = trajectory[index-1]['position']

        velocity = (pos_current - pos_previous) / dt
        return velocity

    def calculate_com_velocity(self, trajectory, index, dt):
        """Calculate CoM velocity from position trajectory."""
        if index == 0 or len(trajectory) < 2:
            return np.zeros(3)

        pos_current = trajectory[index]['position']
        pos_previous = trajectory[index-1]['position']

        velocity = (pos_current - pos_previous) / dt
        return velocity

    def generate_ankle_trajectories(self):
        """
        Generate ankle joint trajectories to achieve desired foot positions.
        This would involve inverse kinematics in a real implementation.
        """
        ankle_trajectories = {'left': [], 'right': []}

        # For each time step in the foot trajectories, calculate required ankle positions
        # This is a simplified placeholder - real implementation would use IK
        for foot in ['left', 'right']:
            for foot_point in self.foot_trajectories[foot]:
                # Inverse kinematics would go here
                # For now, we'll just store the foot position as-is
                ankle_trajectories[foot].append(foot_point)

        return ankle_trajectories

    def optimize_walking_trajectory(self):
        """
        Optimize walking trajectory using trajectory optimization.
        Minimize ZMP deviation from desired path while respecting constraints.
        """
        # Define optimization variables (simplified)
        # In reality, this would be much more complex

        def objective_function(params):
            """
            Objective function to minimize ZMP deviation and energy.
            params: Optimizable parameters for the walking pattern
            """
            # Calculate resulting trajectories with these parameters
            # Calculate ZMP error
            # Calculate energy cost
            # Return weighted sum
            return 0.0  # Placeholder

        # Optimization bounds (example)
        bounds = [
            (0.2, 0.4),  # Step length bounds
            (0.1, 0.3),  # Step width bounds
            (0.02, 0.1), # Step height bounds
            (0.5, 1.0)   # Step duration bounds
        ]

        # Initial guess
        initial_guess = [self.step_length, self.step_width, self.step_height, self.step_duration]

        # Run optimization (this is a simplified example)
        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=[]  # Add constraints as needed
            )

            if result.success:
                # Update walking parameters with optimized values
                (self.step_length, self.step_width,
                 self.step_height, self.step_duration) = result.x

                self.get_logger().info(f'Walking parameters optimized: {result.x}')
            else:
                self.get_logger().warn(f'Optimization failed: {result.message}')

        except Exception as e:
            self.get_logger().error(f'Optimization error: {e}')

    def get_support_polygon(self, time):
        """
        Get the support polygon at a specific time during the walking cycle.
        """
        # Determine which feet are in contact at this time
        gait_phase = (time % (2 * self.step_duration)) / (2 * self.step_duration)

        if gait_phase < 0.5:  # First half: left foot support phase
            support_vertices = self.get_foot_support_area('left')
        elif gait_phase < 1.0:  # Second half: right foot support phase
            support_vertices = self.get_foot_support_area('right')
        elif gait_phase < 1.5:  # Third quarter: right foot support
            support_vertices = self.get_foot_support_area('right')
        else:  # Fourth quarter: left foot support
            support_vertices = self.get_foot_support_area('left')

        return support_vertices

    def get_foot_support_area(self, foot):
        """
        Get the support area for a foot (simplified as rectangle).
        """
        # Simplified rectangular support area
        if foot == 'left':
            # Left foot support polygon vertices
            return np.array([
                [-0.1, 0.1],   # front-left
                [0.1, 0.1],    # front-right
                [0.1, -0.1],   # back-right
                [-0.1, -0.1]   # back-left
            ])
        else:  # right foot
            return np.array([
                [-0.1, 0.1],   # front-left
                [0.1, 0.1],    # front-right
                [0.1, -0.1],   # back-right
                [-0.1, -0.1]   # back-left
            ])

    def is_zmp_stable(self, zmp_position, time):
        """
        Check if ZMP is within support polygon at given time.
        """
        support_polygon = self.get_support_polygon(time)

        # Check if ZMP is inside support polygon using ray casting
        x, y = zmp_position
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

    def adjust_for_balance(self, original_trajectory):
        """
        Adjust trajectory to maintain balance if ZMP goes outside support polygon.
        """
        adjusted_trajectory = []

        for point in original_trajectory:
            zmp_pos = point['zmp_position']
            time = point['time']

            if not self.is_zmp_stable(zmp_pos, time):
                # Adjust CoM trajectory to bring ZMP back to stability region
                adjusted_point = point.copy()

                # Simple adjustment: move CoM toward ZMP
                com_pos = point['com_position']
                adjustment_vector = (zmp_pos - com_pos[:2]) * 0.1  # Small adjustment
                adjusted_point['com_position'][:2] = com_pos[:2] + adjustment_vector

                # Recalculate ZMP with adjusted CoM
                adjusted_zmp = self.calculate_zmp_from_com(
                    adjusted_point['com_position'],
                    point['com_acceleration']
                )
                adjusted_point['zmp_position'] = adjusted_zmp

                adjusted_trajectory.append(adjusted_point)
            else:
                adjusted_trajectory.append(point)

        return adjusted_trajectory

    def calculate_zmp_from_com(self, com_pos, com_acc):
        """Calculate ZMP from CoM position and acceleration."""
        zmp_x = com_pos[0] - (self.com_height / self.gravity) * com_acc[0]
        zmp_y = com_pos[1] - (self.com_height / self.gravity) * com_acc[1]
        return np.array([zmp_x, zmp_y])
```

## Step 6: Create the Main Launch File

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/launch/humanoid_sim_launch.py`:

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
    world = LaunchConfiguration('world', default='empty')

    # Package names
    pkg_isaac_humanoid_lab = FindPackageShare('isaac_humanoid_lab')
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
                FindPackageShare('isaac_humanoid_lab'),
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
                    FindPackageShare('isaac_humanoid_lab'),
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

    # Load controllers
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    load_whole_body_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['whole_body_controller'],
        output='screen',
    )

    # Humanoid controller
    humanoid_controller = Node(
        package='isaac_humanoid_lab',
        executable='humanoid_controller',
        name='humanoid_controller',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Walking pattern generator
    walking_generator = Node(
        package='isaac_humanoid_lab',
        executable='walking_pattern_generator',
        name='walking_generator',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # RViz for visualization
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('isaac_humanoid_lab'),
        'rviz',
        'humanoid_sim.rviz'
    ])

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
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
            default_value='empty',
            description='Choose one of the world files from `/isaac_humanoid_lab/worlds`'
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
                load_whole_body_controller
            ]
        ),

        # Launch controllers after they're loaded
        TimerAction(
            period=9.0,
            actions=[
                humanoid_controller,
                walking_generator
            ]
        ),

        # Launch RViz
        TimerAction(
            period=11.0,
            actions=[rviz]
        )
    ])
```

## Step 7: Create a Simple Demo Node

Create `~/ros2_lab_ws/src/isaac_humanoid_lab/isaac_humanoid_lab/demo_node.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import time
import math

class HumanoidDemoNode(Node):
    def __init__(self):
        super().__init__('humanoid_demo_node')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/humanoid/cmd_vel', 10)
        self.demo_state_pub = self.create_publisher(String, '/demo/state', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        # Timer for demo sequence
        self.demo_timer = self.create_timer(0.1, self.demo_step)
        self.demo_state = 'waiting'  # waiting, walking, balancing, waving
        self.demo_start_time = time.time()
        self.demo_sequence = [
            'init', 'wave', 'walk_forward', 'turn', 'balance', 'stop'
        ]
        self.current_demo_step = 0

        # Joint state storage
        self.joint_positions = {}
        self.joint_velocities = {}

        self.get_logger().info('Humanoid Demo Node initialized')

    def joint_state_callback(self, msg):
        """Update joint state information."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]
            if i < len(msg.velocity):
                self.joint_velocities[name] = msg.velocity[i]

    def demo_step(self):
        """Execute demo sequence step."""
        if self.current_demo_step >= len(self.demo_sequence):
            return

        current_step = self.demo_sequence[self.current_demo_step]
        elapsed_time = time.time() - self.demo_start_time

        if current_step == 'init':
            if elapsed_time > 2.0:  # Wait 2 seconds
                self.current_demo_step += 1
                self.demo_start_time = time.time()
                self.get_logger().info('Moving to next demo step: wave')

        elif current_step == 'wave':
            self.execute_waving_motion(elapsed_time)
            if elapsed_time > 5.0:  # Wave for 5 seconds
                self.current_demo_step += 1
                self.demo_start_time = time.time()
                self.get_logger().info('Moving to next demo step: walk_forward')

        elif current_step == 'walk_forward':
            self.execute_walking_motion(elapsed_time)
            if elapsed_time > 8.0:  # Walk for 8 seconds
                self.current_demo_step += 1
                self.demo_start_time = time.time()
                self.get_logger().info('Moving to next demo step: turn')

        elif current_step == 'turn':
            self.execute_turning_motion(elapsed_time)
            if elapsed_time > 6.0:  # Turn for 6 seconds
                self.current_demo_step += 1
                self.demo_start_time = time.time()
                self.get_logger().info('Moving to next demo step: balance')

        elif current_step == 'balance':
            self.execute_balancing_motion(elapsed_time)
            if elapsed_time > 5.0:  # Balance for 5 seconds
                self.current_demo_step += 1
                self.demo_start_time = time.time()
                self.get_logger().info('Moving to next demo step: stop')

        elif current_step == 'stop':
            self.stop_motion()
            self.get_logger().info('Demo sequence completed')

        # Publish demo state
        state_msg = String()
        state_msg.data = f"{current_step}_{self.current_demo_step}"
        self.demo_state_pub.publish(state_msg)

    def execute_waving_motion(self, elapsed_time):
        """Execute waving motion with right arm."""
        cmd_vel = Twist()

        # Calculate waving motion using sinusoidal function
        wave_freq = 1.0  # Hz
        wave_amplitude = 0.5  # rad/s

        # For this example, we'll send simple velocity commands
        # In a real implementation, this would send joint trajectory commands
        wave_vel = wave_amplitude * math.sin(2 * math.pi * wave_freq * elapsed_time)

        # Send command (this would be more complex in reality)
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd_vel)

    def execute_walking_motion(self, elapsed_time):
        """Execute walking motion."""
        cmd_vel = Twist()

        # Simple forward walking command
        cmd_vel.linear.x = 0.3  # 0.3 m/s forward
        cmd_vel.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd_vel)

    def execute_turning_motion(self, elapsed_time):
        """Execute turning motion."""
        cmd_vel = Twist()

        # Simple turning command
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.2  # 0.2 rad/s turn

        self.cmd_vel_pub.publish(cmd_vel)

    def execute_balancing_motion(self, elapsed_time):
        """Execute balancing motion."""
        cmd_vel = Twist()

        # Send small corrective motions to demonstrate balance
        balance_freq = 0.5
        balance_amplitude = 0.1

        correction = balance_amplitude * math.sin(2 * math.pi * balance_freq * elapsed_time)

        cmd_vel.linear.x = correction
        cmd_vel.angular.z = correction * 0.5

        self.cmd_vel_pub.publish(cmd_vel)

    def stop_motion(self):
        """Stop all robot motion."""
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.linear.y = 0.0
        cmd_vel.linear.z = 0.0
        cmd_vel.angular.x = 0.0
        cmd_vel.angular.y = 0.0
        cmd_vel.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    demo_node = HumanoidDemoNode()

    try:
        rclpy.spin(demo_node)
    except KeyboardInterrupt:
        demo_node.get_logger().info('Shutting down demo node...')
    finally:
        demo_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 8: Update Package Files

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_humanoid_lab'

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
    description='Isaac Sim Humanoid Robot Lab Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'humanoid_controller = isaac_humanoid_lab.humanoid_controller:main',
            'walking_pattern_generator = isaac_humanoid_lab.walking_pattern_generator:main',
            'demo_node = isaac_humanoid_lab.demo_node:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>isaac_humanoid_lab</name>
  <version>0.0.0</version>
  <description>Isaac Sim Humanoid Robot Lab Package</description>
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

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Step 9: Build and Test the Package

```bash
# Go to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select isaac_humanoid_lab

# Source the workspace
source install/setup.bash

# Test the build
ros2 run isaac_humanoid_lab demo_node
```

## Lab Exercise Steps

1. **Build the complete system**: Build all components of the humanoid simulation
2. **Test individual components**: Verify that each subsystem (balance, walking, sensors) works independently
3. **Integrate and test**: Combine all systems and test the complete humanoid behavior
4. **Tune parameters**: Adjust control parameters for stable walking
5. **Validate performance**: Test in various scenarios and environments

## Lab Questions

1. How does the Linear Inverted Pendulum Model (LIPM) simplify walking control for humanoid robots?
2. What are the key challenges in maintaining balance during walking?
3. How does the ZMP-based control ensure stable locomotion?
4. What role does the walking pattern generator play in humanoid locomotion?
5. How could you extend this system to handle uneven terrain?

## Summary

This lab demonstrated the integration of multiple complex systems required for humanoid robot simulation:
- Dynamics modeling with ros2_control
- Balance control using ZMP theory
- Walking pattern generation with LIPM
- Sensor integration for perception
- Whole-body control for coordinated motion

The combination of these systems enables realistic humanoid simulation in Isaac Sim, providing a platform for testing complex robotic behaviors before deployment on real hardware.