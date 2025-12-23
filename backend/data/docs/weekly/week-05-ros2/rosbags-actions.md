---
sidebar_label: 'ROS Bags and Actions'
title: 'ROS Bags and Actions'
---

# ROS Bags and Actions in ROS 2

## Introduction to ROS Bags

ROS bags are a fundamental tool for recording and replaying ROS messages. They provide a way to save data from running ROS systems for later analysis, testing, and debugging.

## ROS Bags in ROS 2

ROS 2 uses a different bag format than ROS 1, with several improvements:

- **Database-based storage**: Uses SQLite for efficient storage and querying
- **Multiple compression formats**: Support for various compression algorithms
- **Better performance**: Improved read/write speeds
- **Enhanced metadata**: More detailed information about recorded data

## Recording Bags

### Command Line Recording

```bash
# Record all topics
ros2 bag record -a

# Record specific topics
ros2 bag record /topic1 /topic2 /topic3

# Record with compression
ros2 bag record -a --compression-mode file --compression-format zstd

# Record with size limits
ros2 bag record -a --max-bag-size 1073741824  # 1GB limit

# Record with time limits
ros2 bag record -a --max-duration 3600  # 1 hour limit

# Record to specific directory
ros2 bag record -a -o /path/to/bag/directory
```

### Programmatic Recording

```python
import rclpy
from rclpy.node import Node
from rosbag2_py import (
    SequentialWriter,
    StorageOptions,
    ConverterOptions,
    get_registered_compressors,
    get_registered_compressors_with_types
)

class BagRecorder(Node):
    def __init__(self):
        super().__init__('bag_recorder')

        # Configure storage options
        storage_options = StorageOptions(
            uri='my_bag',
            storage_id='sqlite3',
            max_bagfile_size=0,  # Unlimited
            max_bagfile_duration=0,  # Unlimited
            max_cache_size=0,
            storage_preset_profile='none',
            compression_mode=0,  # No compression
            compression_format='zstd'
        )

        # Configure converter options
        converter_options = ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr'
        )

        # Create writer
        self.writer = SequentialWriter()
        self.writer.open(storage_options, converter_options)

    def add_topic(self, topic_name, topic_type):
        """Add a topic to record."""
        from rosidl_runtime_py.utilities import get_message
        from rosbag2_py import TopicMetadata

        topic = TopicMetadata(
            name=topic_name,
            type=topic_type,
            serialization_format='cdr'
        )

        self.writer.create_topic(topic)

    def write_message(self, topic_name, message, timestamp):
        """Write a message to the bag."""
        self.writer.write(topic_name, message, timestamp)
```

## Playing Bags

### Command Line Playback

```bash
# Play a bag file
ros2 bag play my_bag

# Play specific topics
ros2 bag play my_bag --topics /topic1 /topic2

# Play with rate control
ros2 bag play my_bag --rate 0.5  # Half speed

# Play with delay
ros2 bag play my_bag --start-offset 10  # Start after 10 seconds

# Play looped
ros2 bag play my_bag --loop

# Play with remapping
ros2 bag play my_bag --remap /old_topic:=/new_topic
```

## Bag Information and Analysis

### Getting Bag Information

```bash
# Show bag info
ros2 bag info my_bag

# Show specific information
ros2 bag info my_bag --storage-config-file config.yaml
```

### Filtering Bags

```bash
# Copy and filter a bag
ros2 bag filter input_bag output_bag --topics /topic1 /topic2

# Filter with regex
ros2 bag filter input_bag output_bag --regex ".*camera.*"
```

## Actions in ROS 2

Actions provide a way to handle long-running tasks with feedback and the ability to cancel. They are ideal for tasks like navigation, manipulation, or any operation that takes a significant amount of time.

### Action Structure

An action consists of three message types:
- **Goal**: Request sent to the action server
- **Result**: Response sent back to the client
- **Feedback**: Intermediate updates during execution

### Creating Action Definitions

Create `action/Fibonacci.action`:

```
#goal definition
int32 order
---
#result definition
int32[] sequence
---
#feedback
int32[] sequence
```

### Action Server Implementation

```python
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            callback_group=rclpy.callback_groups.ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the goal."""
        self.get_logger().info('Executing goal...')

        # Feedback and result
        feedback_msg = Fibonacci.Feedback()
        result_msg = Fibonacci.Result()

        # Initialize Fibonacci sequence
        feedback_msg.sequence = [0, 1]
        sequence = [0, 1]

        # Calculate Fibonacci sequence up to goal.order
        for i in range(1, goal_handle.request.order):
            # Check if cancel was requested
            if goal_handle.is_cancel_requested:
                result_msg.sequence = sequence
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return result_msg

            # Update sequence
            sequence.append(sequence[i] + sequence[i-1])
            feedback_msg.sequence = sequence

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Publishing feedback: {sequence}')

            # Sleep to simulate work
            from time import sleep
            sleep(1)

        # Check if goal was canceled
        if goal_handle.is_cancel_requested:
            result_msg.sequence = sequence
            goal_handle.canceled()
            self.get_logger().info('Goal canceled')
            return result_msg

        # Set result
        result_msg.sequence = sequence

        # Succeed the goal
        goal_handle.succeed()
        self.get_logger().info('Returning result: %d' % len(result_msg.sequence))

        return result_msg

def main(args=None):
    rclpy.init(args=args)
    fibonacci_action_server = FibonacciActionServer()

    try:
        rclpy.spin(fibonacci_action_server)
    except KeyboardInterrupt:
        pass
    finally:
        fibonacci_action_server.destroy_node()
        rclpy.shutdown()
```

### Action Client Implementation

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci')

    def send_goal(self, order):
        """Send a goal to the action server."""
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

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
        self.get_logger().info(f'Received feedback: {feedback.sequence}')

    def get_result_callback(self, future):
        """Handle the result."""
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = FibonacciActionClient()

    # Send goal
    action_client.send_goal(10)

    try:
        rclpy.spin(action_client)
    except KeyboardInterrupt:
        pass
    finally:
        action_client.destroy_node()
        rclpy.shutdown()
```

## Advanced Bag Operations

### Bag Queries

```bash
# List available compression formats
ros2 bag compress --help

# Convert between compression formats
ros2 bag reindex my_bag

# Check bag integrity
ros2 bag validate my_bag
```

### Programmatic Bag Reading

```python
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import rosbag2_py

def read_bag(bag_path):
    """Read and process a bag file."""
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    # Get topic types
    topic_types = reader.get_all_topics_and_types()

    # Create deserializers for each topic
    deserializers = {}
    for topic_type in topic_types:
        deserializers[topic_type.name] = get_message(topic_type.type)

    # Read messages
    while reader.has_next():
        topic_name, data, timestamp = reader.read_next()
        msg_type = deserializers[topic_name]
        msg = deserialize_message(data, msg_type)

        print(f"Topic: {topic_name}, Time: {timestamp}, Message: {msg}")
```

## Best Practices

### Bag Best Practices

1. **Use appropriate compression**: Balance file size vs. CPU usage
2. **Set reasonable limits**: Use size or duration limits for long recordings
3. **Include metadata**: Add descriptions and context to your bags
4. **Organize systematically**: Use clear naming conventions
5. **Test playback**: Verify bags can be played back correctly

### Action Best Practices

1. **Use for long-running operations**: Actions are ideal for tasks that take time
2. **Provide feedback**: Update clients on progress when possible
3. **Handle cancellation**: Implement proper cancellation logic
4. **Set appropriate timeouts**: Prevent actions from running indefinitely
5. **Design clear interfaces**: Make goal/result/feedback messages intuitive

## Summary

ROS bags and actions are essential tools in ROS 2 development. Bags provide powerful recording and playback capabilities for data analysis and testing, while actions offer a robust mechanism for handling long-running tasks with feedback and cancellation. Understanding how to effectively use both is crucial for developing complex robotic applications.