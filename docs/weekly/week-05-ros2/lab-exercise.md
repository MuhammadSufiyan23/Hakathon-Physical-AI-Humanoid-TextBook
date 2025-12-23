---
sidebar_label: 'Week 5 Lab: Middleware and Actions'
title: 'Week 5 Lab: Middleware and Actions'
---

# Week 5 Lab: Middleware and Actions

## Objective

In this lab, you will explore ROS 2 middleware configuration and implement a complex action server. You'll learn how to configure Quality of Service settings and create robust action-based systems.

## Prerequisites

- Completion of Weeks 1-4 labs
- ROS 2 Humble Hawksbill installed
- Basic knowledge of Python or C++

## Step 1: Create a New Package for the Lab

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for this lab
ros2 pkg create --build-type ament_python lab_middleware_actions --dependencies rclpy std_msgs action_msgs example_interfaces
```

## Step 2: Create a Custom Action Definition

Create a directory for action files:

```bash
mkdir -p ~/ros2_lab_ws/src/lab_middleware_actions/action
```

Create `~/ros2_lab_ws/src/lab_middleware_actions/action/MoveRobot.action`:

```
# Goal: Request to move robot to a specific position
float64 target_x
float64 target_y
float64 target_theta
---
# Result: Final position and success status
bool success
float64 final_x
float64 final_y
float64 final_theta
string message
---
# Feedback: Current progress during movement
float64 current_x
float64 current_y
float64 current_theta
float64 distance_remaining
string status
```

## Step 3: Create the Action Server

Create `lab_middleware_actions/lab_middleware_actions/move_robot_server.py`:

```python
import time
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import Float64
from lab_middleware_actions.action import MoveRobot

class MoveRobotActionServer(Node):
    def __init__(self):
        super().__init__('move_robot_action_server')

        # Create QoS profile for action server
        qos_profile = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST
        )

        # Create action server with custom QoS
        self._action_server = ActionServer(
            self,
            MoveRobot,
            'move_robot',
            execute_callback=self.execute_callback,
            callback_group=rclpy.callback_groups.ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

        # Robot state publisher
        self.x_pub = self.create_publisher(Float64, 'robot_x', qos_profile)
        self.y_pub = self.create_publisher(Float64, 'robot_y', qos_profile)
        self.theta_pub = self.create_publisher(Float64, 'robot_theta', qos_profile)

        # Current robot position
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

        self.get_logger().info('MoveRobot action server initialized')

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info(f'Received goal request to move to ({goal_request.target_x}, {goal_request.target_y})')

        # Check if goal is valid (not NaN or infinite)
        if (not (-100.0 <= goal_request.target_x <= 100.0) or
            not (-100.0 <= goal_request.target_y <= 100.0)):
            self.get_logger().info('Goal rejected - invalid coordinates')
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def calculate_distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance between two points."""
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    async def execute_callback(self, goal_handle):
        """Execute the goal."""
        self.get_logger().info('Executing goal...')

        # Feedback and result
        feedback_msg = MoveRobot.Feedback()
        result_msg = MoveRobot.Result()

        # Extract goal parameters
        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y
        target_theta = goal_handle.request.target_theta

        # Calculate initial distance
        initial_distance = self.calculate_distance(
            self.current_x, self.current_y, target_x, target_y)
        self.get_logger().info(f'Initial distance: {initial_distance:.2f}m')

        # Movement simulation
        step_size = 0.1  # Move 0.1m per step
        total_steps = int(initial_distance / step_size)

        for step in range(total_steps + 1):
            # Check if cancel was requested
            if goal_handle.is_cancel_requested:
                result_msg.success = False
                result_msg.message = 'Goal canceled'
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return result_msg

            # Calculate intermediate position
            progress = step / total_steps if total_steps > 0 else 1.0
            self.current_x = self.current_x + (target_x - self.current_x) * progress
            self.current_y = self.current_y + (target_y - self.current_y) * progress
            self.current_theta = self.current_theta + (target_theta - self.current_theta) * progress

            # Calculate remaining distance
            distance_remaining = self.calculate_distance(
                self.current_x, self.current_y, target_x, target_y)

            # Update feedback
            feedback_msg.current_x = self.current_x
            feedback_msg.current_y = self.current_y
            feedback_msg.current_theta = self.current_theta
            feedback_msg.distance_remaining = distance_remaining
            feedback_msg.status = f'Moving... {progress * 100:.1f}% complete'

            # Publish current position
            x_msg = Float64()
            x_msg.data = self.current_x
            y_msg = Float64()
            y_msg.data = self.current_y
            theta_msg = Float64()
            theta_msg.data = self.current_theta

            self.x_pub.publish(x_msg)
            self.y_pub.publish(y_msg)
            self.theta_pub.publish(theta_msg)

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Feedback: {feedback_msg.status} - Distance: {distance_remaining:.2f}m')

            # Simulate movement time
            time.sleep(0.2)

        # Check if goal was canceled during execution
        if goal_handle.is_cancel_requested:
            result_msg.success = False
            result_msg.message = 'Goal canceled during execution'
            goal_handle.canceled()
            self.get_logger().info('Goal canceled during execution')
            return result_msg

        # Set final result
        result_msg.success = True
        result_msg.final_x = self.current_x
        result_msg.final_y = self.current_y
        result_msg.final_theta = self.current_theta
        result_msg.message = f'Robot successfully moved to ({target_x}, {target_y})'

        # Succeed the goal
        goal_handle.succeed()
        self.get_logger().info(f'Result: {result_msg.message}')

        return result_msg

def main(args=None):
    rclpy.init(args=args)
    move_robot_action_server = MoveRobotActionServer()

    try:
        rclpy.spin(move_robot_action_server)
    except KeyboardInterrupt:
        pass
    finally:
        move_robot_action_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 4: Create the Action Client

Create `lab_middleware_actions/lab_middleware_actions/move_robot_client.py`:

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Float64
from lab_middleware_actions.action import MoveRobot

class MoveRobotActionClient(Node):
    def __init__(self):
        super().__init__('move_robot_action_client')

        # Create action client
        self._action_client = ActionClient(
            self,
            MoveRobot,
            'move_robot')

        # Subscribers for robot state
        self.x_sub = self.create_subscription(
            Float64, 'robot_x', self.x_callback, 10)
        self.y_sub = self.create_subscription(
            Float64, 'robot_y', self.y_callback, 10)
        self.theta_sub = self.create_subscription(
            Float64, 'robot_theta', self.theta_callback, 10)

        # Current robot state
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

    def x_callback(self, msg):
        self.current_x = msg.data

    def y_callback(self, msg):
        self.current_y = msg.data

    def theta_callback(self, msg):
        self.current_theta = msg.data

    def send_goal(self, target_x, target_y, target_theta):
        """Send a goal to the action server."""
        goal_msg = MoveRobot.Goal()
        goal_msg.target_x = float(target_x)
        goal_msg.target_y = float(target_y)
        goal_msg.target_theta = float(target_theta)

        self.get_logger().info(f'Waiting for action server...')
        self._action_client.wait_for_server()

        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle the goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        # Get result
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle feedback messages."""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Feedback: {feedback.status} | '
            f'Pos: ({feedback.current_x:.2f}, {feedback.current_y:.2f}) | '
            f'Dist: {feedback.distance_remaining:.2f}m')

    def get_result_callback(self, future):
        """Handle the result."""
        result = future.result().result
        self.get_logger().info(f'Result: {result.message}')
        self.get_logger().info(f'Final position: ({result.final_x:.2f}, {result.final_y:.2f})')

def main(args=None):
    rclpy.init(args=args)
    action_client = MoveRobotActionClient()

    # Send a goal (example: move to x=2.0, y=3.0, theta=1.57)
    action_client.send_goal(2.0, 3.0, 1.57)

    try:
        rclpy.spin(action_client)
    except KeyboardInterrupt:
        pass
    finally:
        action_client.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 5: Create the Bag Recording Node

Create `lab_middleware_actions/lab_middleware_actions/data_recorder.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

class DataRecorder(Node):
    def __init__(self):
        super().__init__('data_recorder')

        # Create different QoS profiles to demonstrate middleware differences
        # Reliable profile for critical data
        reliable_qos = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST
        )

        # Best effort profile for less critical data
        best_effort_qos = QoSProfile(
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST
        )

        # Create subscribers with different QoS
        self.critical_sub = self.create_subscription(
            Float64, 'robot_x', self.critical_callback, reliable_qos)

        self.effort_sub = self.create_subscription(
            String, 'robot_status', self.effort_callback, best_effort_qos)

        # Create publishers
        self.status_pub = self.create_publisher(String, 'robot_status', reliable_qos)

        # Timer for publishing status
        self.timer = self.create_timer(1.0, self.publish_status)

        self.counter = 0
        self.get_logger().info('Data recorder initialized with different QoS profiles')

    def critical_callback(self, msg):
        """Handle critical data (reliable)."""
        self.get_logger().info(f'Critical data received: {msg.data:.2f}', throttle_duration_sec=1.0)

    def effort_callback(self, msg):
        """Handle best-effort data."""
        self.get_logger().info(f'Best-effort data received: {msg.data}', throttle_duration_sec=2.0)

    def publish_status(self):
        """Publish robot status."""
        msg = String()
        msg.data = f'Robot status update #{self.counter}'
        self.status_pub.publish(msg)
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    data_recorder = DataRecorder()

    try:
        rclpy.spin(data_recorder)
    except KeyboardInterrupt:
        pass
    finally:
        data_recorder.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 6: Create Setup Files

Update `setup.py` to include executables and action files:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'lab_middleware_actions'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include action files
        (os.path.join('share', package_name, 'action'), glob('action/*.action')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Middleware and actions lab package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_robot_server = lab_middleware_actions.move_robot_server:main',
            'move_robot_client = lab_middleware_actions.move_robot_client:main',
            'data_recorder = lab_middleware_actions.data_recorder:main',
        ],
    },
)
```

## Step 7: Update package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>lab_middleware_actions</name>
  <version>0.0.0</version>
  <description>Middleware and actions lab package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>action_msgs</depend>
  <depend>example_interfaces</depend>

  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Step 8: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package (this will generate action interfaces)
colcon build --packages-select lab_middleware_actions --symlink-install

# Source the workspace
source install/setup.bash
```

## Step 9: Run the Action Server and Client

**Terminal 1 - Start the action server:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_middleware_actions move_robot_server
```

**Terminal 2 - Start the action client:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_middleware_actions move_robot_client
```

## Step 10: Record Data with Different QoS Settings

**Terminal 3 - Start the data recorder:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_middleware_actions data_recorder
```

**Terminal 4 - Record a bag with different QoS settings:**
```bash
source ~/ros2_lab_ws/install/setup.bash

# Record with compression
ros2 bag record /robot_x /robot_y /robot_theta /robot_status --compression-mode file --compression-format zstd -o qos_test_bag
```

## Step 11: Test Middleware Configuration

Test different middleware implementations:

```bash
# Test with Fast DDS
RMW_IMPLEMENTATION=rmw_fastrtps_cpp ros2 run lab_middleware_actions move_robot_server

# Test with Cyclone DDS (if installed)
RMW_IMPLEMENTATION=rmw_cyclonedx_cpp ros2 run lab_middleware_actions move_robot_server
```

## Step 12: Analyze the Bag File

After stopping the recording:

```bash
# Check bag info
ros2 bag info qos_test_bag

# Play the bag
ros2 bag play qos_test_bag
```

## Lab Questions

1. How do the different QoS profiles affect the communication between nodes?
2. What happens when you cancel the action during execution?
3. How does the feedback mechanism improve the user experience compared to services?
4. What are the advantages of using actions over services for long-running operations?
5. How does the middleware configuration impact the performance of your system?

## Summary

In this lab, you learned how to:
- Create and use custom action definitions
- Implement action servers and clients with feedback and cancellation
- Configure different Quality of Service settings for various data types
- Record and analyze data using ROS 2 bags
- Test different middleware implementations

These advanced concepts are crucial for building robust and efficient robotic systems in ROS 2.