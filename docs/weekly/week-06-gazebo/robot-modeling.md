---
sidebar_label: 'Robot Modeling and URDF Integration'
title: 'Robot Modeling and URDF Integration'
---

# Robot Modeling and URDF Integration in Gazebo

## Introduction to Robot Modeling

Robot modeling in Gazebo involves creating accurate 3D representations of robots with proper physics properties, joints, and sensors. The most common approach is to use URDF (Unified Robot Description Format) combined with SDF for Gazebo-specific extensions.

## URDF vs SDF for Robot Modeling

### URDF (Unified Robot Description Format)
- **Primary use**: Robot kinematic and dynamic description
- **Format**: XML-based
- **ROS integration**: Native ROS support
- **Limitations**: Limited physics simulation features

### SDF (Simulation Description Format)
- **Primary use**: Gazebo-specific simulation features
- **Format**: XML-based
- **Features**: Advanced physics, sensors, plugins
- **Flexibility**: More comprehensive than URDF

## Basic URDF Robot Structure

### Simple Wheeled Robot Example

```xml
<?xml version="1.0"?>
<robot name="simple_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.2" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.2" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Left wheel -->
  <link name="left_wheel">
    <inertial>
      <mass value="0.2"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Right wheel -->
  <link name="right_wheel">
    <inertial>
      <mass value="0.2"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Joints -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.15 -0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.15 -0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
</robot>
```

## Gazebo-Specific Extensions

### Adding Gazebo Elements to URDF

```xml
<?xml version="1.0"?>
<robot name="gazebo_robot">
  <!-- Links and joints as before -->
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.2" length="0.1"/>
      </geometry>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.2" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Gazebo-specific elements -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
    <self_collide>false</self_collide>
    <gravity>true</gravity>
    <max_contacts>10</max_contacts>
  </gazebo>

  <!-- Gazebo plugins -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <update_rate>30</update_rate>
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>0.3</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
```

## Advanced Robot Models

### Multi-Joint Manipulator

```xml
<?xml version="1.0"?>
<robot name="manipulator_robot">
  <!-- Base -->
  <link name="base_link">
    <inertial>
      <mass value="5.0"/>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.2"/>
      </geometry>
      <material name="base_material">
        <color rgba="0.7 0.7 0.7 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <!-- Shoulder joint -->
  <link name="shoulder_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.02"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
      <material name="link_material">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
    </collision>
  </link>

  <joint name="shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_link"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
    <safety_controller k_position="20" k_velocity="500" soft_lower_limit="-1.5" soft_upper_limit="1.5"/>
  </joint>

  <!-- Elbow joint -->
  <link name="elbow_link">
    <inertial>
      <mass value="1.5"/>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <inertia ixx="0.03" ixy="0.0" ixz="0.0" iyy="0.03" iyz="0.0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.2"/>
      </geometry>
      <material name="link_material"/>
    </visual>

    <collision>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.2"/>
      </geometry>
    </collision>
  </link>

  <joint name="elbow_joint" type="revolute">
    <parent link="shoulder_link"/>
    <child link="elbow_link"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <!-- Gazebo elements for the manipulator -->
  <gazebo reference="base_link">
    <material>Gazebo/Grey</material>
  </gazebo>

  <gazebo reference="shoulder_link">
    <material>Gazebo/Grey</material>
  </gazebo>

  <gazebo reference="elbow_link">
    <material>Gazebo/Grey</material>
  </gazebo>

  <!-- Joint state publisher plugin -->
  <gazebo>
    <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>joint_states:=joint_states</remapping>
      </ros>
      <update_rate>30</update_rate>
      <joint_name>shoulder_joint</joint_name>
      <joint_name>elbow_joint</joint_name>
    </plugin>
  </gazebo>
</robot>
```

## Adding Sensors to Robots

### Camera Sensor

```xml
<link name="camera_link">
  <inertial>
    <mass value="0.1"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
  </inertial>

  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
    <material name="black">
      <color rgba="0 0 0 1"/>
    </material>
  </visual>

  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </collision>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.15 0 0.1" rpy="0 0 0"/>
</joint>

<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <camera name="head">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>800</width>
        <height>600</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>image_raw:=camera/image_raw</remapping>
        <remapping>camera_info:=camera/camera_info</remapping>
      </ros>
      <camera_name>camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### LIDAR Sensor

```xml
<link name="lidar_link">
  <inertial>
    <mass value="0.2"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
  </inertial>

  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.03" length="0.03"/>
    </geometry>
    <material name="silver">
      <color rgba="0.7 0.7 0.7 1"/>
    </material>
  </visual>

  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.03" length="0.03"/>
    </geometry>
  </collision>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0.1 0 0.15" rpy="0 0 0"/>
</joint>

<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>40</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-1.570796</min_angle>
          <max_angle>1.570796</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>scan:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## Xacro for Complex Robots

Xacro (XML Macros) allows for more maintainable and reusable robot descriptions:

```xml
<?xml version="1.0"?>
<robot name="xacro_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Properties -->
  <xacro:property name="base_radius" value="0.2"/>
  <xacro:property name="base_length" value="0.1"/>
  <xacro:property name="wheel_radius" value="0.1"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="wheel_offset" value="0.15"/>

  <!-- Macro for wheels -->
  <xacro:macro name="wheel" params="prefix parent xyz rpy">
    <link name="${prefix}_wheel">
      <inertial>
        <mass value="0.2"/>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
      </inertial>

      <visual>
        <origin xyz="0 0 0" rpy="1.570796 0 0"/>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
        <material name="black">
          <color rgba="0 0 0 1"/>
        </material>
      </visual>

      <collision>
        <origin xyz="0 0 0" rpy="1.570796 0 0"/>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
    </link>

    <joint name="${prefix}_wheel_joint" type="continuous">
      <parent link="${parent}"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="${xyz}" rpy="${rpy}"/>
      <axis xyz="0 1 0"/>
    </joint>
  </xacro:macro>

  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="${base_radius}" length="${base_length}"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="${base_radius}" length="${base_length}"/>
      </geometry>
    </collision>
  </link>

  <!-- Use the wheel macro -->
  <xacro:wheel prefix="left" parent="base_link"
                xyz="0 ${wheel_offset} -0.05" rpy="0 0 0"/>
  <xacro:wheel prefix="right" parent="base_link"
                xyz="0 -${wheel_offset} -0.05" rpy="0 0 0"/>

  <!-- Gazebo elements -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="left_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <gazebo reference="right_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <!-- Differential drive plugin -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>robot</namespace>
      </ros>
      <update_rate>30</update_rate>
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>0.3</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
```

## Physics Properties and Tuning

### Inertial Properties

```xml
<link name="custom_link">
  <inertial>
    <!-- Mass of the link in kg -->
    <mass value="2.0"/>

    <!-- Origin of the inertial reference frame -->
    <origin xyz="0.1 0.0 0.05" rpy="0 0 0"/>

    <!-- Inertia matrix -->
    <inertia ixx="0.05" ixy="0.0" ixz="0.0"
             iyy="0.03" iyz="0.0" izz="0.02"/>
  </inertial>
</link>
```

### Gazebo-Specific Physics

```xml
<gazebo reference="custom_link">
  <!-- Material properties -->
  <material>Gazebo/Orange</material>

  <!-- Friction coefficients -->
  <mu1>0.5</mu1>
  <mu2>0.5</mu2>

  <!-- Bounce properties -->
  <kp>1000000.0</kp>  <!-- Spring stiffness -->
  <kd>1.0</kd>        <!-- Damping coefficient -->

  <!-- Self-collision -->
  <self_collide>false</self_collide>

  <!-- Gravity -->
  <gravity>true</gravity>

  <!-- Maximum contacts -->
  <max_contacts>10</max_contacts>

  <!-- Surface properties -->
  <surface>
    <friction>
      <ode>
        <mu>0.5</mu>
        <mu2>0.5</mu2>
        <fdir1>0 0 1</fdir1>
      </ode>
    </friction>
  </surface>
</gazebo>
```

## Best Practices

1. **Accurate inertial properties**: Calculate or estimate mass and inertia properly
2. **Collision vs visual**: Use simpler geometry for collision than visual when possible
3. **Joint limits**: Set appropriate joint limits and safety controllers
4. **Xacro for complexity**: Use Xacro for reusable and maintainable robot descriptions
5. **Testing**: Test robot models in simulation before using on real hardware
6. **Documentation**: Document the purpose and parameters of each link and joint
7. **Modularity**: Design robots in modular components for easier maintenance

## Common Issues and Solutions

### Robot Falls Through Ground
- Check that base link has proper mass and inertia
- Ensure collision geometry is defined for all links
- Verify that static property is set correctly

### Robot Jitters or Behaves Unpredictably
- Check joint limits and safety controllers
- Verify physics parameters (time step, solver parameters)
- Ensure proper mass distribution

### Performance Issues
- Simplify collision geometry where possible
- Reduce physics update rate if appropriate
- Use appropriate solver settings

## Summary

Robot modeling in Gazebo requires combining URDF for kinematic structure with Gazebo-specific extensions for simulation. Proper inertial properties, collision geometry, and plugins are essential for realistic simulation. Using Xacro helps create maintainable and reusable robot descriptions for complex systems.