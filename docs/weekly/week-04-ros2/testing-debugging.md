---
sidebar_label: 'Testing and Debugging in ROS 2'
title: 'Testing and Debugging in ROS 2'
---

# Testing and Debugging in ROS 2

## Introduction to Testing in ROS 2

Testing is a critical component of developing reliable robotic systems. ROS 2 provides several testing frameworks and tools to ensure your nodes and systems function correctly.

## Unit Testing

### Python Unit Testing

ROS 2 uses standard Python testing frameworks like `pytest` and `unittest`:

```python
import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from example_package.my_node import MyNode

class TestMyNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = MyNode()
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def tearDown(self):
        self.node.destroy_node()

    def test_node_initialization(self):
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.get_name(), 'my_node')

    def test_parameter_declaration(self):
        self.assertTrue(self.node.has_parameter('my_param'))
        self.assertEqual(self.node.get_parameter('my_param').value, 'default_value')

if __name__ == '__main__':
    unittest.main()
```

### C++ Unit Testing

ROS 2 uses Google Test for C++ unit testing:

```cpp
#include <gtest/gtest.h>
#include "rclcpp/rclcpp.hpp"
#include "my_package/my_node.hpp"

class TestMyNode : public ::testing::Test
{
protected:
    void SetUp() override
    {
        rclcpp::init(0, nullptr);
        node = std::make_shared<MyNode>();
    }

    void TearDown() override
    {
        node.reset();
        rclcpp::shutdown();
    }

    std::shared_ptr<MyNode> node;
};

TEST_F(TestMyNode, NodeInitialization)
{
    ASSERT_NE(node, nullptr);
    EXPECT_EQ(node->get_name(), "my_node");
}

TEST_F(TestMyNode, ParameterTest)
{
    auto param_desc = node->describe_parameters({{"my_param"}});
    ASSERT_EQ(param_desc.size(), 1);
    EXPECT_EQ(param_desc[0].name, "my_param");
}

int main(int argc, char ** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
```

## Integration Testing

Integration tests verify that multiple nodes work together correctly:

```python
import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String
from example_interfaces.srv import AddTwoInts

class TestNodeCommunication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_node')
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def test_publisher_subscriber_communication(self):
        # Create publisher and subscriber
        publisher = self.node.create_publisher(String, 'test_topic', 10)
        received_messages = []

        def callback(msg):
            received_messages.append(msg.data)

        subscriber = self.node.create_subscription(
            String, 'test_topic', callback, 10)

        # Publish a message
        test_msg = String()
        test_msg.data = 'test_message'
        publisher.publish(test_msg)

        # Spin to process messages
        self.executor.spin_once(timeout_sec=1.0)

        # Verify message was received
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0], 'test_message')
```

## ROS 2 Testing Tools

### ros2 test

The `ros2 test` command runs tests in a ROS 2 package:

```bash
# Run all tests in a package
colcon test --packages-select my_package

# Run tests with verbose output
colcon test --packages-select my_package --event-handlers console_direct+

# Run specific tests
colcon test --packages-select my_package --ctest-args -R test_name
```

### Launch Testing

ROS 2 provides launch testing for testing complex systems:

```python
import launch
import launch.actions
import launch_ros.actions
import launch_testing.actions
import launch_testing.util
import pytest

@pytest.mark.launch_test
def generate_test_description():
    """Launch a simple system and test it."""
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='demo_node_1'
        ),
        launch_testing.util.KeepAliveProc(),
        launch_testing.actions.ReadyToTest()
    ])

def test_node_running_after_delay(publisher_node, proc_info):
    """Test node is running."""
    proc_info.assertWaitForShutdown(process=publisher_node, timeout=5)
```

## Debugging Tools

### rqt Tools

ROS 2 includes various debugging tools accessible through rqt:

- **rqt_graph**: Visualize the node graph
- **rqt_plot**: Plot numeric values over time
- **rqt_console**: View ROS logs
- **rqt_topic**: Inspect topic messages
- **rqt_service**: Call services

```bash
# Launch rqt
rqt

# Or launch specific plugins
rqt_graph
rqt_console
```

### Command Line Debugging

#### Topic Inspection
```bash
# List topics
ros2 topic list

# Echo a topic
ros2 topic echo /topic_name std_msgs/msg/String

# Get topic info
ros2 topic info /topic_name

# Publish to a topic
ros2 topic pub /topic_name std_msgs/msg/String "data: 'hello'"
```

#### Service Debugging
```bash
# List services
ros2 service list

# Call a service
ros2 service call /service_name example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"

# Get service info
ros2 service info /service_name
```

#### Node Debugging
```bash
# List nodes
ros2 node list

# Get node info
ros2 node info /node_name

# Get node parameters
ros2 param list /node_name

# Set node parameter
ros2 param set /node_name param_name param_value
```

## Logging and Debugging

### ROS 2 Logging System

ROS 2 provides a hierarchical logging system:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')

        # Different log levels
        self.get_logger().debug('Debug message')
        self.get_logger().info('Info message')
        self.get_logger().warn('Warning message')
        self.get_logger().error('Error message')
        self.get_logger().fatal('Fatal message')
```

### Setting Log Levels

```bash
# Set log level for all nodes
export RCUTILS_LOGGING_SEVERITY_THRESHOLD=DEBUG

# Set log level for specific node
export RCUTILS_LOGGING_SEVERITY_THRESHOLD=INFO
ros2 run my_package my_node --ros-args --log-level DEBUG

# Set log level for specific logger
ros2 run my_package my_node --ros-args --log-level my_node:DEBUG
```

## Debugging Techniques

### 1. Print Debugging (Not Recommended for Production)

```python
# Python
def my_function(self, data):
    self.get_logger().info(f"Debug: received data = {data}")
    # Process data
    result = process_data(data)
    self.get_logger().info(f"Debug: result = {result}")
    return result
```

### 2. Using Breakpoints

```python
# Python with pdb
import pdb

def my_function(self, data):
    pdb.set_trace()  # Execution will pause here
    result = process_data(data)
    return result
```

### 3. Memory and Performance Debugging

```bash
# Monitor node resources
ros2 run topicos monitoring_node

# Check network usage
ros2 topic bw /topic_name

# Profile node performance
ros2 run tracetools tracetools
```

## Debugging Best Practices

1. **Use appropriate log levels**: Don't use info level for debug information
2. **Provide context**: Include node name, function, and relevant data in logs
3. **Avoid spam**: Don't log in tight loops without rate limiting
4. **Use structured logging**: Include relevant data in a parseable format
5. **Test error conditions**: Ensure error handling works as expected
6. **Document test cases**: Include expected behavior in test documentation

## Continuous Integration

Example GitHub Actions workflow for testing ROS 2 packages:

```yaml
name: ROS 2 CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ros_distribution: [humble]
    container:
      image: ros:${{ matrix.ros_distribution }}-ros-base
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          apt-get update
          rosdep update
          rosdep install --from-paths . --ignore-src -r -y
      - name: Build and test
        run: |
          source /opt/ros/${{ matrix.ros_distribution }}/setup.bash
          colcon build --packages-select my_package
          colcon test --packages-select my_package
          colcon test-result --all
```

## Summary

Testing and debugging are essential skills for developing reliable ROS 2 applications. Using the appropriate tools and techniques helps ensure your robotic systems function correctly and can be maintained over time. A comprehensive testing strategy includes unit tests, integration tests, and system-level tests.