---
sidebar_label: 'Client Libraries and APIs'
title: 'Client Libraries and APIs'
---

# Client Libraries and APIs in ROS 2

## Overview of Client Libraries

ROS 2 provides client libraries that allow developers to write ROS 2 programs in multiple programming languages. The most commonly used client libraries are:

- **rclcpp**: C++ client library
- **rclpy**: Python client library
- **rcl**: C client library (lower-level)
- **rclc**: C client library (higher-level wrapper)
- **rclnodejs**: Node.js client library
- **rcljava**: Java client library
- **rclrust**: Rust client library

## rclpy: Python Client Library

The Python client library (rclpy) provides a Python interface to ROS 2 functionality. It allows developers to create nodes, publishers, subscribers, services, and clients using Python.

### Basic Node Structure in Python

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')
        # Initialize node components here
        self.get_logger().info('Node initialized')

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## rclcpp: C++ Client Library

The C++ client library (rclcpp) provides a C++ interface to ROS 2 functionality with features like:

- Modern C++14/17/20 syntax
- Smart pointers for memory management
- Lambda functions for callbacks
- Template-based message handling

### Basic Node Structure in C++

```cpp
#include "rclcpp/rclcpp.hpp"

class MyNode : public rclcpp::Node
{
public:
    MyNode() : Node("my_node_name")
    {
        RCLCPP_INFO(this->get_logger(), "Node initialized");
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MyNode>());
    rclcpp::shutdown();
    return 0;
}
```

## Creating Publishers and Subscribers

### Python Example

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
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

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')
```

### C++ Example

```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Talker : public rclcpp::Node
{
public:
    Talker() : Node("talker")
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&Talker::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello World " + std::to_string(count_++);
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t count_ = 0;
};

class Listener : public rclcpp::Node
{
public:
    Listener() : Node("listener")
    {
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "topic", 10,
            [this](const std_msgs::msg::String::SharedPtr msg) {
                RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
            });
    }

private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};
```

## Services and Clients

### Python Service Example

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {response.sum}')
        return response

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a, b):
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        self.future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
```

## Parameters

ROS 2 allows nodes to have configurable parameters that can be set at runtime:

### Python Parameter Example

```python
import rclpy
from rclpy.node import Node

class ParamNode(Node):
    def __init__(self):
        super().__init__('param_node')

        # Declare parameters with default values
        self.declare_parameter('my_parameter', 'default_value')
        self.declare_parameter('number_param', 42)

        # Get parameter values
        param_value = self.get_parameter('my_parameter').value
        number_value = self.get_parameter('number_param').value

        self.get_logger().info(f'Parameter value: {param_value}')
        self.get_logger().info(f'Number value: {number_value}')
```

## Best Practices

1. **Use proper error handling**: Always handle exceptions and shutdown procedures
2. **Follow naming conventions**: Use snake_case for Python, camelCase for C++
3. **Memory management**: In C++, use smart pointers and RAII principles
4. **Logging**: Use appropriate log levels (debug, info, warn, error)
5. **Resource cleanup**: Always destroy nodes and clean up resources
6. **Thread safety**: Be aware of thread safety in callbacks

## Summary

Client libraries provide the interface between your application code and the ROS 2 middleware. Understanding how to use these libraries effectively is crucial for developing robust ROS 2 applications in your preferred programming language.