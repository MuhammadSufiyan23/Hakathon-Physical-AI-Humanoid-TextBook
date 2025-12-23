---
sidebar_label: 'Carter Robot: Isaac Reference Platform'
title: 'Carter Robot: Isaac Reference Platform'
---

# Carter Robot: Isaac Reference Platform

## Overview of the Carter Robot

The Carter robot is NVIDIA's reference platform for demonstrating the capabilities of the Isaac platform. It serves as a complete example of how to build, simulate, and deploy AI-powered mobile robots using NVIDIA's robotics ecosystem.

## Carter Robot Specifications

### Physical Characteristics
- **Dimensions**: 0.8m (L) × 0.6m (W) × 0.6m (H)
- **Weight**: ~50 kg
- **Maximum Speed**: 1.0 m/s
- **Payload Capacity**: 20 kg
- **Battery Life**: 4-6 hours continuous operation
- **Operating Temperature**: 0°C to 40°C

### Sensor Suite
- **LiDAR**: 360° SICK LiDAR (20m range)
- **Cameras**:
  - Stereo cameras for depth perception
  - RGB cameras for visual navigation
  - Fish-eye cameras for wide-angle view
- **IMU**: 9-axis inertial measurement unit
- **Wheel Encoders**: Precision odometry
- **Bumpers**: Collision detection

### Computing Hardware
- **GPU**: NVIDIA Jetson AGX Xavier or Orin
- **CPU**: ARM-based processor
- **Memory**: 16GB+ RAM
- **Storage**: 512GB+ SSD
- **Connectivity**: Wi-Fi 6, Ethernet, Bluetooth

## Carter Robot in Isaac Sim

### Simulation Model

The Carter robot in Isaac Sim is a highly detailed model that includes:

```python
# Carter robot configuration in Isaac Sim
import omni
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage

class CarterRobotSim:
    def __init__(self, name="Carter", position=[0, 0, 0], orientation=[0, 0, 0, 1]):
        self.name = name
        self.position = position
        self.orientation = orientation
        self.robot = None

    def load_robot(self, world):
        """Load the Carter robot into the simulation."""
        assets_root_path = get_assets_root_path()
        carter_path = assets_root_path + "/Isaac/Robots/Carter/carter.usd"

        add_reference_to_stage(
            usd_path=carter_path,
            prim_path=f"/World/{self.name}"
        )

        self.robot = world.scene.add(
            Robot(
                prim_path=f"/World/{self.name}",
                name=self.name,
                position=self.position,
                orientation=self.orientation
            )
        )

    def setup_sensors(self):
        """Configure the robot's sensor suite."""
        # Configure LiDAR
        self.setup_lidar()

        # Configure cameras
        self.setup_cameras()

        # Configure IMU
        self.setup_imu()

    def setup_lidar(self):
        """Setup 360-degree LiDAR sensor."""
        # LiDAR configuration for Carter
        lidar_config = {
            "prim_path": f"/World/{self.name}/base_link/lidar",
            "name": "carter_lidar",
            "rotation_frequency": 10,
            "points_per_second": 500000,
            "laser_as_line": False,
            "enable_computed_fix": True
        }
        # Implementation details for LiDAR setup
        pass

    def setup_cameras(self):
        """Setup stereo and RGB cameras."""
        # Stereo camera configuration
        stereo_config = {
            "name": "stereo_camera",
            "resolution": [640, 480],
            "position": [0.2, 0, 0.3],
            "focal_length": 24.0
        }
        # RGB camera configuration
        rgb_config = {
            "name": "rgb_camera",
            "resolution": [1280, 720],
            "position": [0.15, 0, 0.4],
            "focal_length": 18.0
        }
        # Implementation details for camera setup
        pass

    def setup_imu(self):
        """Setup IMU sensor."""
        # IMU configuration
        imu_config = {
            "name": "imu_sensor",
            "position": [0, 0, 0.2],
            "orientation": [0, 0, 0, 1]
        }
        # Implementation details for IMU setup
        pass
```

### Carter Robot URDF for ROS 2 Integration

```xml
<?xml version="1.0"?>
<robot name="carter" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="50.0"/>
      <origin xyz="0 0 0.3" rpy="0 0 0"/>
      <inertia ixx="4.167" ixy="0.0" ixz="0.0" iyy="6.667" iyz="0.0" izz="10.417"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0.3" rpy="0 0 0"/>
      <geometry>
        <box size="0.8 0.6 0.6"/>
      </geometry>
      <material name="orange">
        <color rgba="1.0 0.4235294117647059 0.0392156862745098 1.0"/>
      </material>
    </visual>

    <collision>
      <origin xyz="0 0 0.3" rpy="0 0 0"/>
      <geometry>
        <box size="0.8 0.6 0.6"/>
      </geometry>
    </collision>
  </link>

  <!-- Front left wheel -->
  <link name="front_left_wheel">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.04"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Front right wheel -->
  <link name="front_right_wheel">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.04"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
    </visual>

    <collision>
      <origin xyz="0 0 0" rpy="1.570796 0 0"/>
      <geometry>
        <cylinder radius="0.15" length="0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Rear wheels (same as front) -->
  <link name="rear_left_wheel">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.04"/>
    </inertial>
  </link>

  <link name="rear_right_wheel">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.04"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="front_left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="front_left_wheel"/>
    <origin xyz="0.3 -0.25 0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <joint name="front_right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="front_right_wheel"/>
    <origin xyz="0.3 0.25 0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <joint name="rear_left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="rear_left_wheel"/>
    <origin xyz="-0.3 -0.25 0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <joint name="rear_right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="rear_right_wheel"/>
    <origin xyz="-0.3 0.25 0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <!-- LiDAR mount -->
  <link name="lidar_link">
    <inertial>
      <mass value="0.5"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
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
    <origin xyz="0.0 0.0 0.6" rpy="0 0 0"/>
  </joint>

  <!-- Camera mount -->
  <link name="camera_link">
    <inertial>
      <mass value="0.1"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.35 0.0 0.4" rpy="0 0 0"/>
  </joint>

  <!-- ros2_control interface -->
  <ros2_control name="CarterSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>
    <joint name="front_left_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-1.0</param>
        <param name="max">1.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="front_right_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-1.0</param>
        <param name="max">1.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="rear_left_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-1.0</param>
        <param name="max">1.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
    <joint name="rear_right_wheel_joint">
      <command_interface name="velocity">
        <param name="min">-1.0</param>
        <param name="max">1.0</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>

  <!-- Gazebo plugins -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find carter_description)/config/carter_control.yaml</parameters>
    </plugin>
  </gazebo>
</robot>
```

## Carter Robot Navigation Stack

### Base Navigation Configuration

```yaml
# config/carter_navigation.yaml
amcl:
  ros__parameters:
    use_sim_time: True
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_link"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 10.0
    laser_min_range: -1.0
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.5
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    scan_topic: scan
    set_initial_pose: true
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05

bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    default_bt_xml_filename: "navigate_w_replanning_and_recovery.xml"
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_goal_reached_condition_bt_node
    - nav2_goal_updated_condition_bt_node
    - nav2_initial_pose_received_condition_bt_node
    - nav2_reinitialize_global_localization_service_bt_node
    - nav2_rate_controller_bt_node
    - nav2_distance_controller_bt_node
    - nav2_speed_controller_bt_node
    - nav2_truncate_path_action_bt_node
    - nav2_goal_updater_node_bt_node
    - nav2_recovery_node_bt_node
    - nav2_pipeline_sequence_bt_node
    - nav2_round_robin_node_bt_node
    - nav2_transform_available_condition_bt_node
    - nav2_time_expired_condition_bt_node
    - nav2_path_expiring_timer_condition
    - nav2_distance_traveled_condition_bt_node
    - nav2_single_trigger_bt_node
    - nav2_is_battery_low_condition_bt_node
    - nav2_navigate_through_poses_action_bt_node
    - nav2_navigate_to_pose_action_bt_node
    - nav2_remove_passed_goals_action_bt_node
    - nav2_planner_selector_bt_node
    - nav2_controller_selector_bt_node
    - nav2_goal_checker_selector_bt_node

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # Progress checker parameters
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    # Goal checker parameters
    goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful: True

    # DWB parameters
    FollowPath:
      plugin: "nav2_controllers::DWBLocalPlanner"
      debug_trajectory_details: True
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.5
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 5
      vtheta_samples: 20
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: True
      stateful: True
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0
```

## Carter Robot Perception Stack

### Isaac ROS Integration

```python
# Carter robot perception pipeline using Isaac ROS
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, CameraInfo
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PointStamped
from visualization_msgs.msg import MarkerArray
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

class CarterPerceptionNode(Node):
    def __init__(self):
        super().__init__('carter_perception')

        # Initialize Isaac ROS components
        self.initialize_isaac_components()

        # Create subscribers for sensor data
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/carter/scan',
            self.lidar_callback,
            10
        )

        self.camera_sub = self.create_subscription(
            Image,
            '/carter/camera/image_raw',
            self.camera_callback,
            10
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/carter/camera/camera_info',
            self.camera_info_callback,
            10
        )

        # Create publishers for processed data
        self.map_pub = self.create_publisher(
            OccupancyGrid,
            '/carter/map',
            10
        )

        self.obstacles_pub = self.create_publisher(
            MarkerArray,
            '/carter/obstacles',
            10
        )

        # Initialize perception components
        self.initialize_perception_pipeline()

    def initialize_isaac_components(self):
        """Initialize Isaac ROS components."""
        # Initialize Isaac image processing components
        # This would include rectification, feature detection, etc.
        pass

    def initialize_perception_pipeline(self):
        """Initialize the complete perception pipeline."""
        # Initialize SLAM components
        self.slam_initialized = False

        # Initialize obstacle detection
        self.obstacle_detector = ObstacleDetector()

        # Initialize object recognition
        self.object_recognizer = ObjectRecognizer()

    def lidar_callback(self, msg):
        """Process LiDAR data for obstacle detection and mapping."""
        # Process LiDAR scan for obstacles
        obstacles = self.detect_obstacles_lidar(msg)

        # Update occupancy grid
        if self.slam_initialized:
            self.update_occupancy_grid(msg)

        # Publish obstacle markers
        obstacle_markers = self.create_obstacle_markers(obstacles)
        self.obstacles_pub.publish(obstacle_markers)

    def camera_callback(self, msg):
        """Process camera data for visual perception."""
        # Process camera image for object detection
        objects = self.detect_objects_camera(msg)

        # Perform visual SLAM if available
        if hasattr(self, 'visual_slam'):
            self.visual_slam.process_image(msg)

    def camera_info_callback(self, msg):
        """Process camera calibration information."""
        # Store camera calibration for rectification
        self.camera_matrix = msg.k
        self.distortion_coeffs = msg.d

    def detect_obstacles_lidar(self, scan_msg):
        """Detect obstacles from LiDAR data."""
        obstacles = []

        # Process scan ranges to detect obstacles
        for i, range_val in enumerate(scan_msg.ranges):
            if 0.1 < range_val < 3.0:  # Valid range
                angle = scan_msg.angle_min + i * scan_msg.angle_increment
                x = range_val * math.cos(angle)
                y = range_val * math.sin(angle)

                if self.is_obstacle_point(x, y):
                    obstacles.append((x, y))

        return obstacles

    def create_obstacle_markers(self, obstacles):
        """Create visualization markers for obstacles."""
        marker_array = MarkerArray()

        for i, (x, y) in enumerate(obstacles):
            marker = Marker()
            marker.header = Header()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "obstacles"
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD

            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0

            marker.scale.x = 0.2  # Diameter
            marker.scale.y = 0.2
            marker.scale.z = 1.0  # Height

            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.8

            marker_array.markers.append(marker)

        return marker_array

class ObstacleDetector:
    """Obstacle detection component."""
    def __init__(self):
        # Initialize obstacle detection parameters
        self.min_obstacle_size = 0.1
        self.max_obstacle_distance = 3.0

    def detect_from_scan(self, scan_data):
        """Detect obstacles from scan data."""
        # Implementation for obstacle detection
        pass

class ObjectRecognizer:
    """Object recognition component using Isaac ROS."""
    def __init__(self):
        # Initialize object recognition model
        pass

    def recognize(self, image_data):
        """Recognize objects in image data."""
        # Implementation for object recognition
        pass

def main(args=None):
    rclpy.init(args=args)
    perception_node = CarterPerceptionNode()

    try:
        rclpy.spin(perception_node)
    except KeyboardInterrupt:
        pass
    finally:
        perception_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Carter Robot Control System

### Differential Drive Controller

```python
# Carter robot control system
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import math

class CarterController(Node):
    def __init__(self):
        super().__init__('carter_controller')

        # Robot parameters
        self.wheel_base = 0.5  # Distance between front and rear wheels
        self.wheel_track = 0.5  # Distance between left and right wheels
        self.max_linear_vel = 1.0
        self.max_angular_vel = 1.0

        # Robot state
        self.current_pose = [0.0, 0.0, 0.0]  # x, y, theta
        self.current_velocity = [0.0, 0.0]    # linear, angular

        # Create subscribers and publishers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.odom_pub = self.create_publisher(
            Odometry,
            '/odom',
            10
        )

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer for odometry update
        self.timer = self.create_timer(0.05, self.update_odometry)  # 20 Hz

    def cmd_vel_callback(self, msg):
        """Handle velocity commands."""
        # Limit velocities
        linear_vel = max(-self.max_linear_vel, min(self.max_linear_vel, msg.linear.x))
        angular_vel = max(-self.max_angular_vel, min(self.max_angular_vel, msg.angular.z))

        self.current_velocity = [linear_vel, angular_vel]

        # Publish to hardware interface
        self.publish_to_hardware(linear_vel, angular_vel)

    def update_odometry(self):
        """Update robot odometry."""
        dt = 0.05  # Time step from timer

        # Update pose based on current velocity
        linear_vel, angular_vel = self.current_velocity

        if abs(angular_vel) < 1e-6:  # Straight line motion
            self.current_pose[0] += linear_vel * dt * math.cos(self.current_pose[2])
            self.current_pose[1] += linear_vel * dt * math.sin(self.current_pose[2])
        else:  # Arc motion
            radius = linear_vel / angular_vel if abs(linear_vel) > 1e-6 else 0
            dx = radius * (math.sin(self.current_pose[2] + angular_vel * dt) - math.sin(self.current_pose[2]))
            dy = radius * (math.cos(self.current_pose[2]) - math.cos(self.current_pose[2] + angular_vel * dt))
            dtheta = angular_vel * dt

            self.current_pose[0] += dx
            self.current_pose[1] += dy
            self.current_pose[2] += dtheta

            # Normalize angle
            self.current_pose[2] = math.atan2(
                math.sin(self.current_pose[2]),
                math.cos(self.current_pose[2])
            )

        # Publish odometry
        self.publish_odometry()

    def publish_odometry(self):
        """Publish odometry message."""
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        # Position
        odom_msg.pose.pose.position.x = self.current_pose[0]
        odom_msg.pose.pose.position.y = self.current_pose[1]
        odom_msg.pose.pose.position.z = 0.0

        # Orientation (as quaternion)
        from tf_transformations import quaternion_from_euler
        quat = quaternion_from_euler(0, 0, self.current_pose[2])
        odom_msg.pose.pose.orientation.x = quat[0]
        odom_msg.pose.pose.orientation.y = quat[1]
        odom_msg.pose.pose.orientation.z = quat[2]
        odom_msg.pose.pose.orientation.w = quat[3]

        # Velocity
        odom_msg.twist.twist.linear.x = self.current_velocity[0]
        odom_msg.twist.twist.angular.z = self.current_velocity[1]

        self.odom_pub.publish(odom_msg)

        # Broadcast transform
        from geometry_msgs.msg import TransformStamped
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = self.current_pose[0]
        t.transform.translation.y = self.current_pose[1]
        t.transform.translation.z = 0.0

        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]

        self.tf_broadcaster.sendTransform(t)

    def publish_to_hardware(self, linear_vel, angular_vel):
        """Publish velocity commands to hardware interface."""
        # This would interface with the actual robot hardware
        # For simulation, this might publish to Gazebo or Isaac Sim
        pass

def main(args=None):
    rclpy.init(args=args)
    controller = CarterController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Carter Robot Applications

### Warehouse Navigation Example

```python
# Carter robot warehouse navigation application
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

class CarterWarehouseNavigator(Node):
    def __init__(self):
        super().__init__('carter_warehouse_navigator')

        # Initialize navigation action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Warehouse locations
        self.locations = {
            'charging_station': (0.0, 0.0, 0.0),
            'storage_area_1': (5.0, 3.0, 1.57),
            'storage_area_2': (-2.0, 4.0, 3.14),
            'loading_dock': (8.0, -1.0, 0.0),
            'inspection_area': (2.0, -3.0, -1.57)
        }

        # Task queue
        self.task_queue = []
        self.current_task = None

    def navigate_to_location(self, location_name):
        """Navigate to a predefined location."""
        if location_name not in self.locations:
            self.get_logger().error(f'Unknown location: {location_name}')
            return False

        x, y, theta = self.locations[location_name]

        # Wait for action server
        self.nav_client.wait_for_server()

        # Create goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert theta to quaternion
        from tf_transformations import quaternion_from_euler
        quat = quaternion_from_euler(0, 0, theta)
        goal_msg.pose.pose.orientation.x = quat[0]
        goal_msg.pose.pose.orientation.y = quat[1]
        goal_msg.pose.pose.orientation.z = quat[2]
        goal_msg.pose.pose.orientation.w = quat[3]

        # Send goal
        self.get_logger().info(f'Navigating to {location_name} at ({x}, {y})')
        send_goal_future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(self.goal_response_callback)
        return True

    def feedback_callback(self, feedback_msg):
        """Handle navigation feedback."""
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Navigating... Progress: {feedback.distance_remaining:.2f}m remaining')

    def goal_response_callback(self, future):
        """Handle goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted, waiting for result...')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle navigation result."""
        result = future.result().result
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Navigation succeeded!')
        else:
            self.get_logger().info(f'Navigation failed with status: {status}')

        # Process next task if available
        self.process_next_task()

    def add_task(self, location_name):
        """Add a navigation task to the queue."""
        self.task_queue.append(location_name)
        self.get_logger().info(f'Added task: navigate to {location_name}')

        # Start processing if no current task
        if self.current_task is None:
            self.process_next_task()

    def process_next_task(self):
        """Process the next task in the queue."""
        if self.task_queue:
            next_location = self.task_queue.pop(0)
            self.current_task = next_location
            self.navigate_to_location(next_location)
        else:
            self.current_task = None
            self.get_logger().info('Task queue empty')

def main(args=None):
    rclpy.init(args=args)
    navigator = CarterWarehouseNavigator()

    # Example: Navigate through warehouse locations
    navigator.add_task('storage_area_1')
    navigator.add_task('loading_dock')
    navigator.add_task('inspection_area')
    navigator.add_task('charging_station')

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

The Carter robot serves as an excellent reference platform for understanding the NVIDIA Isaac ecosystem. Its comprehensive sensor suite, robust navigation capabilities, and integration with Isaac tools provide a complete example of how to build production-ready autonomous mobile robots. Understanding the Carter robot's architecture, simulation model, and software stack is essential for developing similar robotic systems using the Isaac platform.