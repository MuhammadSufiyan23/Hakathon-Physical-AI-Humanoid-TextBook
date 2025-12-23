---
sidebar_label: 'Packages and Workspaces'
title: 'Packages and Workspaces'
---

# Packages and Workspaces in ROS 2

## ROS 2 Packages

A package is the fundamental unit of software organization in ROS 2. It contains nodes, libraries, and other resources needed for a specific functionality. Packages provide modularity, reusability, and maintainability to ROS 2 projects.

### Package Structure

A typical ROS 2 package includes:

- **CMakeLists.txt**: Build instructions for C++ packages
- **package.xml**: Package metadata and dependencies
- **src/**: Source code files
- **include/**: Header files (for C++)
- **scripts/**: Standalone executable scripts
- **launch/**: Launch files for starting multiple nodes
- **config/**: Configuration files
- **test/**: Unit and integration tests

## ROS 2 Workspaces

A workspace is a directory that contains one or more packages. It provides a unified build and runtime environment for ROS 2 development.

### Workspace Structure

```
workspace_folder/
├── src/
│   ├── package_1/
│   ├── package_2/
│   └── ...
├── build/
├── install/
└── log/
```

## Creating and Building Packages

### Creating a Package

```bash
# Create a C++ package
ros2 pkg create --build-type ament_cmake my_robot_control

# Create a Python package
ros2 pkg create --build-type ament_python my_robot_control
```

### Package.xml Example

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_control</name>
  <version>0.0.0</version>
  <description>Example robot control package</description>
  <maintainer email="user@example.com">User Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
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

## Build Systems in ROS 2

ROS 2 supports multiple build systems:

- **ament_cmake**: For C++ packages using CMake
- **ament_python**: For Python packages
- **ament_make**: Legacy build system (not recommended)
- **colcon**: The unified build tool for ROS 2

## Using colcon for Building

### Basic Build Commands

```bash
# Build all packages in the workspace
colcon build

# Build specific packages
colcon build --packages-select my_robot_control

# Build with specific arguments (e.g., for CMake)
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Build and run tests
colcon build --packages-select my_robot_control
colcon test --packages-select my_robot_control
```

## Python Package Example

```python
# setup.py
from setuptools import setup

package_name = 'my_robot_control'

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
    description='Example robot control package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_controller = my_robot_control.robot_controller:main',
        ],
    },
)
```

## Managing Dependencies

### Adding Dependencies

```xml
<!-- In package.xml -->
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>my_custom_msgs</depend>
```

```cmake
# In CMakeLists.txt
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(my_custom_msgs REQUIRED)
```

## Best Practices

1. **Single Responsibility**: Each package should have a clear, focused purpose
2. **Dependency Management**: Only depend on packages that are actually needed
3. **Proper Naming**: Use descriptive, consistent names
4. **Documentation**: Include README files and proper comments
5. **Testing**: Include unit tests for all functionality
6. **Version Control**: Use git for source control

## Summary

Understanding packages and workspaces is essential for effective ROS 2 development. Proper organization of code into well-structured packages enables modularity, reusability, and maintainability of robotic applications.