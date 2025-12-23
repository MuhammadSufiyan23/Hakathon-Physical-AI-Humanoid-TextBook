---
sidebar_label: 'Week 8 Lab: Carter Robot Navigation in Isaac Sim'
title: 'Week 8 Lab: Carter Robot Navigation in Isaac Sim'
---

# Week 8 Lab: Carter Robot Navigation in Isaac Sim

## Objective

In this lab, you will set up and configure the Carter robot in Isaac Sim, implement a navigation system, and test it in a simulated warehouse environment. You'll learn how to integrate Isaac tools with ROS 2 for autonomous navigation.

## Prerequisites

- NVIDIA GPU with Compute Capability 6.0+
- Isaac Sim installed
- ROS 2 Humble with navigation2 packages
- Isaac ROS packages installed
- Basic knowledge of navigation stack

## Step 1: Create a New ROS 2 Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for the Isaac lab
ros2 pkg create --build-type ament_python isaac_carter_lab --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros visualization_msgs action_msgs
```

## Step 2: Create Carter Robot Configuration

Create the necessary configuration directories:

```bash
mkdir -p ~/ros2_lab_ws/src/isaac_carter_lab/config
mkdir -p ~/ros2_lab_ws/src/isaac_carter_lab/launch
mkdir -p ~/ros2_lab_ws/src/isaac_carter_lab/maps
```

Create `~/ros2_lab_ws/src/isaac_carter_lab/config/carter_navigation_config.yaml`:

```yaml
# Navigation configuration for Carter robot
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
    laser_max_range: 20.0
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
    scan_topic: "scan"
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
    odom_topic: odom
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

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.3
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
  local_costmap_client:
    ros__parameters:
      use_sim_time: True
  local_costmap_rclcpp_node:
    ros__parameters:
      use_sim_time: True

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.3
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
  global_costmap_client:
    ros__parameters:
      use_sim_time: True
  global_costmap_rclcpp_node:
    ros__parameters:
      use_sim_time: True

map_server:
  ros__parameters:
    use_sim_time: True
    yaml_filename: "carter_warehouse.yaml"

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

## Step 3: Create the Navigation Node

Create `~/ros2_lab_ws/src/isaac_carter_lab/isaac_carter_lab/navigation_manager.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseStamped, Point
from nav2_msgs.action import NavigateToPose
from visualization_msgs.msg import MarkerArray, Marker
from std_msgs.msg import ColorRGBA
from builtin_interfaces.msg import Duration
import math
import time

class IsaacCarterNavigationManager(Node):
    def __init__(self):
        super().__init__('isaac_carter_navigation_manager')

        # Initialize navigation action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Warehouse locations
        self.locations = {
            'charging_station': (0.0, 0.0, 0.0),
            'storage_area_1': (5.0, 3.0, 1.57),
            'storage_area_2': (-2.0, 4.0, 3.14),
            'loading_dock': (8.0, -1.0, 0.0),
            'inspection_area': (2.0, -3.0, -1.57),
            'office': (-3.0, -2.0, 0.0)
        }

        # Task queue
        self.task_queue = []
        self.current_task = None
        self.navigation_active = False

        # Create publishers
        self.marker_pub = self.create_publisher(MarkerArray, 'warehouse_locations', 10)

        # Create timer for task processing
        self.timer = self.create_timer(5.0, self.process_tasks)

        # Publish warehouse locations as markers
        self.publish_warehouse_locations()

        self.get_logger().info('Isaac Carter Navigation Manager initialized')

    def publish_warehouse_locations(self):
        """Publish warehouse locations as visualization markers."""
        marker_array = MarkerArray()

        for i, (name, (x, y, theta)) in enumerate(self.locations.items()):
            # Location marker
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'warehouse_locations'
            marker.id = i
            marker.type = Marker.TEXT_VIEW_FACING
            marker.action = Marker.ADD

            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.5
            marker.pose.orientation.w = 1.0

            marker.scale.z = 0.3  # Text scale
            marker.color.r = 1.0
            marker.color.g = 1.0
            marker.color.b = 1.0
            marker.color.a = 1.0
            marker.text = name

            marker_array.markers.append(marker)

            # Goal position marker
            goal_marker = Marker()
            goal_marker.header.frame_id = 'map'
            goal_marker.header.stamp = self.get_clock().now().to_msg()
            goal_marker.ns = 'warehouse_goals'
            goal_marker.id = i + 100  # Different ID range
            goal_marker.type = Marker.CYLINDER
            goal_marker.action = Marker.ADD

            goal_marker.pose.position.x = x
            goal_marker.pose.position.y = y
            goal_marker.pose.position.z = 0.0
            goal_marker.pose.orientation.w = 1.0

            goal_marker.scale.x = 0.3  # Diameter
            goal_marker.scale.y = 0.3
            goal_marker.scale.z = 0.1  # Height

            goal_marker.color.r = 0.0
            goal_marker.color.g = 1.0
            goal_marker.color.b = 0.0
            goal_marker.color.a = 0.5

            marker_array.markers.append(goal_marker)

        self.marker_pub.publish(marker_array)

    def add_task(self, location_name):
        """Add a navigation task to the queue."""
        if location_name not in self.locations:
            self.get_logger().error(f'Unknown location: {location_name}')
            return False

        self.task_queue.append(location_name)
        self.get_logger().info(f'Added task: navigate to {location_name}')
        self.get_logger().info(f'Task queue size: {len(self.task_queue)}')
        return True

    def process_tasks(self):
        """Process navigation tasks."""
        if self.task_queue and not self.navigation_active:
            next_location = self.task_queue.pop(0)
            self.current_task = next_location
            self.get_logger().info(f'Processing task: navigate to {next_location}')

            # Navigate to the location
            success = self.navigate_to_location(next_location)

            if not success:
                self.get_logger().error(f'Failed to start navigation to {next_location}')
                self.current_task = None

    def navigate_to_location(self, location_name):
        """Navigate to a predefined location."""
        if location_name not in self.locations:
            self.get_logger().error(f'Unknown location: {location_name}')
            return False

        x, y, theta = self.locations[location_name]

        # Wait for action server
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation action server not available')
            return False

        # Create goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
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
        self.get_logger().info(f'Sending navigation goal to {location_name} at ({x}, {y})')
        self.navigation_active = True

        send_goal_future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(self.goal_response_callback)
        return True

    def feedback_callback(self, feedback_msg):
        """Handle navigation feedback."""
        feedback = feedback_msg.feedback
        if feedback:
            self.get_logger().info(
                f'Navigating to {self.current_task}... '
                f'Distance remaining: {feedback.distance_remaining:.2f}m, '
                f'Estimated time: {feedback.estimated_time_remaining.sec}s'
            )

    def goal_response_callback(self, future):
        """Handle goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Navigation goal rejected')
            self.navigation_active = False
            self.current_task = None
            return

        self.get_logger().info('Navigation goal accepted, waiting for result...')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle navigation result."""
        result = future.result().result
        status = future.result().status

        if status == 3:  # SUCCEEDED
            self.get_logger().info(f'Navigation to {self.current_task} succeeded!')
        else:
            self.get_logger().info(f'Navigation to {self.current_task} failed with status: {status}')

        # Reset navigation state
        self.navigation_active = False
        self.current_task = None

def main(args=None):
    rclpy.init(args=args)
    navigator = IsaacCarterNavigationManager()

    # Add some example tasks to the queue
    navigator.add_task('storage_area_1')
    navigator.add_task('loading_dock')
    navigator.add_task('inspection_area')
    navigator.add_task('charging_station')
    navigator.add_task('office')

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        navigator.get_logger().info('Shutting down navigation manager...')
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 4: Create Isaac Sim Python Script

Create `~/ros2_lab_ws/src/isaac_carter_lab/isaac_carter_lab/isaac_sim_setup.py`:

```python
#!/usr/bin/env python3

"""
Isaac Sim setup script for Carter robot navigation lab
This script sets up the simulation environment for the Carter robot
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage, get_stage_units
from omni.isaac.core.utils.carb import set_carb_setting
from omni.isaac.range_sensor import _range_sensor
import numpy as np
import math

class IsaacCarterSim:
    def __init__(self):
        self.world = None
        self.robot = None
        self.lidar_sensor = None

    def setup_environment(self):
        """Setup the Isaac Sim environment with Carter robot."""
        # Set up the world
        self.world = World(stage_units_in_meters=1.0)

        # Get assets root path
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets. Please check your installation.")
            return False

        # Add Carter robot to the stage
        carter_asset_path = assets_root_path + "/Isaac/Robots/Carter/carter.usd"
        add_reference_to_stage(
            usd_path=carter_asset_path,
            prim_path="/World/Carter"
        )

        # Add the robot to the world
        self.robot = self.world.scene.add(
            Robot(
                prim_path="/World/Carter",
                name="carter_robot",
                usd_path=carter_asset_path,
                position=np.array([0.0, 0.0, 0.1]),
                orientation=np.array([0.0, 0.0, 0.0, 1.0])
            )
        )

        # Add a simple warehouse environment
        self.setup_warehouse_environment()

        return True

    def setup_warehouse_environment(self):
        """Setup a simple warehouse environment."""
        import omni.isaac.core.utils.prims as prims
        import omni.isaac.core.utils.stage as stage_utils
        from pxr import Gf, UsdGeom, Sdf

        # Add floor
        prims.create_prim(
            prim_path="/World/floor",
            prim_type="Mesh",
            position=np.array([0, 0, 0]),
            orientation=np.array([0, 0, 0, 1]),
            scale=np.array([20, 20, 1]),
            usd_path=f"{get_assets_root_path()}/Isaac/Props/Grid/default_unit_cube_prim.usd"
        )

        # Add some obstacles to simulate warehouse environment
        obstacles = [
            # Storage racks
            {"name": "rack_1", "pos": [4, 2, 1], "scale": [0.5, 3, 2]},
            {"name": "rack_2", "pos": [-3, 3, 1], "scale": [0.5, 2, 1.5]},
            {"name": "rack_3", "pos": [7, -2, 1], "scale": [0.5, 4, 2.5]},
            {"name": "rack_4", "pos": [1, -4, 1], "scale": [0.5, 2, 1.8]},
        ]

        for i, obs in enumerate(obstacles):
            prims.create_prim(
                prim_path=f"/World/obstacle_{i}",
                prim_type="Mesh",
                position=np.array(obs["pos"]),
                orientation=np.array([0, 0, 0, 1]),
                scale=np.array(obs["scale"]),
                usd_path=f"{get_assets_root_path()}/Isaac/Props/Grid/default_unit_cube_prim.usd"
            )

    def setup_sensors(self):
        """Setup robot sensors."""
        # Setup LiDAR sensor
        self.setup_lidar()

    def setup_lidar(self):
        """Setup 360-degree LiDAR sensor on the robot."""
        # Get the range sensor interface
        self._range_sensor = _range_sensor.acquire_range_sensor_interface()

        # Add LiDAR to the robot
        lidar_config = {
            "prim_path": "/World/Carter/base_link/Lidar",
            "name": "carter_lidar",
            "rotation_frequency": 20,
            "points_per_second": 500000,
            "laser_as_line": False,
            "enable_computed_fix": True
        }

        # This would be the actual implementation to add LiDAR
        # For this example, we'll just log that it would be set up
        print("LiDAR sensor would be configured here in a real implementation")

    def run_simulation(self, steps=1000):
        """Run the simulation for a specified number of steps."""
        if self.world is None:
            print("World not initialized. Call setup_environment first.")
            return

        self.world.reset()

        for i in range(steps):
            self.world.step(render=True)

            # Print robot position periodically
            if i % 100 == 0:
                robot_position, robot_orientation = self.robot.get_world_pose()
                print(f"Step {i}: Robot position: {robot_position[:2]}")

            # Example: Get sensor data (would be implemented in real scenario)
            if i % 50 == 0:
                self.get_sensor_data()

    def get_sensor_data(self):
        """Get sensor data from the robot."""
        # In a real implementation, this would get actual sensor data
        # For this example, we'll simulate some data
        simulated_scan = [2.5 + 0.5 * math.sin(i * 0.1) for i in range(360)]
        return simulated_scan

def main():
    """Main function to run the Isaac Sim setup."""
    sim = IsaacCarterSim()

    print("Setting up Isaac Sim environment...")
    if sim.setup_environment():
        print("Environment setup successful!")

        print("Setting up sensors...")
        sim.setup_sensors()

        print("Starting simulation...")
        sim.run_simulation(steps=500)  # Run for 500 steps
        print("Simulation completed.")
    else:
        print("Failed to setup environment.")

if __name__ == "__main__":
    main()
```

## Step 5: Create Launch Files

Create `~/ros2_lab_ws/src/isaac_carter_lab/launch/carter_navigation_launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    params_file = LaunchConfiguration('params_file', default='carter_navigation_config.yaml')

    # Package names
    pkg_nav2_bringup = FindPackageShare('nav2_bringup')
    pkg_isaac_carter_lab = FindPackageShare('isaac_carter_lab')

    # Map server
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[
            {'yaml_filename': PathJoinSubstitution([pkg_isaac_carter_lab, 'maps', 'carter_warehouse.yaml'])},
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    # Lifecycle manager for map server
    lifecycle_manager_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        parameters=[{'use_sim_time': use_sim_time},
                   {'autostart': True},
                   {'node_names': ['map_server']}],
        output='screen'
    )

    # AMCL
    amcl = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nav2_amcl'),
                'launch',
                'amcl.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Navigation server
    navigation_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': PathJoinSubstitution([pkg_isaac_carter_lab, 'config', params_file])
        }.items()
    )

    # RViz
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

    # Isaac Carter Navigation Manager
    navigation_manager = Node(
        package='isaac_carter_lab',
        executable='navigation_manager',
        name='navigation_manager',
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
            'params_file',
            default_value='carter_navigation_config.yaml',
            description='Full path to the ROS2 parameters file to use for all launched nodes'
        ),
        SetParameter('use_sim_time', use_sim_time),
        map_server,
        lifecycle_manager_map,
        amcl,
        navigation_server,
        # Uncomment the following lines if you want to launch RViz automatically
        # TimerAction(
        #     period=3.0,
        #     actions=[rviz]
        # ),
        navigation_manager
    ])
```

## Step 6: Create Setup Files

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_carter_lab'

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
    description='Isaac Carter robot navigation lab package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_manager = isaac_carter_lab.navigation_manager:main',
            'isaac_sim_setup = isaac_carter_lab.isaac_sim_setup:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>isaac_carter_lab</name>
  <version>0.0.0</version>
  <description>Isaac Carter robot navigation lab package</description>
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
  <depend>action_msgs</depend>

  <exec_depend>nav2_bringup</exec_depend>
  <exec_depend>nav2_map_server</exec_depend>
  <exec_depend>nav2_amcl</exec_depend>
  <exec_depend>nav2_lifecycle_manager</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Step 7: Create a Simple Map File

Create `~/ros2_lab_ws/src/isaac_carter_lab/maps/carter_warehouse.yaml`:

```yaml
image: carter_warehouse.pgm
mode: trinary
resolution: 0.05
origin: [-10, -10, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

For now, we'll create a placeholder map file. In a real scenario, you would generate an actual map.

```bash
# Create a placeholder map file
cd ~/ros2_lab_ws/src/isaac_carter_lab/maps
echo "Creating placeholder map file..."
touch carter_warehouse.pgm
```

## Step 8: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select isaac_carter_lab

# Source the workspace
source install/setup.bash
```

## Step 9: Test the System

**Terminal 1 - Start Isaac Sim (if available):**
```bash
# Start Isaac Sim with Carter robot
# This would be done through Isaac Sim's launcher
# For this lab, we'll simulate the robot in Gazebo instead
```

**Terminal 1 - Start Navigation System:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Use a Gazebo simulation instead of Isaac Sim for this example
ros2 launch isaac_carter_lab carter_navigation_launch.py
```

**Terminal 2 - Start a simulated Carter robot in Gazebo:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Launch a simulated Carter robot (you would need to create this URDF/config)
# For this example, we'll create a simple differential drive robot
```

**Terminal 3 - Monitor the system:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Check topics
ros2 topic list

# Monitor navigation status
ros2 topic echo /navigate_to_pose/_action/status

# Check robot pose
ros2 topic echo /amcl_pose
```

## Step 10: Create a Simple Robot Simulation (Alternative to Isaac Sim)

Since Isaac Sim might not be available, let's create a simple Gazebo simulation for testing:

Create `~/ros2_lab_ws/src/isaac_carter_lab/launch/simple_carter_sim_launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'empty_world.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': '<robot name="carter_sim"><link name="base_link"><visual><geometry><box size="0.8 0.6 0.3"/></geometry></visual></link></robot>'
        }]
    )

    # Spawn robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'carter_sim',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        parameters=[{'use_sim_time': use_sim_time}]
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

## Lab Questions

1. How does the Isaac Carter robot integrate with the ROS 2 navigation stack?
2. What are the key components needed for autonomous navigation in the Isaac platform?
3. How does the navigation manager handle multiple tasks in sequence?
4. What role does the LiDAR sensor play in the navigation system?
5. How could you extend this system to include Isaac Sim-specific features?

## Summary

In this lab, you learned how to:
- Set up a navigation system for the Carter robot using ROS 2 navigation stack
- Create a task management system for autonomous navigation
- Configure navigation parameters for warehouse environments
- Integrate Isaac tools with ROS 2 systems
- Implement visualization for navigation goals and locations

This provides a foundation for developing more complex autonomous navigation systems using the NVIDIA Isaac platform.