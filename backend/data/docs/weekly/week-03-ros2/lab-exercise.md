---
sidebar_label: 'Week 3 Lab: Creating Your First ROS 2 Package'
title: 'Week 3 Lab: Creating Your First ROS 2 Package'
---

# Week 3 Lab: Creating Your First ROS 2 Package

## Objective

In this lab, you will create your first ROS 2 package that implements a simple publisher-subscriber system. By the end of this lab, you will understand how to create, build, and run a basic ROS 2 package.

## Prerequisites

- ROS 2 Humble Hawksbill installed
- Basic knowledge of Python or C++
- Terminal/command line familiarity

## Step 1: Create a Workspace

First, create a new ROS 2 workspace for this lab:

```bash
# Create workspace directory
mkdir -p ~/ros2_lab_ws/src
cd ~/ros2_lab_ws
```

## Step 2: Create a New Package

Create a new package called `lab_publisher_subscriber`:

```bash
# Navigate to the src directory
cd src

# Create a new Python package
ros2 pkg create --build-type ament_python lab_publisher_subscriber
```

## Step 3: Navigate to the Package Directory

```bash
cd lab_publisher_subscriber
```

## Step 4: Create the Publisher Node

Create a new Python file for the publisher in `lab_publisher_subscriber/lab_publisher_subscriber/publisher_member_function.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()

    try:
        rclpy.spin(minimal_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        minimal_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 5: Create the Subscriber Node

Create a new Python file for the subscriber in `lab_publisher_subscriber/lab_publisher_subscriber/subscriber_member_function.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()

    try:
        rclpy.spin(minimal_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        minimal_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 6: Update setup.py

Edit the `setup.py` file to include the new nodes as executables:

```python
from setuptools import setup

package_name = 'lab_publisher_subscriber'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Simple publisher subscriber lab',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = lab_publisher_subscriber.publisher_member_function:main',
            'listener = lab_publisher_subscriber.subscriber_member_function:main',
        ],
    },
)
```

## Step 7: Build the Package

Navigate back to the workspace root and build the package:

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select lab_publisher_subscriber

# Source the workspace
source install/setup.bash
```

## Step 8: Run the Publisher and Subscriber

Open two terminal windows:

**Terminal 1 (Publisher):**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_publisher_subscriber talker
```

**Terminal 2 (Subscriber):**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run lab_publisher_subscriber listener
```

You should see the publisher sending messages and the subscriber receiving them.

## Step 9: Create a Launch File

Create a launch directory and file to run both nodes simultaneously:

```bash
# Create launch directory
mkdir -p ~/ros2_lab_ws/src/lab_publisher_subscriber/launch
```

Create `~/ros2_lab_ws/src/lab_publisher_subscriber/launch/talker_listener_launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='lab_publisher_subscriber',
            executable='talker',
            name='talker',
        ),
        Node(
            package='lab_publisher_subscriber',
            executable='listener',
            name='listener',
        ),
    ])
```

## Step 10: Update package.xml

Make sure your `package.xml` includes the necessary dependencies:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>lab_publisher_subscriber</name>
  <version>0.0.0</version>
  <description>Simple publisher subscriber lab</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Step 11: Run with Launch File

```bash
# Build again after adding launch file
cd ~/ros2_lab_ws
colcon build --packages-select lab_publisher_subscriber
source install/setup.bash

# Run with launch file
ros2 launch lab_publisher_subscriber talker_listener_launch.py
```

## Lab Questions

1. What is the purpose of the `create_publisher` and `create_subscription` methods?
2. How does the Quality of Service (QoS) profile affect communication in your nodes?
3. What happens if you change the timer period in the publisher?
4. How does the launch file simplify running multiple nodes?

## Summary

In this lab, you learned how to:
- Create a new ROS 2 package
- Implement publisher and subscriber nodes
- Build and run ROS 2 packages
- Create and use launch files for multiple nodes

This foundation will be essential as you continue developing more complex ROS 2 applications.