---
sidebar_label: 'Week 10 Lab: Isaac Navigation and Manipulation'
title: 'Week 10 Lab: Isaac Navigation and Manipulation'
---

# Week 10 Lab: Isaac Navigation and Manipulation

## Objective

In this lab, you will create a complete robotic system that integrates navigation and manipulation capabilities using the Isaac platform. You'll implement path planning, obstacle avoidance, grasp planning, and coordinated manipulation in a simulated environment.

## Prerequisites

- Completion of Weeks 1-9 labs
- Isaac Sim installed with Omniverse
- ROS 2 Humble with navigation2 packages
- Understanding of Isaac GEMs and perception

## Step 1: Create a New ROS 2 Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for the Isaac navigation and manipulation lab
ros2 pkg create --build-type ament_python isaac_nav_manip_lab --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros visualization_msgs cv_bridge builtin_interfaces
```

## Step 2: Create the Navigation and Manipulation Node

Create the necessary directories:

```bash
mkdir -p ~/ros2_lab_ws/src/isaac_nav_manip_lab/config
mkdir -p ~/ros2_lab_ws/src/isaac_nav_manip_lab/launch
mkdir -p ~/ros2_lab_ws/src/isaac_nav_manip_lab/maps
```

Create `~/ros2_lab_ws/src/isaac_nav_manip_lab/isaac_nav_manip_lab/nav_manip_controller.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist, Pose, PoseStamped, Point
from sensor_msgs.msg import LaserScan, Image, PointCloud2, JointState
from nav_msgs.msg import Odometry, OccupancyGrid
from nav2_msgs.action import NavigateToPose
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from visualization_msgs.msg import MarkerArray, Marker
from cv_bridge import CvBridge
from std_msgs.msg import Header, String
from builtin_interfaces.msg import Duration
import numpy as np
import math
import time
from enum import Enum

class TaskState(Enum):
    IDLE = 1
    NAVIGATING = 2
    PERCEIVING_OBJECT = 3
    PLANNING_GRASP = 4
    MANIPULATING = 5
    RETURNING = 6

class IsaacNavManipController(Node):
    def __init__(self):
        super().__init__('isaac_nav_manip_controller')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Initialize state
        self.state = TaskState.IDLE
        self.target_object = None
        self.grasp_pose = None
        self.return_position = [0.0, 0.0, 0.0]  # Starting position

        # Navigation action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joint_traj_pub = self.create_publisher(JointTrajectory, '/joint_trajectory', 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/task_markers', 10)
        self.state_pub = self.create_publisher(String, '/task_state', 10)

        # Subscribers
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.pc_sub = self.create_subscription(PointCloud2, '/camera/depth/points', self.pointcloud_callback, 10)
        self.joint_state_sub = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)

        # Navigation goal positions
        self.search_position = [2.0, 2.0, 0.0]  # Position to search for objects
        self.manipulation_position = [1.5, 1.5, 0.0]  # Position for manipulation
        self.drop_position = [3.0, 0.0, 0.0]  # Drop-off position

        # Robot state
        self.current_pose = None
        self.current_joints = None
        self.laser_data = None
        self.image_data = None
        self.pointcloud_data = None

        # Task timer
        self.task_timer = self.create_timer(0.1, self.task_step)

        # Object detection parameters
        self.object_detected = False
        self.object_position = None

        self.get_logger().info('Isaac Navigation and Manipulation Controller initialized')

    def odom_callback(self, msg):
        """Update robot pose."""
        self.current_pose = msg.pose.pose

    def scan_callback(self, msg):
        """Update laser scan data."""
        self.laser_data = msg

    def image_callback(self, msg):
        """Process camera image for object detection."""
        try:
            self.image_data = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Simple object detection (in a real implementation, this would use AI)
            # For this example, we'll simulate object detection
            self.detect_object_in_image(self.image_data)
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def pointcloud_callback(self, msg):
        """Process point cloud for 3D object localization."""
        self.pointcloud_data = msg

    def joint_state_callback(self, msg):
        """Update joint states."""
        self.current_joints = msg

    def detect_object_in_image(self, image):
        """Detect objects in the image (simulated for this lab)."""
        # In a real implementation, this would use Isaac's AI perception
        # For this lab, we'll simulate object detection

        # Simulate detecting an object occasionally
        if np.random.random() < 0.05:  # 5% chance per callback
            self.object_detected = True
            # Simulate object position in front of robot
            self.object_position = [
                self.current_pose.position.x + 0.5,  # 50cm in front
                self.current_pose.position.y,       # Same Y
                self.current_pose.position.z        # Same Z
            ]
            self.get_logger().info(f'Object detected at: {self.object_position}')

    def task_step(self):
        """Main task execution loop."""
        if self.current_pose is None:
            return

        # Publish current state
        state_msg = String()
        state_msg.data = self.state.name
        self.state_pub.publish(state_msg)

        # Execute state-specific actions
        if self.state == TaskState.IDLE:
            self.transition_to(TaskState.NAVIGATING)

        elif self.state == TaskState.NAVIGATING:
            self.execute_navigation()

        elif self.state == TaskState.PERCEIVING_OBJECT:
            self.execute_perception()

        elif self.state == TaskState.PLANNING_GRASP:
            self.execute_grasp_planning()

        elif self.state == TaskState.MANIPULATING:
            self.execute_manipulation()

        elif self.state == TaskState.RETURNING:
            self.execute_return()

    def transition_to(self, new_state):
        """Transition to a new state."""
        self.get_logger().info(f'Transitioning from {self.state.name} to {new_state.name}')
        self.state = new_state

    def execute_navigation(self):
        """Execute navigation to search position."""
        if self.current_pose is None:
            return

        # Check if we're close to the search position
        current_pos = [self.current_pose.position.x, self.current_pose.position.y]
        search_pos = self.search_position[:2]

        distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(current_pos, search_pos)]))

        if distance < 0.5:  # Within 50cm of goal
            self.get_logger().info('Reached search position, looking for objects')
            self.transition_to(TaskState.PERCEIVING_OBJECT)
        else:
            # Navigate to search position
            self.navigate_to_position(self.search_position)

    def execute_perception(self):
        """Execute object perception."""
        if self.object_detected and self.object_position:
            self.get_logger().info('Object detected, planning grasp')
            self.transition_to(TaskState.PLANNING_GRASP)
        else:
            self.get_logger().info('Looking for objects...')

    def execute_grasp_planning(self):
        """Execute grasp planning."""
        if self.object_position:
            # Plan grasp pose (simplified for this lab)
            self.grasp_pose = self.plan_grasp_pose(self.object_position)

            if self.grasp_pose:
                self.get_logger().info('Grasp planned, navigating to manipulation position')
                self.transition_to(TaskState.MANIPULATING)
            else:
                self.get_logger().warn('Could not plan grasp, returning to search')
                self.transition_to(TaskState.NAVIGATING)

    def execute_manipulation(self):
        """Execute manipulation task."""
        if self.current_pose is None:
            return

        # Navigate to manipulation position
        current_pos = [self.current_pose.position.x, self.current_pose.position.y]
        manip_pos = self.manipulation_position[:2]

        distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(current_pos, manip_pos)]))

        if distance < 0.3:  # Close enough to manipulation position
            # Execute grasp (simplified)
            self.execute_grasp()
            self.get_logger().info('Object grasped, returning to drop position')
            self.transition_to(TaskState.RETURNING)
        else:
            # Navigate to manipulation position
            self.navigate_to_position(self.manipulation_position)

    def execute_return(self):
        """Return to drop position."""
        if self.current_pose is None:
            return

        # Navigate to drop position
        current_pos = [self.current_pose.position.x, self.current_pose.position.y]
        drop_pos = self.drop_position[:2]

        distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(current_pos, drop_pos)]))

        if distance < 0.3:  # Close enough to drop position
            # Execute drop
            self.execute_drop()
            self.get_logger().info('Object dropped, task complete')
            self.transition_to(TaskState.IDLE)
        else:
            # Navigate to drop position
            self.navigate_to_position(self.drop_position)

    def navigate_to_position(self, position):
        """Navigate to a specific position."""
        if not self.nav_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().error('Navigation action server not available')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.pose.position.x = position[0]
        goal_msg.pose.pose.position.y = position[1]
        goal_msg.pose.pose.position.z = 0.0

        # Set orientation to face forward
        from tf_transformations import quaternion_from_euler
        quat = quaternion_from_euler(0, 0, position[2])
        goal_msg.pose.pose.orientation.x = quat[0]
        goal_msg.pose.pose.orientation.y = quat[1]
        goal_msg.pose.pose.orientation.z = quat[2]
        goal_msg.pose.pose.orientation.w = quat[3]

        self.get_logger().info(f'Navigating to position: {position}')

        send_goal_future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigation_feedback_callback
        )

        send_goal_future.add_done_callback(self.navigation_goal_response_callback)

    def navigation_feedback_callback(self, feedback_msg):
        """Handle navigation feedback."""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Navigating... Distance remaining: {feedback.distance_remaining:.2f}m'
        )

    def navigation_goal_response_callback(self, future):
        """Handle navigation goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Navigation goal rejected')
            return

        self.get_logger().info('Navigation goal accepted, waiting for result...')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.navigation_result_callback)

    def navigation_result_callback(self, future):
        """Handle navigation result."""
        result = future.result().result
        status = future.result().status

        if status == 3:  # SUCCEEDED
            self.get_logger().info('Navigation succeeded!')
        else:
            self.get_logger().info(f'Navigation failed with status: {status}')

    def plan_grasp_pose(self, object_position):
        """Plan a grasp pose for the object."""
        # Simplified grasp planning
        # In a real implementation, this would use Isaac's grasp planning
        grasp_pose = Pose()
        grasp_pose.position.x = object_position[0] - 0.2  # Approach from front
        grasp_pose.position.y = object_position[1]
        grasp_pose.position.z = object_position[2] + 0.1  # Slightly above object

        # Simple orientation
        from tf_transformations import quaternion_from_euler
        quat = quaternion_from_euler(0, -1.57, 0)  # Facing downward
        grasp_pose.orientation.x = quat[0]
        grasp_pose.orientation.y = quat[1]
        grasp_pose.orientation.z = quat[2]
        grasp_pose.orientation.w = quat[3]

        return grasp_pose

    def execute_grasp(self):
        """Execute the grasp action."""
        # In a real implementation, this would control the manipulator
        # For this lab, we'll simulate the grasp
        self.get_logger().info('Executing grasp...')

        # Publish grasp visualization
        self.visualize_grasp_attempt()

        # Simulate grasp success
        time.sleep(1)  # Simulate time for grasp
        self.get_logger().info('Grasp completed')

    def execute_drop(self):
        """Execute the drop action."""
        # In a real implementation, this would control the manipulator
        # For this lab, we'll simulate the drop
        self.get_logger().info('Executing drop...')

        # Simulate drop
        time.sleep(1)  # Simulate time for drop
        self.get_logger().info('Drop completed')

        # Reset for next object
        self.object_detected = False
        self.object_position = None
        self.grasp_pose = None

    def visualize_grasp_attempt(self):
        """Visualize the grasp attempt."""
        marker_array = MarkerArray()

        # Create grasp position marker
        grasp_marker = Marker()
        grasp_marker.header.frame_id = 'map'
        grasp_marker.header.stamp = self.get_clock().now().to_msg()
        grasp_marker.ns = 'grasp_attempt'
        grasp_marker.id = 0
        grasp_marker.type = Marker.SPHERE
        grasp_marker.action = Marker.ADD

        if self.grasp_pose:
            grasp_marker.pose = self.grasp_pose
            grasp_marker.scale.x = 0.1
            grasp_marker.scale.y = 0.1
            grasp_marker.scale.z = 0.1
            grasp_marker.color.r = 1.0
            grasp_marker.color.g = 0.0
            grasp_marker.color.b = 0.0
            grasp_marker.color.a = 0.8

        marker_array.markers.append(grasp_marker)

        # Create approach direction marker
        approach_marker = Marker()
        approach_marker.header = grasp_marker.header
        approach_marker.ns = 'approach_direction'
        approach_marker.id = 1
        approach_marker.type = Marker.ARROW
        approach_marker.action = Marker.ADD

        if self.grasp_pose:
            # Arrow from object position to grasp position
            start_point = Point()
            start_point.x = self.object_position[0] if self.object_position else 0.0
            start_point.y = self.object_position[1] if self.object_position else 0.0
            start_point.z = self.object_position[2] if self.object_position else 0.0

            end_point = Point()
            end_point.x = self.grasp_pose.position.x
            end_point.y = self.grasp_pose.position.y
            end_point.z = self.grasp_pose.position.z

            approach_marker.points = [start_point, end_point]
            approach_marker.scale.x = 0.02  # Shaft diameter
            approach_marker.scale.y = 0.04  # Head diameter
            approach_marker.color.r = 0.0
            approach_marker.color.g = 1.0
            approach_marker.color.b = 0.0
            approach_marker.color.a = 0.8

        marker_array.markers.append(approach_marker)

        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    controller = IsaacNavManipController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down navigation and manipulation controller...')
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 3: Create Isaac Sim Configuration

Create `~/ros2_lab_ws/src/isaac_nav_manip_lab/config/nav_manip_config.yaml`:

```yaml
# Navigation and Manipulation Configuration
nav_manip_controller:
  ros__parameters:
    # Navigation parameters
    navigation:
      planner_frequency: 5.0
      controller_frequency: 20.0
      max_vel_x: 0.5
      min_vel_x: 0.1
      max_vel_theta: 1.0
      min_in_place_vel_theta: 0.2
      yaw_goal_tolerance: 0.1
      xy_goal_tolerance: 0.2
      rot_stopped_velocity: 0.1
      trans_stopped_velocity: 0.1

    # Manipulation parameters
    manipulation:
      approach_distance: 0.15
      grasp_height: 0.1
      drop_height: 0.05
      gripper_force: 50.0
      max_gripper_width: 0.08
      min_gripper_width: 0.01

    # Perception parameters
    perception:
      object_detection_threshold: 0.5
      min_object_size: 0.02  # 2cm minimum
      max_detection_range: 2.0  # 2m maximum

    # Task parameters
    task:
      search_timeout: 30.0  # seconds
      manipulation_timeout: 60.0  # seconds
      return_timeout: 30.0  # seconds
```

## Step 4: Create a Launch File

Create `~/ros2_lab_ws/src/isaac_nav_manip_lab/launch/nav_manip_system_launch.py`:

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
    params_file = LaunchConfiguration('params_file', default='nav_manip_config.yaml')

    # Package names
    pkg_isaac_nav_manip_lab = FindPackageShare('isaac_nav_manip_lab')
    pkg_nav2_bringup = FindPackageShare('nav2_bringup')

    # Navigation system (this would normally include AMCL, BT Navigator, etc.)
    navigation_system = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Navigation and manipulation controller
    nav_manip_controller = Node(
        package='isaac_nav_manip_lab',
        executable='nav_manip_controller',
        name='nav_manip_controller',
        parameters=[
            PathJoinSubstitution([pkg_isaac_nav_manip_lab, 'config', params_file]),
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    # RViz for visualization
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('nav2_bringup'),
        'rviz',
        'nav2_default_view.rviz'
    ])

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Isaac Perception Nodes (simulated)
    perception_simulator = Node(
        package='isaac_nav_manip_lab',
        executable='perception_simulator',
        name='perception_simulator',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Isaac Sim) clock if true'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value='nav_manip_config.yaml',
            description='Full path to the ROS2 parameters file to use for all launched nodes'
        ),

        # Launch navigation system
        navigation_system,

        # Launch perception simulator
        TimerAction(
            period=2.0,
            actions=[perception_simulator]
        ),

        # Launch navigation and manipulation controller
        TimerAction(
            period=3.0,
            actions=[nav_manip_controller]
        ),

        # Launch RViz
        TimerAction(
            period=4.0,
            actions=[rviz]
        )
    ])
```

## Step 5: Create Perception Simulator

Create `~/ros2_lab_ws/src/isaac_nav_manip_lab/isaac_nav_manip_lab/perception_simulator.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2, LaserScan
from geometry_msgs.msg import PointStamped
from vision_msgs.msg import Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import numpy as np
import cv2
from std_msgs.msg import Header
import random

class IsaacPerceptionSimulator(Node):
    def __init__(self):
        super().__init__('isaac_perception_simulator')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Publishers
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.pc_pub = self.create_publisher(PointCloud2, '/camera/depth/points', 10)
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        self.detection_pub = self.create_publisher(Detection2DArray, '/detections', 10)

        # Timer for simulating sensor data
        self.perception_timer = self.create_timer(0.1, self.generate_perception_data)  # 10 Hz

        # Simulated objects in environment
        self.objects = [
            {'position': [2.5, 2.5, 0.1], 'size': [0.1, 0.1, 0.1], 'class': 'cube'},
            {'position': [1.8, 1.2, 0.1], 'size': [0.08, 0.08, 0.15], 'class': 'cylinder'},
            {'position': [3.2, 0.8, 0.1], 'size': [0.12, 0.06, 0.08], 'class': 'rect_prism'}
        ]

        # Robot position (will be updated based on navigation)
        self.robot_position = [0.0, 0.0, 0.0]

        self.get_logger().info('Isaac Perception Simulator initialized')

    def generate_perception_data(self):
        """Generate simulated perception data."""
        # Update robot position (simulated based on navigation)
        self.update_robot_position()

        # Generate simulated sensor data
        self.generate_simulated_image()
        self.generate_simulated_pointcloud()
        self.generate_simulated_laser_scan()
        self.generate_simulated_detections()

    def update_robot_position(self):
        """Update robot position based on navigation (simulated)."""
        # In a real system, this would come from odometry
        # For this simulation, we'll just simulate movement
        pass

    def generate_simulated_image(self):
        """Generate simulated camera image."""
        # Create a simulated image with objects
        height, width = 480, 640
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Add simulated objects based on their positions relative to robot
        for obj in self.objects:
            # Calculate object position relative to robot
            rel_x = obj['position'][0] - self.robot_position[0]
            rel_y = obj['position'][1] - self.robot_position[1]

            # Simple projection to image coordinates
            # This is a simplified model - in reality, you'd use camera intrinsics
            if abs(rel_x) < 3.0 and abs(rel_y) < 3.0:  # Within 3m
                # Project to image (simplified)
                img_x = int((rel_x * 100) + width // 2)  # Simplified projection
                img_y = int((-rel_y * 100) + height // 2)  # Flip Y axis

                if 0 < img_x < width and 0 < img_y < height:
                    # Draw object as a colored rectangle
                    color = {
                        'cube': (255, 0, 0),      # Red
                        'cylinder': (0, 255, 0),  # Green
                        'rect_prism': (0, 0, 255) # Blue
                    }.get(obj['class'], (255, 255, 255))

                    # Draw a rectangle representing the object
                    size_px = max(10, int(min(obj['size'][:2]) * 100))
                    cv2.rectangle(
                        image,
                        (img_x - size_px//2, img_y - size_px//2),
                        (img_x + size_px//2, img_y + size_px//2),
                        color, -1
                    )

        # Add some noise
        noise = np.random.normal(0, 10, image.shape).astype(np.int16)
        noisy_image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Publish image
        img_msg = self.bridge.cv2_to_imgmsg(noisy_image, "bgr8")
        img_msg.header.stamp = self.get_clock().now().to_msg()
        img_msg.header.frame_id = 'camera_rgb_optical_frame'
        self.image_pub.publish(img_msg)

    def generate_simulated_pointcloud(self):
        """Generate simulated point cloud data."""
        # Create a simple point cloud with some points around objects
        points = []

        # Add ground plane points
        for x in np.linspace(-5, 5, 100):
            for y in np.linspace(-5, 5, 100):
                if np.random.random() < 0.1:  # Sparse sampling
                    points.append([x, y, 0.0])  # Ground plane at z=0

        # Add object points
        for obj in self.objects:
            # Add points for each object
            obj_x, obj_y, obj_z = obj['position']
            size_x, size_y, size_z = obj['size']

            # Generate points on object surfaces
            for _ in range(50):  # 50 points per object
                px = obj_x + np.random.uniform(-size_x/2, size_x/2)
                py = obj_y + np.random.uniform(-size_y/2, size_y/2)
                pz = obj_z + np.random.uniform(0, size_z)
                points.append([px, py, pz])

        # Convert to PointCloud2 message
        from sensor_msgs_py import point_cloud2
        from sensor_msgs.msg import PointField

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'camera_depth_optical_frame'

        pc_msg = point_cloud2.create_cloud(header, fields, points)
        self.pc_pub.publish(pc_msg)

    def generate_simulated_laser_scan(self):
        """Generate simulated laser scan data."""
        scan_msg = LaserScan()
        scan_msg.header.stamp = self.get_clock().now().to_msg()
        scan_msg.header.frame_id = 'laser_frame'

        # Laser scan parameters
        scan_msg.angle_min = -np.pi
        scan_msg.angle_max = np.pi
        scan_msg.angle_increment = 2 * np.pi / 360  # 1 degree resolution
        scan_msg.time_increment = 0.0
        scan_msg.scan_time = 0.1
        scan_msg.range_min = 0.1
        scan_msg.range_max = 10.0

        # Generate ranges based on objects in environment
        ranges = []
        for i in range(360):
            angle = scan_msg.angle_min + i * scan_msg.angle_increment

            # Calculate ray direction
            ray_dir_x = np.cos(angle)
            ray_dir_y = np.sin(angle)

            # Check for intersections with objects
            min_range = scan_msg.range_max

            for obj in self.objects:
                obj_x, obj_y, _ = obj['position']
                size_x, size_y, _ = obj['size']

                # Simple circle intersection (approximating rectangular objects)
                obj_dist = np.sqrt((obj_x - self.robot_position[0])**2 + (obj_y - self.robot_position[1])**2)

                # Check if ray intersects with object's bounding circle
                dx = obj_x - self.robot_position[0]
                dy = obj_y - self.robot_position[1]

                # Distance from ray to object center
                cross_product = ray_dir_x * dy - ray_dir_y * dx
                distance_to_center = abs(cross_product)

                if distance_to_center < max(size_x, size_y):
                    # Ray intersects object's vicinity, return approximate distance
                    min_range = min(min_range, obj_dist - max(size_x, size_y)/2)

            # Add some noise to the range
            noise = np.random.normal(0, 0.01)
            final_range = max(scan_msg.range_min, min(min_range + noise, scan_msg.range_max))
            ranges.append(final_range)

        scan_msg.ranges = ranges
        self.scan_pub.publish(scan_msg)

    def generate_simulated_detections(self):
        """Generate simulated object detections."""
        detection_array = Detection2DArray()
        detection_array.header.stamp = self.get_clock().now().to_msg()
        detection_array.header.frame_id = 'camera_rgb_optical_frame'

        # Detect objects that are within camera range
        for i, obj in enumerate(self.objects):
            obj_x, obj_y, obj_z = obj['position']

            # Calculate distance from robot
            distance = np.sqrt((obj_x - self.robot_position[0])**2 + (obj_y - self.robot_position[1])**2)

            # Only detect if within range
            if distance < 3.0:  # 3m detection range
                detection = Detection2D()

                # Simple bounding box (in image coordinates, simplified)
                detection.bbox.center.x = 320  # Center of image
                detection.bbox.center.y = 240
                detection.bbox.size_x = 50
                detection.bbox.size_y = 50

                # Add classification
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.hypothesis.class_id = obj['class']
                hypothesis.hypothesis.score = 0.8  # High confidence for simulation
                detection.results.append(hypothesis)

                detection_array.detections.append(detection)

        self.detection_pub.publish(detection_array)

def main(args=None):
    rclpy.init(args=args)
    simulator = IsaacPerceptionSimulator()

    try:
        rclpy.spin(simulator)
    except KeyboardInterrupt:
        simulator.get_logger().info('Shutting down perception simulator...')
    finally:
        simulator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 6: Create Setup Files

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_nav_manip_lab'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/maps', glob('maps/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Isaac Navigation and Manipulation Lab Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'nav_manip_controller = isaac_nav_manip_lab.nav_manip_controller:main',
            'perception_simulator = isaac_nav_manip_lab.perception_simulator:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>isaac_nav_manip_lab</name>
  <version>0.0.0</version>
  <description>Isaac Navigation and Manipulation Lab Package</description>
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
  <depend>visualization_msgs</depend>
  <depend>cv_bridge</depend>
  <depend>vision_msgs</depend>
  <depend>nav2_msgs</depend>

  <exec_depend>nav2_bringup</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Step 7: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select isaac_nav_manip_lab

# Source the workspace
source install/setup.bash
```

## Step 8: Test the System

**Terminal 1 - Start the navigation and manipulation system:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 launch isaac_nav_manip_lab nav_manip_system_launch.py
```

**Terminal 2 - Monitor the task state:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 topic echo /task_state
```

**Terminal 3 - Monitor navigation goals:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose '{pose: {position: {x: 2.0, y: 2.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}}'
```

**Terminal 4 - Visualize in RViz:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# RViz should start automatically with the launch file
# If not, run:
# rviz2
```

## Step 9: Create a Task Manager Node

Create `~/ros2_lab_ws/src/isaac_nav_manip_lab/isaac_nav_manip_lab/task_manager.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import time
import json

class IsaacTaskManager(Node):
    def __init__(self):
        super().__init__('isaac_task_manager')

        # Action clients
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Publishers and subscribers
        self.task_state_sub = self.create_subscription(
            String,
            '/task_state',
            self.task_state_callback,
            10
        )

        self.task_command_pub = self.create_publisher(
            String,
            '/task_commands',
            10
        )

        self.task_status_pub = self.create_publisher(
            String,
            '/task_status',
            10
        )

        self.task_completed_pub = self.create_publisher(
            Bool,
            '/task_completed',
            10
        )

        # Task management
        self.current_task = None
        self.task_queue = []
        self.task_history = []

        # Timer for task management
        self.task_timer = self.create_timer(1.0, self.manage_tasks)

        # Task states
        self.current_state = "IDLE"
        self.state_start_time = time.time()

        self.get_logger().info('Isaac Task Manager initialized')

    def task_state_callback(self, msg):
        """Handle task state updates."""
        self.current_state = msg.data
        self.get_logger().info(f'Task state changed to: {self.current_state}')

        # Update state start time when state changes
        self.state_start_time = time.time()

        # Check for state-specific actions
        self.handle_state_changes()

    def handle_state_changes(self):
        """Handle actions when states change."""
        if self.current_state == "IDLE":
            # Check if we have tasks to execute
            if self.task_queue:
                next_task = self.task_queue.pop(0)
                self.execute_task(next_task)
        elif self.current_state == "MANIPULATING":
            # Task is actively manipulating
            pass
        elif self.current_state == "RETURNING":
            # Task is returning
            pass

    def manage_tasks(self):
        """Main task management loop."""
        # Check for task timeouts
        time_in_state = time.time() - self.state_start_time

        # Timeout thresholds (in seconds)
        timeouts = {
            "NAVIGATING": 60.0,
            "PERCEIVING_OBJECT": 30.0,
            "PLANNING_GRASP": 30.0,
            "MANIPULATING": 120.0,
            "RETURNING": 60.0
        }

        if self.current_state in timeouts:
            if time_in_state > timeouts[self.current_state]:
                self.get_logger().warn(f'Task timed out in state {self.current_state}')
                self.handle_timeout()

    def handle_timeout(self):
        """Handle task timeout."""
        # Reset to a safe state
        self.current_state = "IDLE"
        self.state_start_time = time.time()

        # Publish timeout notification
        status_msg = String()
        status_msg.data = f"TASK_TIMEOUT_IN_{self.current_state}"
        self.task_status_pub.publish(status_msg)

    def add_task(self, task_definition):
        """Add a task to the queue."""
        self.task_queue.append(task_definition)
        self.get_logger().info(f'Added task to queue: {task_definition}')

    def execute_task(self, task):
        """Execute a specific task."""
        self.current_task = task
        self.get_logger().info(f'Executing task: {task}')

        # Publish task command
        command_msg = String()
        command_msg.data = json.dumps({
            "task": task,
            "timestamp": time.time()
        })
        self.task_command_pub.publish(command_msg)

    def queue_pick_and_place_task(self, pickup_position, place_position):
        """Queue a pick and place task."""
        task = {
            "type": "pick_and_place",
            "pickup": pickup_position,
            "place": place_position,
            "object_class": "any_object"
        }
        self.add_task(task)

    def queue_search_and_grab_task(self, search_area_center, search_radius):
        """Queue a search and grab task."""
        task = {
            "type": "search_and_grab",
            "search_center": search_area_center,
            "search_radius": search_radius,
            "return_position": [0.0, 0.0, 0.0]
        }
        self.add_task(task)

def main(args=None):
    rclpy.init(args=args)
    task_manager = IsaacTaskManager()

    # Add some example tasks
    task_manager.queue_search_and_grab_task(
        search_area_center=[2.0, 2.0, 0.0],
        search_radius=1.0
    )

    try:
        rclpy.spin(task_manager)
    except KeyboardInterrupt:
        task_manager.get_logger().info('Shutting down task manager...')
    finally:
        task_manager.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Update `setup.py` to include the task manager:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_nav_manip_lab'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/maps', glob('maps/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Isaac Navigation and Manipulation Lab Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'nav_manip_controller = isaac_nav_manip_lab.nav_manip_controller:main',
            'perception_simulator = isaac_nav_manip_lab.perception_simulator:main',
            'task_manager = isaac_nav_manip_lab.task_manager:main',
        ],
    },
)
```

Rebuild the package:

```bash
cd ~/ros2_lab_ws
colcon build --packages-select isaac_nav_manip_lab
source install/setup.bash
```

## Step 10: Run the Complete System

**Terminal 1 - Start the complete system:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 launch isaac_nav_manip_lab nav_manip_system_launch.py
```

**Terminal 2 - Start the task manager:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run isaac_nav_manip_lab task_manager
```

**Terminal 3 - Monitor the system:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Monitor task state
ros2 topic echo /task_state

# Monitor navigation
ros2 topic echo /odom

# Monitor sensor data
ros2 topic echo /scan
```

## Lab Questions

1. How does the navigation and manipulation system coordinate between different tasks?
2. What are the key components needed for a complete navigation and manipulation pipeline?
3. How does the perception simulator contribute to the overall system?
4. What safety measures are implemented in the system to handle failures?
5. How could you extend this system to handle multiple objects or more complex manipulation tasks?

## Summary

In this lab, you learned how to:
- Integrate navigation and manipulation capabilities in a single system
- Create a state machine for coordinating complex robotic tasks
- Simulate perception data for testing navigation and manipulation
- Implement task management for autonomous operation
- Use Isaac tools for creating a complete robotic system

This comprehensive system demonstrates the integration of navigation, perception, and manipulation capabilities that are essential for autonomous robotic applications.