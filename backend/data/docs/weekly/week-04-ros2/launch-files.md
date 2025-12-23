---
sidebar_label: 'Launch Files and System Management'
title: 'Launch Files and System Management'
---

# Launch Files and System Management in ROS 2

## Introduction to Launch Files

Launch files in ROS 2 allow you to start multiple nodes with a single command, configure parameters, and manage complex robotic systems. They provide a declarative way to define how your system should be launched and configured.

## Launch System Architecture

ROS 2 uses the `launch` system which is based on a directed acyclic graph (DAG) of actions. The launch system is language-agnostic and provides:

- Cross-platform compatibility
- Composable launch files
- Parameter configuration
- Node management
- Event handling

## Python Launch Files

Python launch files are the most common and flexible approach for defining system launches in ROS 2.

### Basic Launch File Structure

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker',
            parameters=[
                {'param_name': 'param_value'}
            ],
            remappings=[
                ('original_topic', 'new_topic')
            ]
        ),
        Node(
            package='demo_nodes_cpp',
            executable='listener',
            name='listener',
        ),
    ])
```

## Launch File Components

### 1. LaunchDescription
The root element that contains all launch actions.

### 2. Actions
Actions are the building blocks of launch files:
- `Node`: Launches a ROS node
- `ExecuteProcess`: Runs a non-ROS process
- `RegisterEventHandler`: Registers event handlers
- `LogInfo`: Logs information during launch
- `TimerAction`: Delays actions

### 3. Conditions
Launch files support conditional execution:

```python
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker',
            condition=IfCondition(use_sim_time)
        ),
    ])
```

## Advanced Launch Features

### Parameters in Launch Files

```python
Node(
    package='my_package',
    executable='my_node',
    name='my_node',
    parameters=[
        {'param1': 'value1'},
        {'param2': 42},
        {'param3': True},
        # Load from YAML file
        '/path/to/params.yaml',
    ]
)
```

### Remappings

```python
Node(
    package='my_package',
    executable='my_node',
    name='my_node',
    remappings=[
        ('original_topic', 'new_topic'),
        ('original_service', 'new_service'),
    ]
)
```

### Command Line Arguments

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'node_frequency',
            default_value='10.0',
            description='Frequency of the node'
        ),
        Node(
            package='my_package',
            executable='my_node',
            name='my_node',
            parameters=[
                {'frequency': LaunchConfiguration('node_frequency')}
            ]
        ),
    ])
```

## Complex Launch Example

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    log_level = LaunchConfiguration('log_level')

    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time if true'
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Log level'
        ),

        # Launch nodes
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'robot_description': open('/path/to/robot.urdf').read()}
            ],
            arguments=['--ros-args', '--log-level', log_level]
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[
                {'use_sim_time': use_sim_time}
            ]
        ),

        # Launch gazebo if needed
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ) if LaunchConfiguration('use_gazebo') else None,
    ])
```

## YAML Launch Files

ROS 2 also supports YAML-based launch files for simpler configurations:

```yaml
launch:
  - node:
      pkg: "demo_nodes_cpp"
      exec: "talker"
      name: "talker_node"
      parameters:
        - {param1: "value1", param2: 42}
      remappings:
        - ["original_topic", "new_topic"]
  - node:
      pkg: "demo_nodes_cpp"
      exec: "listener"
      name: "listener_node"
```

## Launch File Best Practices

1. **Modularity**: Create reusable launch files that can be composed
2. **Parameterization**: Use launch arguments for configurable options
3. **Documentation**: Include descriptions for all launch arguments
4. **Error Handling**: Use conditions to handle optional components
5. **Organization**: Group related nodes in logical launch files
6. **Testing**: Test launch files with different parameter combinations

## Composable Launch Files

Launch files can include other launch files to create complex systems:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('my_robot_description'),
                    'launch',
                    'robot_description.launch.py'
                ])
            ])
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('my_robot_control'),
                    'launch',
                    'robot_control.launch.py'
                ])
            ])
        ),
    ])
```

## Running Launch Files

To run a launch file:

```bash
# Basic launch
ros2 launch my_package my_launch_file.py

# With arguments
ros2 launch my_package my_launch_file.py use_sim_time:=true log_level:=debug

# List available launch arguments
ros2 launch my_package my_launch_file.py --show-args
```

## Summary

Launch files are essential for managing complex ROS 2 systems. They provide a clean, organized way to start multiple nodes with appropriate configurations, parameters, and remappings. Understanding launch files is crucial for deploying real-world robotic applications.