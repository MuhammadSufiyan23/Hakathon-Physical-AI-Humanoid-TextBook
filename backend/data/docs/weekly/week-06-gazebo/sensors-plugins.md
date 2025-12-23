---
sidebar_label: 'Sensors and Plugins in Gazebo'
title: 'Sensors and Plugins in Gazebo'
---

# Sensors and Plugins in Gazebo

## Introduction to Gazebo Sensors

Gazebo provides a rich set of simulated sensors that closely mimic real-world sensors. These sensors generate realistic data that can be used for robot perception, navigation, and control algorithms development.

## Types of Sensors in Gazebo

### Camera Sensors

Camera sensors simulate RGB cameras and can generate realistic images with proper distortion, noise, and lighting effects.

#### Basic Camera Sensor Configuration

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.3962634</horizontal_fov>  <!-- 80 degrees -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.007</stddev>
      </noise>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>image_raw:=camera/image_raw</remapping>
        <remapping>camera_info:=camera/camera_info</remapping>
      </ros>
      <camera_name>camera</camera_name>
      <image_topic_name>image_raw</image_topic_name>
      <camera_info_topic_name>camera_info</camera_info_topic_name>
      <frame_name>camera_link</frame_name>
      <hack_baseline>0.07</hack_baseline>
      <distortion_k1>0.0</distortion_k1>
      <distortion_k2>0.0</distortion_k2>
      <distortion_k3>0.0</distortion_k3>
      <distortion_t1>0.0</distortion_t1>
      <distortion_t2>0.0</distortion_t2>
    </plugin>
  </sensor>
</gazebo>
```

### LIDAR Sensors

LIDAR sensors simulate laser range finders and provide 2D or 3D point cloud data.

#### 2D LIDAR Configuration

```xml
<gazebo reference="lidar_link">
  <sensor name="lidar_2d" type="ray">
    <always_on>true</always_on>
    <update_rate>40</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-1.570796</min_angle>  <!-- -90 degrees -->
          <max_angle>1.570796</max_angle>    <!-- 90 degrees -->
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_laser.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>scan:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
      <min_range>0.1</min_range>
      <max_range>30.0</max_range>
      <gaussian_noise>0.01</gaussian_noise>
    </plugin>
  </sensor>
</gazebo>
```

#### 3D LIDAR Configuration (Velodyne-style)

```xml
<gazebo reference="velodyne_link">
  <sensor name="velodyne" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>800</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159265359</min_angle>  <!-- -180 degrees -->
          <max_angle>3.14159265359</max_angle>    <!-- 180 degrees -->
        </horizontal>
        <vertical>
          <samples>32</samples>
          <resolution>1</resolution>
          <min_angle>-0.523599</min_angle>  <!-- -30 degrees -->
          <max_angle>0.261799</max_angle>   <!-- 15 degrees -->
        </vertical>
      </scan>
      <range>
        <min>0.1</min>
        <max>100.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="velodyne_controller" filename="libgazebo_ros_velodyne_laser.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>points:=velodyne_points</remapping>
      </ros>
      <topic_name>velodyne_points</topic_name>
      <frame_name>velodyne_link</frame_name>
      <min_range>0.1</min_range>
      <max_range>100.0</max_range>
      <gaussian_noise>0.01</gaussian_noise>
    </plugin>
  </sensor>
</gazebo>
```

### IMU Sensors

IMU sensors provide acceleration, angular velocity, and orientation data.

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </noise>
        </z>
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
    <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>imu:=imu</remapping>
      </ros>
      <topic_name>imu</topic_name>
      <body_name>imu_link</body_name>
      <frame_name>imu_link</frame_name>
      <update_rate>100</update_rate>
      <gaussian_noise>0.01</gaussian_noise>
    </plugin>
  </sensor>
</gazebo>
```

### GPS Sensors

GPS sensors provide location data with realistic accuracy and noise.

```xml
<gazebo reference="gps_link">
  <sensor name="gps_sensor" type="gps">
    <always_on>true</always_on>
    <update_rate>4</update_rate>
    <plugin name="gps_plugin" filename="libgazebo_ros_gps.so">
      <ros>
        <namespace>robot</namespace>
        <remapping>fix:=gps/fix</remapping>
      </ros>
      <topic_name>fix</topic_name>
      <frame_name>gps_link</frame_name>
      <update_rate>4</update_rate>
      <gaussian_noise>0.1</gaussian_noise>
    </plugin>
  </sensor>
</gazebo>
```

## Gazebo Plugins

### Control Plugins

#### Differential Drive Plugin

```xml
<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <ros>
      <namespace>robot</namespace>
      <remapping>cmd_vel:=cmd_vel</remapping>
      <remapping>odom:=odom</remapping>
      <remapping>joint_states:=joint_states</remapping>
    </ros>
    <update_rate>30</update_rate>
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.3</wheel_separation>
    <wheel_diameter>0.2</wheel_diameter>
    <max_wheel_torque>20</max_wheel_torque>
    <max_wheel_acceleration>1.0</max_wheel_acceleration>
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_link</robot_base_frame>
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>true</publish_wheel_tf>
  </plugin>
</gazebo>
```

#### Joint State Publisher Plugin

```xml
<gazebo>
  <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
    <ros>
      <namespace>robot</namespace>
      <remapping>joint_states:=joint_states</remapping>
    </ros>
    <update_rate>30</update_rate>
    <joint_name>left_wheel_joint</joint_name>
    <joint_name>right_wheel_joint</joint_name>
    <joint_name>arm_joint</joint_name>
  </plugin>
</gazebo>
```

#### Joint Position Controller Plugin

```xml
<gazebo>
  <plugin name="arm_controller" filename="libgazebo_ros_joint_position.so">
    <ros>
      <namespace>robot</namespace>
      <remapping>position_cmd:=arm_position</remapping>
    </ros>
    <joint_name>arm_joint</joint_name>
    <topic>arm_position</topic>
    <update_rate>100</update_rate>
    <gaussian_noise>0.01</gaussian_noise>
  </plugin>
</gazebo>
```

### ros2_control Integration

For modern ROS 2 control systems, you can integrate with ros2_control:

```xml
<!-- In URDF -->
<ros2_control name="GazeboSystem" type="system">
  <hardware>
    <plugin>gazebo_ros2_control/GazeboSystem</plugin>
  </hardware>
  <joint name="left_wheel_joint">
    <command_interface name="velocity">
      <param name="min">-10</param>
      <param name="max">10</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
  <joint name="right_wheel_joint">
    <command_interface name="velocity">
      <param name="min">-10</param>
      <param name="max">10</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
</ros2_control>

<!-- Gazebo plugin -->
<gazebo>
  <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
    <parameters>$(find my_robot_description)/config/robot_control.yaml</parameters>
  </plugin>
</gazebo>
```

## Custom Plugins

### Creating a Custom Plugin

Example of a simple custom plugin:

```cpp
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>

namespace gazebo
{
  class CustomPlugin : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      // Store the pointer to the model
      this->model = _parent;

      // Listen to the update event. This event is broadcast every
      // simulation iteration.
      this->updateConnection = event::Events::ConnectWorldUpdateBegin(
          std::bind(&CustomPlugin::OnUpdate, this));
    }

    // Called by the world update start event
    public: void OnUpdate()
    {
      // Apply a small linear velocity to the model
      this->model->SetLinearVel(math::Vector3(0.01, 0, 0));
    }

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(CustomPlugin)
}
```

### Plugin Configuration in URDF

```xml
<gazebo>
  <plugin name="custom_plugin" filename="libCustomPlugin.so">
    <ros>
      <namespace>robot</namespace>
    </ros>
    <param1>value1</param1>
    <param2>value2</param2>
  </plugin>
</gazebo>
```

## Sensor and Plugin Best Practices

### Performance Optimization

1. **Update rates**: Set appropriate update rates for each sensor
2. **Resolution**: Balance sensor resolution with performance requirements
3. **Noise**: Add realistic noise to make simulation more robust
4. **Filtering**: Use appropriate filtering for sensor data

### Configuration Guidelines

1. **Realistic parameters**: Use parameters that match real sensors
2. **Topic names**: Use consistent and descriptive topic names
3. **Frame IDs**: Use proper coordinate frame IDs
4. **Namespace**: Organize topics under appropriate namespaces

### Example: Complete Sensor Configuration

```xml
<?xml version="1.0"?>
<robot name="sensor_robot">
  <!-- Robot links and joints -->
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
    <visual>
      <geometry><box size="0.5 0.3 0.2"/></geometry>
    </visual>
    <collision>
      <geometry><box size="0.5 0.3 0.2"/></geometry>
    </collision>
  </link>

  <!-- Camera link -->
  <link name="camera_link">
    <inertial>
      <mass value="0.01"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
    <visual>
      <geometry><box size="0.05 0.05 0.05"/></geometry>
    </visual>
    <collision>
      <geometry><box size="0.05 0.05 0.05"/></geometry>
    </collision>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
  </joint>

  <!-- IMU link -->
  <link name="imu_link">
    <inertial>
      <mass value="0.01"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="imu_joint" type="fixed">
    <parent link="base_link"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
  </joint>

  <!-- LIDAR link -->
  <link name="lidar_link">
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
    <visual>
      <geometry><cylinder radius="0.03" length="0.03"/></geometry>
    </visual>
    <collision>
      <geometry><cylinder radius="0.03" length="0.03"/></geometry>
    </collision>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0.15 0 0.15" rpy="0 0 0"/>
  </joint>

  <!-- Gazebo sensor and plugin configurations -->
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
        <image><width>640</width><height>480</height><format>R8G8B8</format></image>
        <clip><near>0.1</near><far>100</far></clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros><namespace>robot</namespace></ros>
        <camera_name>camera</camera_name>
        <frame_name>camera_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo reference="imu_link">
    <sensor name="imu_sensor" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
        <ros><namespace>robot</namespace></ros>
        <topic_name>imu</topic_name>
        <frame_name>imu_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo reference="lidar_link">
    <sensor name="lidar" type="ray">
      <always_on>true</always_on>
      <update_rate>40</update_rate>
      <ray>
        <scan><horizontal><samples>360</samples><min_angle>-3.14159</min_angle><max_angle>3.14159</max_angle></horizontal></scan>
        <range><min>0.1</min><max>30.0</max></range>
      </ray>
      <plugin name="lidar_controller" filename="libgazebo_ros_laser.so">
        <ros><namespace>robot</namespace></ros>
        <frame_name>lidar_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <!-- Differential drive plugin -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros><namespace>robot</namespace></ros>
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>0.3</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
```

## Troubleshooting Common Issues

### Sensor Not Publishing Data
- Check that the sensor is properly configured with `always_on` and `update_rate`
- Verify plugin filename and parameters
- Check ROS topic remappings

### Performance Issues
- Reduce sensor update rates
- Lower image resolution for camera sensors
- Simplify sensor parameters where possible

### Coordinate Frame Issues
- Ensure proper frame names in plugins
- Check joint transforms between links
- Verify sensor link placement

## Summary

Gazebo sensors and plugins provide realistic simulation of real-world hardware. Proper configuration of these elements is crucial for effective robot development and testing. Understanding the different sensor types, their parameters, and plugin configurations enables the creation of realistic simulation environments that closely match real-world conditions.