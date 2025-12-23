---
sidebar_label: 'Week 6 Lab: Creating a Simulated Robot'
title: 'Week 6 Lab: Creating a Simulated Robot'
---

# Week 6 Lab: Creating a Simulated Robot

## Objective

In this lab, you will create a complete simulated robot with multiple sensors in Gazebo. You'll learn how to model a robot, add sensors, configure plugins, and test the simulation with ROS 2.

## Prerequisites

- Completion of Weeks 1-5 labs
- ROS 2 Humble Hawksbill installed
- Gazebo Classic or Gazebo Garden installed
- Basic knowledge of URDF and XML

## Step 1: Create a Robot Description Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a robot description package
ros2 pkg create --build-type ament_cmake sim_robot_description --dependencies urdf xacro
```

## Step 2: Create the Robot URDF

Create the main robot description file:

```bash
mkdir -p ~/ros2_lab_ws/src/sim_robot_description/urdf
```

Create `~/ros2_lab_ws/src/sim_robot_description/urdf/sim_robot.urdf.xacro`:

```xml
<?xml version="1.0"?>
<robot name="sim_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Properties -->
  <xacro:property name="base_width" value="0.4"/>
  <xacro:property name="base_length" value="0.6"/>
  <xacro:property name="base_height" value="0.2"/>
  <xacro:property name="wheel_radius" value="0.1"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="wheel_offset_x" value="0.2"/>
  <xacro:property name="wheel_offset_y" value="0.25"/>

  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="0.4167" ixy="0.0" ixz="0.0"
        iyy="0.2083" iyz="0.0"
        izz="0.2083"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
    </collision>
  </link>

  <!-- Macro for wheels -->
  <xacro:macro name="wheel" params="prefix side">
    <link name="${prefix}_${side}_wheel">
      <inertial>
        <mass value="1.0"/>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <inertia
          ixx="0.01" ixy="0.0" ixz="0.0"
          iyy="0.01" iyz="0.0"
          izz="0.02"/>
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

    <joint name="${prefix}_${side}_wheel_joint" type="continuous">
      <parent link="base_link"/>
      <child link="${prefix}_${side}_wheel"/>
      <origin xyz="${wheel_offset_x} ${wheel_offset_y if side == 'right' else -wheel_offset_y} 0" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
    </joint>
  </xacro:macro>

  <!-- Create wheels using macro -->
  <xacro:wheel prefix="front" side="left"/>
  <xacro:wheel prefix="front" side="right"/>
  <xacro:wheel prefix="rear" side="left"/>
  <xacro:wheel prefix="rear" side="right"/>

  <!-- Camera link -->
  <link name="camera_link">
    <inertial>
      <mass value="0.1"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="0.001" ixy="0.0" ixz="0.0"
        iyy="0.001" iyz="0.0"
        izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
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
    <origin xyz="${base_length/2 - 0.025} 0 ${base_height/2}" rpy="0 0 0"/>
  </joint>

  <!-- LIDAR link -->
  <link name="lidar_link">
    <inertial>
      <mass value="0.2"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="0.001" ixy="0.0" ixz="0.0"
        iyy="0.001" iyz="0.0"
        izz="0.001"/>
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
    <origin xyz="0 0 ${base_height/2 + 0.05}" rpy="0 0 0"/>
  </joint>

  <!-- Gazebo-specific elements -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="front_left_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <gazebo reference="front_right_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <gazebo reference="rear_left_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <gazebo reference="rear_right_wheel">
    <material>Gazebo/Black</material>
  </gazebo>

  <gazebo reference="camera_link">
    <material>Gazebo/Red</material>
  </gazebo>

  <gazebo reference="lidar_link">
    <material>Gazebo/Grey</material>
  </gazebo>

  <!-- Differential drive plugin -->
  <gazebo>
    <plugin name="sim_robot_diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>sim_robot</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
        <remapping>joint_states:=joint_states</remapping>
      </ros>
      <update_rate>30</update_rate>
      <left_joint>front_left_wheel_joint</left_joint>
      <right_joint>front_right_wheel_joint</right_joint>
      <wheel_separation>0.5</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>true</publish_wheel_tf>
    </plugin>
  </gazebo>

  <!-- Joint state publisher -->
  <gazebo>
    <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
      <ros>
        <namespace>sim_robot</namespace>
        <remapping>joint_states:=joint_states</remapping>
      </ros>
      <update_rate>30</update_rate>
      <joint_name>front_left_wheel_joint</joint_name>
      <joint_name>front_right_wheel_joint</joint_name>
      <joint_name>rear_left_wheel_joint</joint_name>
      <joint_name>rear_right_wheel_joint</joint_name>
    </plugin>
  </gazebo>

  <!-- Camera sensor -->
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
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
          <namespace>sim_robot</namespace>
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

  <!-- LIDAR sensor -->
  <gazebo reference="lidar_link">
    <sensor name="lidar" type="ray">
      <always_on>true</always_on>
      <update_rate>40</update_rate>
      <ray>
        <scan>
          <horizontal>
            <samples>360</samples>
            <resolution>1</resolution>
            <min_angle>-3.14159</min_angle>
            <max_angle>3.14159</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.1</min>
          <max>30.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <plugin name="lidar_controller" filename="libgazebo_ros_laser.so">
        <ros>
          <namespace>sim_robot</namespace>
          <remapping>scan:=scan</remapping>
        </ros>
        <topic_name>scan</topic_name>
        <frame_name>lidar_link</frame_name>
        <min_range>0.1</min_range>
        <max_range>30.0</max_range>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

## Step 3: Create Launch Files

Create the launch directory and files:

```bash
mkdir -p ~/ros2_lab_ws/src/sim_robot_description/launch
```

Create `~/ros2_lab_ws/src/sim_robot_description/launch/robot_spawn_launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Get URDF path
    pkg_share = FindPackageShare('sim_robot_description').find('sim_robot_description')
    urdf_path = os.path.join(pkg_share, 'urdf', 'sim_robot.urdf.xacro')

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
                FindPackageShare('sim_robot_description'),
                'worlds',
                'simple_room.world'
            ])
        }.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': open(urdf_path).read()
        }]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'sim_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity
    ])
```

## Step 4: Create a World File

Create the worlds directory and a simple room world:

```bash
mkdir -p ~/ros2_lab_ws/src/sim_robot_description/worlds
```

Create `~/ros2_lab_ws/src/sim_robot_description/worlds/simple_room.world`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="simple_room">
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Sun -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Walls -->
    <model name="wall_1">
      <pose>0 5 1 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>10 0.2 2</size></box></geometry>
          <material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <model name="wall_2">
      <pose>0 -5 1 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>10 0.2 2</size></box></geometry>
          <material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <model name="wall_3">
      <pose>5 0 1 1.5707 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>10 0.2 2</size></box></geometry>
          <material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <model name="wall_4">
      <pose>-5 0 1 1.5707 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>10 0.2 2</size></box></geometry>
          <material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <!-- Obstacle -->
    <model name="obstacle">
      <pose>2 2 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>1 1 1</size></box></geometry>
          <material><ambient>1 0 0 1</ambient><diffuse>1 0 0 1</diffuse></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>1 1 1</size></box></geometry>
        </collision>
        <inertial>
          <mass>10</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <!-- Physics -->
    <physics name="default_physics" default="0" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
    </physics>
  </world>
</sdf>
```

## Step 5: Create Setup Files

Create `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(sim_robot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

# Install launch files
install(DIRECTORY
  launch
  worlds
  urdf
  DESTINATION share/${PROJECT_NAME}/
)

# Install other files
install(DIRECTORY
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>sim_robot_description</name>
  <version>0.0.0</version>
  <description>Simulated robot description package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>urdf</depend>
  <depend>xacro</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Step 6: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select sim_robot_description

# Source the workspace
source install/setup.bash
```

## Step 7: Test the Robot Model

First, test that the URDF is valid:

```bash
# Check URDF validity
xacro ~/ros2_lab_ws/src/sim_robot_description/urdf/sim_robot.urdf.xacro

# Launch robot state publisher to visualize in RViz
ros2 launch sim_robot_description robot_spawn_launch.py
```

## Step 8: Launch the Simulation

In separate terminals:

**Terminal 1 - Launch Gazebo simulation:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 launch sim_robot_description robot_spawn_launch.py
```

**Terminal 2 - Send movement commands:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Move forward
ros2 topic pub /sim_robot/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}"

# Turn in place
ros2 topic pub /sim_robot/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

**Terminal 3 - Monitor sensor data:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Check LIDAR data
ros2 topic echo /sim_robot/scan

# Check camera data (image view)
# Install image view if not already installed
sudo apt install ros-humble-image-view
ros2 run image_view image_view --ros-args --remap image:=/sim_robot/camera/image_raw
```

## Step 9: Create a Control Node

Create a simple navigation node to test the sensors:

Create `sim_robot_description/sim_robot_description/navigate_node.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class NavigationNode(Node):
    def __init__(self):
        super().__init__('navigation_node')

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/sim_robot/cmd_vel', 10)

        # Create subscriber for laser scan
        self.scan_sub = self.create_subscription(
            LaserScan, '/sim_robot/scan', self.scan_callback, 10)

        # Create timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Robot state
        self.obstacle_detected = False
        self.obstacle_distance = float('inf')

        self.get_logger().info('Navigation node initialized')

    def scan_callback(self, msg):
        """Process laser scan data to detect obstacles."""
        # Check for obstacles in front (±30 degrees)
        front_ranges = msg.ranges[150:210]  # Approximately front

        if front_ranges:
            # Filter out invalid readings
            valid_ranges = [r for r in front_ranges if r > 0 and not math.isinf(r)]
            if valid_ranges:
                min_distance = min(valid_ranges)
                self.obstacle_distance = min_distance
                self.obstacle_detected = min_distance < 1.0  # Obstacle within 1 meter
                self.get_logger().info(f'Min front distance: {min_distance:.2f}m, Obstacle: {self.obstacle_detected}')

    def control_loop(self):
        """Main control loop."""
        msg = Twist()

        if self.obstacle_detected:
            # Stop and turn if obstacle detected
            msg.linear.x = 0.0
            msg.angular.z = 0.5
            self.get_logger().info('Obstacle detected! Turning...')
        else:
            # Move forward if no obstacle
            msg.linear.x = 0.5
            msg.angular.z = 0.0
            self.get_logger().info('No obstacle, moving forward...')

        self.cmd_vel_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    navigation_node = NavigationNode()

    try:
        rclpy.spin(navigation_node)
    except KeyboardInterrupt:
        pass
    finally:
        navigation_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Update `setup.py` to include the new executable:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'sim_robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/worlds', glob('worlds/*.world')),
        ('share/' + package_name + '/urdf', glob('urdf/*.xacro')),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Simulated robot description package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigate_node = sim_robot_description.navigate_node:main',
        ],
    },
)
```

Update `package.xml` to include Python dependencies:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>sim_robot_description</name>
  <version>0.0.0</version>
  <description>Simulated robot description package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_cmake_python</buildtool_depend>

  <depend>urdf</depend>
  <depend>xacro</depend>
  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>
  <depend>sensor_msgs</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Rebuild the package:

```bash
cd ~/ros2_lab_ws
colcon build --packages-select sim_robot_description
source install/setup.bash
```

## Step 10: Test the Complete System

**Terminal 1 - Launch simulation:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 launch sim_robot_description robot_spawn_launch.py
```

**Terminal 2 - Launch navigation node:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run sim_robot_description navigate_node
```

## Lab Questions

1. How does the Xacro macro system help in creating reusable robot components?
2. What are the key differences between the camera and LIDAR sensor configurations?
3. How does the differential drive plugin translate velocity commands to wheel movements?
4. What role does the robot_state_publisher play in the simulation?
5. How could you modify the robot to include additional sensors like an IMU?

## Summary

In this lab, you learned how to:
- Create a complete robot model with multiple sensors
- Configure Gazebo plugins for control and sensing
- Set up launch files for simulation
- Implement a simple navigation algorithm using sensor feedback
- Test the complete simulation system

This provides a solid foundation for developing more complex robotic systems in simulation.