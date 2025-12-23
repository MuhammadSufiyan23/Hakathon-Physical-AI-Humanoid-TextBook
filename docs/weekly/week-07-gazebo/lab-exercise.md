---
sidebar_label: 'Week 7 Lab: Advanced Gazebo-ROS 2 Integration'
title: 'Week 7 Lab: Advanced Gazebo-ROS 2 Integration'
---

# Week 7 Lab: Advanced Gazebo-ROS 2 Integration

## Objective

In this lab, you will create a complete integrated system with ros2_control, multiple sensors, and a complex environment. You'll learn to configure advanced Gazebo-ROS 2 integration and implement a navigation system that uses multiple sensor modalities.

## Prerequisites

- Completion of Weeks 1-6 labs
- ROS 2 Humble installed with Gazebo packages
- Basic knowledge of ros2_control
- Understanding of launch files and parameters

## Step 1: Create a New Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for this lab
ros2 pkg create --build-type ament_python advanced_sim_robot --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros cv_bridge
```

## Step 2: Create Robot Description with ros2_control

Create the URDF directory:

```bash
mkdir -p ~/ros2_lab_ws/src/advanced_sim_robot/urdf
mkdir -p ~/ros2_lab_ws/src/advanced_sim_robot/config
mkdir -p ~/ros2_lab_ws/src/advanced_sim_robot/launch
mkdir -p ~/ros2_lab_ws/src/advanced_sim_robot/worlds
```

Create `~/ros2_lab_ws/src/advanced_sim_robot/urdf/advanced_robot.urdf.xacro`:

```xml
<?xml version="1.0"?>
<robot name="advanced_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Properties -->
  <xacro:property name="base_width" value="0.6"/>
  <xacro:property name="base_length" value="0.8"/>
  <xacro:property name="base_height" value="0.3"/>
  <xacro:property name="wheel_radius" value="0.15"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="wheel_offset_x" value="0.3"/>
  <xacro:property name="wheel_offset_y" value="0.4"/>

  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="20.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="1.667" ixy="0.0" ixz="0.0"
        iyy="1.083" iyz="0.0"
        izz="1.083"/>
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
        <mass value="2.0"/>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <inertia
          ixx="0.02" ixy="0.0" ixz="0.0"
          iyy="0.02" iyz="0.0"
          izz="0.04"/>
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

  <!-- Create wheels -->
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
    <origin xyz="${base_length/2 - 0.025} 0 ${base_height/2 + 0.1}" rpy="0 0 0"/>
  </joint>

  <!-- LIDAR link -->
  <link name="lidar_link">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="0.001" ixy="0.0" ixz="0.0"
        iyy="0.001" iyz="0.0"
        izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
      <material name="silver">
        <color rgba="0.7 0.7 0.7 1"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0 0 ${base_height/2 + 0.15}" rpy="0 0 0"/>
  </joint>

  <!-- IMU link -->
  <link name="imu_link">
    <inertial>
      <mass value="0.01"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia
        ixx="0.0001" ixy="0.0" ixz="0.0"
        iyy="0.0001" iyz="0.0"
        izz="0.0001"/>
    </inertial>
  </link>

  <joint name="imu_joint" type="fixed">
    <parent link="base_link"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <!-- ros2_control configuration -->
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>
    <joint name="front_left_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="front_right_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="rear_left_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="rear_right_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>

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

  <!-- Camera sensor -->
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>
        <image><width>640</width><height>480</height><format>R8G8B8</format></image>
        <clip><near>0.1</near><far>100</far></clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>/advanced_robot</namespace>
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
        <scan><horizontal><samples>360</samples><min_angle>-3.14159</min_angle><max_angle>3.14159</max_angle></horizontal></scan>
        <range><min>0.1</min><max>30.0</max></range>
      </ray>
      <plugin name="lidar_controller" filename="libgazebo_ros_laser.so">
        <ros>
          <namespace>/advanced_robot</namespace>
          <remapping>scan:=scan</remapping>
        </ros>
        <topic_name>scan</topic_name>
        <frame_name>lidar_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <!-- IMU sensor -->
  <gazebo reference="imu_link">
    <sensor name="imu_sensor" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
        <ros>
          <namespace>/advanced_robot</namespace>
          <remapping>imu:=imu</remapping>
        </ros>
        <topic_name>imu</topic_name>
        <body_name>imu_link</body_name>
        <frame_name>imu_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <!-- ros2_control plugin -->
  <gazebo>
    <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
      <parameters>/home/user/ros2_lab_ws/src/advanced_sim_robot/config/robot_control.yaml</parameters>
      <ros>
        <namespace>/advanced_robot</namespace>
      </ros>
    </plugin>
  </gazebo>
</robot>
```

## Step 3: Create ros2_control Configuration

Create `~/ros2_lab_ws/src/advanced_sim_robot/config/robot_control.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    velocity_controller:
      type: velocity_controllers/JointGroupVelocityController

velocity_controller:
  ros__parameters:
    joints:
      - front_left_wheel_joint
      - front_right_wheel_joint
      - rear_left_wheel_joint
      - rear_right_wheel_joint
```

## Step 4: Create a Complex World

Create `~/ros2_lab_ws/src/advanced_sim_robot/worlds/complex_environment.world`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="complex_environment">
    <!-- Physics -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
      <ode>
        <solver>
          <type>quick</type>
          <iters>10</iters>
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0.000001</cfm>
          <erp>0.2</erp>
        </constraints>
      </ode>
    </physics>

    <!-- Scene -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>true</shadows>
    </scene>

    <!-- Sun -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Walls -->
    <model name="north_wall">
      <pose>0 8 1 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><box><size>16 0.2 2</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>16 0.2 2</size></box></geometry></collision>
        <inertial><mass>1</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia></inertial>
      </link>
    </model>

    <model name="south_wall">
      <pose>0 -8 1 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><box><size>16 0.2 2</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>16 0.2 2</size></box></geometry></collision>
        <inertial><mass>1</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertial>
      </link>
    </model>

    <model name="east_wall">
      <pose>8 0 1 1.5707 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><box><size>16 0.2 2</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>16 0.2 2</size></box></geometry></collision>
        <inertial><mass>1</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertial>
      </link>
    </model>

    <model name="west_wall">
      <pose>-8 0 1 1.5707 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><box><size>16 0.2 2</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>16 0.2 2</size></box></geometry></collision>
        <inertial><mass>1</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertial>
      </link>
    </model>

    <!-- Obstacles -->
    <model name="obstacle_1">
      <pose>3 3 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><box><size>1 1 1</size></box></geometry></visual>
        <collision name="collision"><geometry><box><size>1 1 1</size></box></geometry></collision>
        <inertial><mass>10</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia></inertial>
      </link>
    </model>

    <model name="obstacle_2">
      <pose>-3 -3 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual"><geometry><cylinder><radius>0.8</radius><length>1</length></cylinder></geometry></visual>
        <collision name="collision"><geometry><cylinder><radius>0.8</radius><length>1</length></cylinder></geometry></collision>
        <inertial><mass>10</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia></inertial>
      </link>
    </model>

    <!-- Goal area -->
    <model name="goal_area">
      <pose>6 6 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><cylinder><radius>1.0</radius><length>0.02</length></cylinder></geometry>
          <material><ambient>0 1 0 0.5</ambient><diffuse>0 1 0 0.5</diffuse></material>
        </visual>
        <collision name="collision"><geometry><cylinder><radius>1.0</radius><length>0.02</length></cylinder></geometry></collision>
        <inertial><mass>1</mass><inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia></inertial>
      </link>
    </model>
  </world>
</sdf>
```

## Step 5: Create the Main Launch File

Create `~/ros2_lab_ws/src/advanced_sim_robot/launch/advanced_robot_launch.py`:

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
    world = LaunchConfiguration('world', default='complex_environment')

    # Get paths
    pkg_share = FindPackageShare('advanced_sim_robot').find('advanced_sim_robot')
    urdf_path = os.path.join(pkg_share, 'urdf', 'advanced_robot.urdf.xacro')
    world_path = os.path.join(pkg_share, 'worlds', world.perform({}) + '.world')

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
            'world': world_path,
            'verbose': 'true'
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
            '-entity', 'advanced_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )

    # Joint state broadcaster
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    # Velocity controller
    velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['velocity_controller'],
        output='screen'
    )

    # TF2 static broadcaster for odom to base_link
    static_transform_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link'],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='complex_environment',
            description='Choose one of the world files from `/advanced_sim_robot/worlds`'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        joint_state_broadcaster,
        velocity_controller,
        static_transform_publisher
    ])
```

## Step 6: Create the Navigation Node

Create `~/ros2_lab_ws/src/advanced_sim_robot/advanced_sim_robot/navigation_node.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan, Image, Imu
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
import numpy as np
import math
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class AdvancedNavigationNode(Node):
    def __init__(self):
        super().__init__('advanced_navigation_node')

        # Create publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/advanced_robot/cmd_vel', 10)

        # Create subscribers
        self.scan_sub = self.create_subscription(LaserScan, '/advanced_robot/scan', self.scan_callback, 10)
        self.image_sub = self.create_subscription(Image, '/advanced_robot/camera/image_raw', self.image_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/advanced_robot/imu', self.imu_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/advanced_robot/odom', self.odom_callback, 10)

        # Create timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # CV Bridge for image processing
        self.bridge = CvBridge()

        # Robot state
        self.scan_data = None
        self.image_data = None
        self.imu_data = None
        self.odom_data = None

        # Navigation state
        self.obstacle_detected = False
        self.obstacle_distance = float('inf')
        self.target_reached = False
        self.target_x = 6.0  # Goal position
        self.target_y = 6.0

        # State machine
        self.state = 'EXPLORING'  # EXPLORING, NAVIGATING_TO_GOAL, AVOIDING_OBSTACLE

        self.get_logger().info('Advanced navigation node initialized')

    def scan_callback(self, msg):
        """Process laser scan data."""
        self.scan_data = msg

        # Analyze front-facing scan (±30 degrees)
        front_ranges = msg.ranges[150:210]  # Approximately front 60 degrees
        if front_ranges:
            valid_ranges = [r for r in front_ranges if r > 0 and not math.isinf(r)]
            if valid_ranges:
                self.obstacle_distance = min(valid_ranges)
                self.obstacle_detected = self.obstacle_distance < 1.5  # 1.5m threshold
                self.get_logger().info(f'Front distance: {self.obstacle_distance:.2f}m, Obstacle: {self.obstacle_detected}')

    def image_callback(self, msg):
        """Process camera image."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.image_data = cv_image

            # Simple color detection for goal area (green)
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Count green pixels to detect goal
            green_pixel_count = cv2.countNonZero(mask)
            if green_pixel_count > 5000:  # Threshold for goal detection
                self.get_logger().info('Goal detected in camera view!')

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def imu_callback(self, msg):
        """Process IMU data."""
        self.imu_data = msg
        # Extract orientation information if needed for navigation
        orientation = msg.orientation
        # Could use this for more precise navigation

    def odom_callback(self, msg):
        """Process odometry data."""
        self.odom_data = msg

        # Get current position
        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y

        # Calculate distance to target
        dist_to_target = math.sqrt((self.target_x - current_x)**2 + (self.target_y - current_y)**2)

        if dist_to_target < 0.5:  # 0.5m threshold for reaching goal
            self.target_reached = True
            self.get_logger().info('Target reached!')
        else:
            self.target_reached = False

    def control_loop(self):
        """Main navigation control loop."""
        if self.scan_data is None or self.odom_data is None:
            return

        # Get current position
        current_x = self.odom_data.pose.pose.position.x
        current_y = self.odom_data.pose.pose.position.y

        # Calculate angle to target
        target_angle = math.atan2(self.target_y - current_y, self.target_x - current_x)

        # Get current orientation (simplified - in real implementation you'd extract from quaternion)
        current_yaw = 0.0  # Simplified for this example
        if self.imu_data:
            # Extract yaw from quaternion (would need proper quaternion to euler conversion)
            pass

        # State machine for navigation
        if self.target_reached:
            self.state = 'REACHED_GOAL'
        elif self.obstacle_detected and self.state != 'AVOIDING_OBSTACLE':
            self.state = 'AVOIDING_OBSTACLE'
        elif not self.obstacle_detected and self.state == 'AVOIDING_OBSTACLE':
            self.state = 'NAVIGATING_TO_GOAL'
        elif self.state not in ['REACHED_GOAL', 'AVOIDING_OBSTACLE']:
            self.state = 'NAVIGATING_TO_GOAL'

        cmd = Twist()

        if self.state == 'REACHED_GOAL':
            # Stop when target is reached
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.get_logger().info('Goal reached - stopping')
        elif self.state == 'AVOIDING_OBSTACLE':
            # Obstacle avoidance behavior
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5  # Turn in place
            self.get_logger().info('Avoiding obstacle')
        else:  # NAVIGATING_TO_GOAL
            # Navigate toward target
            angle_diff = target_angle - current_yaw
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            # PID-like control for orientation
            angular_kp = 1.0
            cmd.angular.z = angular_kp * angle_diff

            # Move forward if roughly aligned with target
            if abs(angle_diff) < 0.3:  # 0.3 rad = ~17 degrees
                cmd.linear.x = 0.5
            else:
                cmd.linear.x = 0.0

            self.get_logger().info(f'Navigating to ({self.target_x}, {self.target_y}), state: {self.state}')

        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    import cv2  # Import here to avoid issues if OpenCV is not available
    rclpy.init(args=args)
    nav_node = AdvancedNavigationNode()

    try:
        rclpy.spin(nav_node)
    except KeyboardInterrupt:
        pass
    finally:
        nav_node.destroy_node()
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

package_name = 'advanced_sim_robot'

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
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Advanced simulation robot package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_node = advanced_sim_robot.navigation_node:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>advanced_sim_robot</name>
  <version>0.0.0</version>
  <description>Advanced simulation robot package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_cmake_python</buildtool_depend>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>tf2_ros</depend>
  <depend>cv_bridge</depend>

  <exec_depend>gazebo_ros_pkgs</exec_depend>
  <exec_depend>gazebo_ros2_control</exec_depend>
  <exec_depend>joint_state_broadcaster</exec_depend>
  <exec_depend>velocity_controllers</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Step 8: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select advanced_sim_robot

# Source the workspace
source install/setup.bash
```

## Step 9: Test the Complete System

**Terminal 1 - Launch the simulation:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 launch advanced_sim_robot advanced_robot_launch.py
```

**Terminal 2 - Launch the navigation node:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run advanced_sim_robot navigation_node
```

**Terminal 3 - Monitor topics:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Check laser scan
ros2 topic echo /advanced_robot/scan

# Check odometry
ros2 topic echo /advanced_robot/odom

# Check camera (if OpenCV is available)
ros2 run image_view image_view --ros-args --remap image:=/advanced_robot/camera/image_raw
```

## Step 10: Test Manual Control

**Terminal 4 - Manual control:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Move forward
ros2 topic pub /advanced_robot/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}"

# Turn
ros2 topic pub /advanced_robot/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 1.0}}"
```

## Lab Questions

1. How does ros2_control provide better hardware abstraction compared to traditional Gazebo plugins?
2. What are the advantages of using multiple sensor types (LIDAR, camera, IMU) for navigation?
3. How does the state machine approach in the navigation node handle different scenarios?
4. What role does the `use_sim_time` parameter play in the integration?
5. How could you extend this system to include path planning algorithms like A* or Dijkstra?

## Summary

In this lab, you learned how to:
- Create a robot model with ros2_control integration
- Configure complex sensors in Gazebo
- Set up a multi-sensor navigation system
- Implement a state machine for navigation behavior
- Create complex simulation environments
- Integrate all components into a complete system

This advanced integration demonstrates the full potential of Gazebo-ROS 2 systems for robotics development and testing.