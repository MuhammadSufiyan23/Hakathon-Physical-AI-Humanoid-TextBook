---
sidebar_label: 'Week 4 Quiz: ROS 2 Development'
title: 'Week 4 Quiz: ROS 2 Development'
---

# Week 4 Quiz: ROS 2 Development

## Question 1
Which client library is used for Python ROS 2 development?
- A) rclcpp
- B) rclpy
- C) rcljava
- D) rclc

## Question 2
What does the LaunchDescription class contain in a Python launch file?
- A) Node parameters only
- B) All launch actions
- C) Service definitions
- D) Message definitions

## Question 3
Which testing framework is commonly used for C++ ROS 2 unit tests?
- A) pytest
- B) unittest
- C) Google Test
- D) nose2

## Question 4
How do you declare a launch argument in a Python launch file?
- A) launch_argument()
- B) arg_declare()
- C) DeclareLaunchArgument()
- D) launch_declare()

## Question 5
Which command is used to run tests for a specific ROS 2 package?
- A) ros2 test package_name
- B) colcon test --packages-select package_name
- C) ros2 run test package_name
- D) test package_name

## Question 6
What is the purpose of remappings in ROS 2 launch files?
- A) To change node names
- B) To redirect topic/service names
- C) To set parameters
- D) To define node dependencies

## Question 7
Which ROS 2 logging level should be used for detailed debugging information?
- A) INFO
- B) WARN
- C) DEBUG
- D) ERROR

## Question 8
How can you set a specific log level for a ROS 2 node at runtime?
- A) Using ROS_LOG_LEVEL environment variable
- B) With the --ros-args --log-level flag
- C) Through a parameter file
- D) By modifying the source code

## Question 9
Which tool can be used to visualize the ROS 2 node graph?
- A) rqt_console
- B) rqt_plot
- C) rqt_graph
- D) rqt_topic

## Question 10
What is the correct syntax for calling a service from the command line?
- A) ros2 service call /service_name `"{param: value}"`
- B) ros2 call /service_name service_type `"{param: value}"`
- C) ros2 service call /service_name service_type `"{param: value}"`
- D) ros2 run service /service_name service_type

## Answer Key
1. B) rclpy
2. B) All launch actions
3. C) Google Test
4. C) DeclareLaunchArgument()
5. B) colcon test --packages-select package_name
6. B) To redirect topic/service names
7. C) DEBUG
8. B) With the --ros-args --log-level flag
9. C) rqt_graph
10. C) ros2 service call /service_name service_type `"{param: value}"`