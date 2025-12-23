---
sidebar_label: 'Nodes, Topics, and Services'
title: 'Nodes, Topics, and Services'
---

# Nodes, Topics, and Services in ROS 2

## Understanding Nodes

A node is a process that performs computation in ROS 2. Nodes are the fundamental building blocks of a ROS 2 system and can be written in multiple languages (Python, C++, etc.). Each node can publish or subscribe to topics, provide or use services, and interact with other nodes.

## Topics and Publishers/Subscribers

Topics provide a unidirectional communication mechanism where publishers send data and subscribers receive it. This publish-subscribe pattern allows for loose coupling between nodes.

### Key Characteristics of Topics:
- Unidirectional data flow
- Multiple publishers and subscribers allowed
- Asynchronous communication
- Data is distributed to all subscribers simultaneously

## Services

Services provide bidirectional communication where a client sends a request and receives a response from a server. This request-response pattern is useful for operations that require a specific response.

## Quality of Service (QoS) in ROS 2

ROS 2 introduces Quality of Service policies that allow fine-tuning of communication behavior:

- **Reliability**: Best effort or reliable delivery
- **Durability**: Volatile or transient local
- **History**: Keep last or keep all
- **Deadline**: Maximum time between messages
- **Liveliness**: How to detect if a publisher is alive

## Python Example: Creating a Simple Publisher and Subscriber

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

    minimal_publisher = MinimalPublisher()
    minimal_subscriber = MinimalSubscriber()

    rclpy.spin_once(minimal_publisher)
    rclpy.spin_once(minimal_subscriber)

    minimal_publisher.destroy_node()
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## C++ Example: Creating a Simple Service Server and Client

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class MinimalService : public rclcpp::Node
{
public:
    MinimalService()
    : Node("minimal_service")
    {
        service_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "add_two_ints",
            [this](const std::shared_ptr<rmw_request_id_t> request_header,
                   const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
                   std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response) {
                (void)request_header;
                response->sum = request->a + request->b;
                RCLCPP_INFO(rclcpp::get_logger("rclcpp"),
                            "Incoming request\na: %ld, b: %ld",
                            request->a, request->b);
                RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Sending back response: [%ld]", response->sum);
            });
    }

private:
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MinimalService>());
    rclcpp::shutdown();
    return 0;
}
```

## Summary

Understanding nodes, topics, and services is fundamental to ROS 2 development. These communication patterns form the basis of how robotic systems interact and coordinate their behavior.