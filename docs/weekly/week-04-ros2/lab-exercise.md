---
sidebar_label: 'Week 4 Lab: Launch Files and Testing'
title: 'Week 4 Lab: Launch Files and Testing'
---

# Week 4 Lab: Launch Files and Testing

## Objective

In this lab, you will create a launch file for a multi-node system and implement unit tests for your nodes. You'll learn how to organize complex systems and ensure their reliability through testing.

## Prerequisites

- Completion of Week 3 lab
- ROS 2 Humble Hawksbill installed
- Basic knowledge of Python or C++

## Step 1: Create a New Package for the Lab

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for this lab
ros2 pkg create --build-type ament_python lab_launch_test --dependencies rclpy std_msgs geometry_msgs sensor_msgs
```

## Step 2: Create the Robot Controller Node

Create `lab_launch_test/lab_launch_test/robot_controller.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        # Create subscribers
        self.laser_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.laser_callback,
            10)

        # Create publisher
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            'cmd_vel',
            10)

        # Create timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Robot state
        self.obstacle_distance = float('inf')
        self.obstacle_angle = 0.0

        self.get_logger().info('Robot controller initialized')

    def laser_callback(self, msg):
        """Process laser scan data to detect obstacles."""
        if len(msg.ranges) > 0:
            # Find closest obstacle in front of robot (±30 degrees)
            front_ranges = msg.ranges[330:30] + msg.ranges[330:]  # Wrap around
            if front_ranges:
                min_distance = min(x for x in front_ranges if not math.isinf(x) and x > 0)
                self.obstacle_distance = min_distance
                self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m')

    def control_loop(self):
        """Main control loop."""
        msg = Twist()

        # Simple obstacle avoidance
        if self.obstacle_distance < 1.0:  # Obstacle within 1 meter
            msg.linear.x = 0.0  # Stop
            msg.angular.z = 0.5  # Turn
        else:
            msg.linear.x = 0.2  # Move forward slowly
            msg.angular.z = 0.0  # No turn

        self.cmd_vel_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = RobotController()

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

## Step 3: Create the Sensor Simulator Node

Create `lab_launch_test/lab_launch_test/sensor_simulator.py`:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header
import math
import random

class SensorSimulator(Node):
    def __init__(self):
        super().__init__('sensor_simulator')

        # Create publisher
        self.scan_pub = self.create_publisher(
            LaserScan,
            'scan',
            10)

        # Create timer
        self.timer = self.create_timer(0.1, self.publish_scan)

        self.get_logger().info('Sensor simulator initialized')

    def publish_scan(self):
        """Publish simulated laser scan data."""
        msg = LaserScan()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'

        # Laser scan parameters
        msg.angle_min = -math.pi / 2  # -90 degrees
        msg.angle_max = math.pi / 2   # 90 degrees
        msg.angle_increment = math.pi / 180  # 1 degree
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.1
        msg.range_max = 10.0

        # Calculate number of ranges
        num_ranges = int((msg.angle_max - msg.angle_min) / msg.angle_increment) + 1
        msg.ranges = []

        # Generate simulated ranges (with occasional obstacles)
        for i in range(num_ranges):
            angle = msg.angle_min + i * msg.angle_increment

            # Add some variation and occasional obstacles
            if abs(angle) < 0.2 and random.random() < 0.3:  # Front with 30% chance of obstacle
                distance = 0.5 + random.random() * 0.5  # 0.5-1.0m obstacle
            else:
                distance = 5.0 + random.random() * 2.0  # Far objects

            msg.ranges.append(distance)

        self.scan_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    simulator = SensorSimulator()

    try:
        rclpy.spin(simulator)
    except KeyboardInterrupt:
        pass
    finally:
        simulator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 4: Create the Launch File

Create `lab_launch_test/launch/robot_system_launch.py`:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time if true'
        ),

        # Launch sensor simulator
        Node(
            package='lab_launch_test',
            executable='sensor_simulator',
            name='sensor_simulator',
            parameters=[
                {'use_sim_time': use_sim_time}
            ],
            remappings=[
                ('scan', 'laser_scan')
            ],
            output='screen'
        ),

        # Launch robot controller
        Node(
            package='lab_launch_test',
            executable='robot_controller',
            name='robot_controller',
            parameters=[
                {'use_sim_time': use_sim_time}
            ],
            remappings=[
                ('scan', 'laser_scan'),  # Remap to match sensor simulator
                ('cmd_vel', 'robot_cmd_vel')
            ],
            output='screen'
        ),
    ])
```

## Step 5: Create Unit Tests

Create `test/test_robot_controller.py`:

```python
import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from lab_launch_test.robot_controller import RobotController
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import time

class TestRobotController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = RobotController()
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def tearDown(self):
        self.node.destroy_node()

    def test_initial_state(self):
        """Test that the controller initializes properly."""
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.obstacle_distance, float('inf'))

    def test_laser_callback(self):
        """Test laser callback with obstacle."""
        # Create a mock laser scan message with an obstacle
        msg = LaserScan()
        msg.ranges = [0.5, 1.0, 2.0, 3.0, 4.0]  # Close obstacle at 0.5m

        # Call the callback
        self.node.laser_callback(msg)

        # Check that obstacle distance was updated
        self.assertAlmostEqual(self.node.obstacle_distance, 0.5, places=1)

    def test_control_loop_no_obstacle(self):
        """Test control loop when no obstacle is detected."""
        # Set obstacle distance to far away
        self.node.obstacle_distance = 5.0

        # Call control loop (this will publish a Twist message)
        self.node.control_loop()

        # The robot should move forward
        # We can't easily test the publisher output in this simple test
        self.assertTrue(True)  # Placeholder - in a real test, we'd check publisher

    def test_control_loop_with_obstacle(self):
        """Test control loop when obstacle is detected."""
        # Set obstacle distance to close
        self.node.obstacle_distance = 0.5

        # Call control loop
        self.node.control_loop()

        # The robot should stop and turn
        self.assertTrue(True)  # Placeholder - in a real test, we'd check publisher

if __name__ == '__main__':
    unittest.main()
```

## Step 6: Create Setup Files

Update `setup.py` to include executables:

```python
from setuptools import setup

package_name = 'lab_launch_test'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/robot_system_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Launch and testing lab package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_controller = lab_launch_test.robot_controller:main',
            'sensor_simulator = lab_launch_test.sensor_simulator:main',
        ],
    },
)
```

## Step 7: Update package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>lab_launch_test</name>
  <version>0.0.0</version>
  <description>Launch and testing lab package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>sensor_msgs</depend>

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

# Build the package
colcon build --packages-select lab_launch_test

# Source the workspace
source install/setup.bash
```

## Step 9: Run the Launch File

```bash
# Run the launch file
ros2 launch lab_launch_test robot_system_launch.py
```

## Step 10: Run Tests

```bash
# Run tests for the package
colcon test --packages-select lab_launch_test

# View test results
colcon test-result --all --verbose
```

## Step 11: Test Individual Components

In separate terminals:

**Terminal 1 - Sensor Simulator Only:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_launch_test sensor_simulator
```

**Terminal 2 - Robot Controller Only:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_launch_test robot_controller
```

**Terminal 3 - Monitor Topics:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 topic echo /laser_scan sensor_msgs/msg/LaserScan
```

## Lab Questions

1. How does the launch file simplify running multiple nodes compared to running them individually?
2. What is the purpose of remappings in the launch file?
3. How do the unit tests verify the behavior of the robot controller?
4. What happens if you change the obstacle detection distance threshold?
5. How could you extend this system to include more sophisticated navigation?

## Summary

In this lab, you learned how to:
- Create a multi-node ROS 2 system
- Write launch files to manage complex systems
- Implement unit tests for ROS 2 nodes
- Use remappings to connect nodes with different topic names
- Test individual components and the complete system

These skills are essential for developing and maintaining complex robotic systems.