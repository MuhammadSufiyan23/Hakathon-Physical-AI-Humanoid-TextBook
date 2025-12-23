---
sidebar_label: 'Gazebo-ROS 2 Integration'
title: 'Gazebo-ROS 2 Integration'
---

# Gazebo-ROS 2 Integration

## Introduction to Gazebo-ROS 2 Bridge

The integration between Gazebo and ROS 2 enables seamless simulation of robotic systems with full ROS 2 functionality. This integration allows developers to test ROS 2 nodes, algorithms, and complete robotic systems in a simulated environment before deploying on real hardware.

## Gazebo-ROS 2 Packages

### Core Integration Packages

The primary packages for Gazebo-ROS 2 integration include:

- **gazebo_ros_pkgs**: Core ROS 2 plugins and tools for Gazebo
- **gazebo_ros2_control**: ros2_control integration for Gazebo
- **ros_gz_bridge**: Bridge between ROS 2 and Gazebo Garden
- **ros_gz_sim**: Integration with Gazebo Garden simulation

### Installation

```bash
# Install Gazebo-ROS 2 packages for Humble
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs
sudo apt install ros-humble-gazebo-ros2-control
sudo apt install ros-humble-ros-gz
```

## Gazebo ROS 2 Plugins

### Joint State Publisher Plugin

The joint state publisher plugin publishes joint states for visualization and control:

```xml
<gazebo>
  <plugin filename="libgazebo_ros_joint_state_publisher.so" name="joint_state_publisher">
    <ros>
      <namespace>/robot</namespace>
      <remapping>joint_states:=/robot/joint_states</remapping>
    </ros>
    <update_rate>30</update_rate>
    <joint_name>left_wheel_joint</joint_name>
    <joint_name>right_wheel_joint</joint_name>
    <joint_name>arm_joint</joint_name>
    <topic>joint_states</topic>
  </plugin>
</gazebo>
```

### Diff Drive Controller Plugin

For differential drive robots:

```xml
<gazebo>
  <plugin filename="libgazebo_ros_diff_drive.so" name="diff_drive">
    <ros>
      <namespace>/robot</namespace>
      <remapping>cmd_vel:=/cmd_vel</remapping>
      <remapping>odom:=/odom</remapping>
      <remapping>joint_states:=/joint_states</remapping>
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
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>true</publish_wheel_tf>
  </plugin>
</gazebo>
```

### Sensor Plugins

#### Camera Plugin

```xml
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
    <plugin filename="libgazebo_ros_camera.so" name="camera_controller">
      <ros>
        <namespace>/robot</namespace>
        <remapping>image_raw:=/camera/image_raw</remapping>
        <remapping>camera_info:=/camera/camera_info</remapping>
      </ros>
      <camera_name>camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

#### LIDAR Plugin

```xml
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
    <plugin filename="libgazebo_ros_laser.so" name="lidar_controller">
      <ros>
        <namespace>/robot</namespace>
        <remapping>scan:=/scan</remapping>
      </ros>
      <topic_name>scan</topic_name>
      <frame_name>lidar_link</frame_name>
      <min_range>0.1</min_range>
      <max_range>30.0</max_range>
    </plugin>
  </sensor>
</gazebo>
```

#### IMU Plugin

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <plugin filename="libgazebo_ros_imu.so" name="imu_plugin">
      <ros>
        <namespace>/robot</namespace>
        <remapping>imu:=/imu</remapping>
      </ros>
      <topic_name>imu</topic_name>
      <body_name>imu_link</body_name>
      <frame_name>imu_link</frame_name>
      <update_rate>100</update_rate>
    </plugin>
  </sensor>
</gazebo>
```

## ros2_control Integration

### URDF with ros2_control

Modern ROS 2 control systems use ros2_control for hardware abstraction:

```xml
<?xml version="1.0"?>
<robot name="ros2_control_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Robot links and joints -->
  <link name="base_link">
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.4167" ixy="0.0" ixz="0.0" iyy="0.2083" iyz="0.0" izz="0.2083"/>
    </inertial>
    <visual>
      <geometry><box size="0.6 0.4 0.2"/></geometry>
    </visual>
    <collision>
      <geometry><box size="0.6 0.4 0.2"/></geometry>
    </collision>
  </link>

  <link name="wheel_link">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.02"/>
    </inertial>
    <visual>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </visual>
    <collision>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </collision>
  </link>

  <joint name="wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_link"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <!-- ros2_control configuration -->
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>
    <joint name="wheel_joint">
      <command_interface name="velocity">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>

  <!-- Gazebo plugin for ros2_control -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find my_robot_description)/config/robot_control.yaml</parameters>
      <ros>
        <namespace>/robot</namespace>
      </ros>
    </plugin>
  </gazebo>
</robot>
```

### Control Configuration File

Create `config/robot_control.yaml`:

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
      - wheel_joint
```

## Launch Files for Integration

### Basic Simulation Launch

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
    robot_name = LaunchConfiguration('robot_name', default='robot')

    # Get URDF path
    pkg_share = FindPackageShare('my_robot_description').find('my_robot_description')
    urdf_path = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ])
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
            '-entity', [robot_name],
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # Joint state broadcaster (for ros2_control)
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    # Velocity controller (for ros2_control)
    velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['velocity_controller'],
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
            default_value='robot',
            description='Name of the robot to spawn'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        joint_state_broadcaster,
        velocity_controller
    ])
```

### Advanced Multi-Robot Launch

```python
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='empty')

    # Get URDF path
    pkg_share = FindPackageShare('multi_robot_description').find('multi_robot_description')
    robot_urdf_path = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')

    # Launch Gazebo
    gazebo = ExecuteProcess(
        cmd=['gzserver',
             '--verbose',
             '-s', 'libgazebo_ros_factory.so',
             '-s', 'libgazebo_ros_init.so'],
        output='screen'
    )

    # Robot 1 launch
    robot1_group = GroupAction(
        actions=[
            PushRosNamespace('robot1'),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot1_state_publisher',
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'robot_description': open(robot_urdf_path).read()
                }]
            ),
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'robot1',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.1'
                ],
                output='screen'
            )
        ]
    )

    # Robot 2 launch
    robot2_group = GroupAction(
        actions=[
            PushRosNamespace('robot2'),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot2_state_publisher',
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'robot_description': open(robot_urdf_path).read()
                }]
            ),
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'robot2',
                    '-x', '2.0',
                    '-y', '0.0',
                    '-z', '0.1'
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='empty',
            description='Choose one of the world files from `/gazebo_ros/worlds`'
        ),
        gazebo,
        robot1_group,
        robot2_group
    ])
```

## Bridge Between ROS 2 and Gazebo Garden

### ros_gz Bridge

For Gazebo Garden integration, use the ros_gz bridge:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # Launch Gazebo Garden
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),

        # Bridge for specific topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/model/vehicle/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/model/vehicle/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                '/camera@sensor_msgs/msg/Image@gz.msgs.Image',
                '/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo'
            ],
            output='screen'
        ),

        # Bridge for services
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/world/default/control@std_srvs/srv/Empty@gz.msgs.Empty'
            ],
            output='screen'
        )
    ])
```

## Testing Integration

### Example ROS 2 Node for Testing

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import Odometry
import cv2
from cv_bridge import CvBridge
import numpy as np

class IntegrationTestNode(Node):
    def __init__(self):
        super().__init__('integration_test_node')

        # Create publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/robot/cmd_vel', 10)

        # Create subscribers
        self.odom_sub = self.create_subscription(Odometry, '/robot/odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/robot/scan', self.scan_callback, 10)
        self.image_sub = self.create_subscription(Image, '/robot/camera/image_raw', self.image_callback, 10)

        # Create timer for sending commands
        self.timer = self.create_timer(0.1, self.timer_callback)

        # CV Bridge for image processing
        self.bridge = CvBridge()

        # Robot state
        self.current_pose = None
        self.obstacle_detected = False
        self.latest_image = None

        self.get_logger().info('Integration test node initialized')

    def odom_callback(self, msg):
        """Handle odometry messages."""
        self.current_pose = msg.pose.pose
        self.get_logger().info(
            f'Robot position: ({msg.pose.pose.position.x:.2f}, {msg.pose.pose.position.y:.2f})'
        )

    def scan_callback(self, msg):
        """Handle laser scan messages."""
        # Check for obstacles in front
        front_scan = msg.ranges[170:190]  # Front 20 degrees
        if front_scan:
            min_distance = min([r for r in front_scan if r > 0 and not np.isinf(r)], default=float('inf'))
            self.obstacle_detected = min_distance < 1.0
            self.get_logger().info(f'Front distance: {min_distance:.2f}m, Obstacle: {self.obstacle_detected}')

    def image_callback(self, msg):
        """Handle image messages."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.latest_image = cv_image
            # Process image (simple example: detect edges)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Display image with OpenCV (optional)
            cv2.imshow('Robot Camera', cv_image)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def timer_callback(self):
        """Send commands to robot."""
        cmd = Twist()

        if self.obstacle_detected:
            # Turn if obstacle detected
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5
        else:
            # Move forward if no obstacle
            cmd.linear.x = 0.5
            cmd.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    test_node = IntegrationTestNode()

    try:
        rclpy.spin(test_node)
    except KeyboardInterrupt:
        pass
    finally:
        test_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Configuration Best Practices

### Parameter Management

Use parameter files for consistent configuration:

```yaml
# config/simulation_params.yaml
robot_controller:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 50.0
    cmd_vel_timeout: 0.5
    linear:
      x:
        has_velocity_limits: true
        max_velocity: 1.0
        has_acceleration_limits: true
        max_acceleration: 2.0
    angular:
      z:
        has_velocity_limits: true
        max_velocity: 1.0
        has_acceleration_limits: true
        max_acceleration: 2.0
```

### Namespace Organization

Organize topics and services with proper namespaces:

```xml
<robot name="multi_robot_system" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Robot 1 -->
  <gazebo>
    <plugin name="robot1_diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/robot1</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <!-- other parameters -->
    </plugin>
  </gazebo>

  <!-- Robot 2 -->
  <gazebo>
    <plugin name="robot2_diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/robot2</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <!-- other parameters -->
    </plugin>
  </gazebo>
</robot>
```

## Debugging Integration Issues

### Common Issues and Solutions

1. **Topic Connection Issues**:
   - Check namespace consistency
   - Verify topic remappings
   - Ensure use_sim_time is set correctly

2. **Timing Issues**:
   - Synchronize simulation and ROS time
   - Adjust update rates appropriately
   - Check for timing constraints

3. **Performance Issues**:
   - Optimize update rates
   - Reduce unnecessary topic publications
   - Check CPU and memory usage

### Diagnostic Tools

```bash
# Check topic connections
ros2 topic list
ros2 topic info /robot/odom

# Check service availability
ros2 service list

# Monitor performance
ros2 run topicos monitoring_node
ros2 run rqt_graph rqt_graph
```

## Advanced Integration Patterns

### Custom Sensor Integration

```xml
<gazebo reference="custom_sensor_link">
  <sensor name="custom_sensor" type="ray">
    <always_on>true</always_on>
    <update_rate>50</update_rate>
    <ray>
      <scan>
        <horizontal><samples>64</samples><min_angle>-0.785</min_angle><max_angle>0.785</max_angle></horizontal>
        <vertical><samples>16</samples><min_angle>-0.174</min_angle><max_angle>0.174</max_angle></vertical>
      </scan>
      <range><min>0.1</min><max>10.0</max></range>
    </ray>
    <plugin filename="libCustomSensorPlugin.so" name="custom_sensor_plugin">
      <ros>
        <namespace>/robot</namespace>
        <remapping>custom_data:=/sensor_data</remapping>
      </ros>
      <topic_name>sensor_data</topic_name>
      <frame_name>custom_sensor_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## Summary

Gazebo-ROS 2 integration provides a powerful platform for robotics simulation and development. The combination of realistic physics simulation with ROS 2's communication and control framework enables comprehensive testing and validation of robotic systems. Proper configuration of plugins, namespaces, and parameters is essential for effective integration, and understanding the various integration patterns allows for complex multi-robot and multi-sensor systems to be simulated effectively.