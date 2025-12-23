---
sidebar_label: 'World Modeling and Environment Design'
title: 'World Modeling and Environment Design'
---

# World Modeling and Environment Design in Gazebo

## Introduction to World Modeling

World modeling in Gazebo involves creating realistic 3D environments where robots can operate. A well-designed world includes appropriate physics properties, visual elements, and environmental conditions that match the intended application.

## SDF (Simulation Description Format) Structure

SDF is the XML-based format used to describe worlds, models, and objects in Gazebo. Understanding its structure is crucial for world modeling.

### Basic SDF World Template

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="my_environment">
    <!-- World properties -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Physics engine -->
    <physics name="default_physics" default="0" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
    </physics>

    <!-- Environment elements -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>
  </world>
</sdf>
```

## Creating Custom Environments

### Indoor Environments

For indoor scenarios like warehouses or homes:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="indoor_warehouse">
    <light name="ceiling_light" type="point">
      <pose>0 0 3 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.5 0.5 0.5 1</specular>
      <attenuation>
        <range>10</range>
        <constant>0.9</constant>
        <linear>0.045</linear>
        <quadratic>0.0075</quadratic>
      </attenuation>
    </light>

    <!-- Indoor environment -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Walls -->
    <model name="wall_1">
      <pose>0 5 1 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box><size>10 0.2 2</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box><size>10 0.2 2</size></box>
          </geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>

    <!-- Furniture and obstacles -->
    <model name="table">
      <pose>2 0 0 0 0 0</pose>
      <link name="table_top">
        <visual name="visual">
          <geometry>
            <box><size>1.5 0.8 0.02</size></box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box><size>1.5 0.8 0.02</size></box>
          </geometry>
        </collision>
        <inertial>
          <mass>10</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
      <link name="leg_1">
        <pose>0.65 0.3 -0.39 0 0 0</pose>
        <visual name="visual">
          <geometry>
            <cylinder><radius>0.02</radius><length>0.8</length></cylinder>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <cylinder><radius>0.02</radius><length>0.8</length></cylinder>
          </geometry>
        </collision>
        <inertial>
          <mass>1</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

### Outdoor Environments

For outdoor scenarios like city streets or natural environments:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="outdoor_city">
    <!-- Sky and atmosphere -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>true</shadows>
    </scene>

    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Terrain with elevation -->
    <model name="terrain">
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <heightmap>
              <uri>file://path/to/heightmap.png</uri>
              <size>100 100 20</size>
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </visual>
        <collision name="collision">
          <geometry>
            <heightmap>
              <uri>file://path/to/heightmap.png</uri>
              <size>100 100 20</size>
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </collision>
      </link>
    </model>

    <!-- Buildings -->
    <model name="building_1">
      <pose>-10 0 0 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box><size>5 5 8</size></box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box><size>5 5 8</size></box>
          </geometry>
        </collision>
        <inertial>
          <mass>1000</mass>
          <inertia><ixx>1</ixx><iyy>1</iyy><izz>1</izz></inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

## Physics Properties and Materials

### Friction and Contact Properties

```xml
<link name="wheel_link">
  <collision name="collision">
    <geometry>
      <cylinder><radius>0.1</radius><length>0.05</length></cylinder>
    </geometry>
    <surface>
      <friction>
        <ode>
          <mu>1.0</mu>  <!-- Coefficient of friction -->
          <mu2>1.0</mu2>
          <fdir1>0 0 1</fdir1>  <!-- Friction direction -->
          <slip1>0.0</slip1>    <!-- Slip in primary direction -->
          <slip2>0.0</slip2>    <!-- Slip in secondary direction -->
        </ode>
      </friction>
      <bounce>
        <restitution_coefficient>0.1</restitution_coefficient>
        <threshold>100000</threshold>
      </bounce>
      <contact>
        <ode>
          <soft_cfm>0</soft_cfm>
          <soft_erp>0.2</soft_erp>
          <kp>1e+13</kp>
          <kd>1</kd>
          <max_vel>0.01</max_vel>
          <min_depth>0</min_depth>
        </ode>
      </contact>
    </surface>
  </collision>
</link>
```

### Material Definitions

```xml
<model name="colored_object">
  <link name="link">
    <visual name="visual">
      <geometry>
        <box><size>1 1 1</size></box>
      </geometry>
      <material>
        <ambient>0.1 0.1 0.1 1</ambient>
        <diffuse>0.7 0.7 0.0 1</diffuse>
        <specular>0.01 0.01 0.01 1</specular>
        <emissive>0 0 0 1</emissive>
        <shader type="vertex">
          <normal_map>none</normal_map>
        </shader>
      </material>
    </visual>
  </link>
</model>
```

## Creating Complex Models

### Multi-Link Models

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <model name="articulated_robot">
    <link name="base_link">
      <pose>0 0 0.5 0 0 0</pose>
      <inertial>
        <mass>5.0</mass>
        <inertia><ixx>0.4</ixx><iyy>0.4</iyy><izz>0.4</izz></inertia>
      </inertial>
      <visual name="visual">
        <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      </visual>
      <collision name="collision">
        <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      </collision>
    </link>

    <link name="arm_link">
      <pose>0.3 0 0.5 0 0 0</pose>
      <inertial>
        <mass>1.0</mass>
        <inertia><ixx>0.1</ixx><iyy>0.1</iyy><izz>0.1</izz></inertia>
      </inertial>
      <visual name="visual">
        <geometry><cylinder><radius>0.05</radius><length>0.5</length></cylinder></geometry>
      </visual>
      <collision name="collision">
        <geometry><cylinder><radius>0.05</radius><length>0.5</length></cylinder></geometry>
      </collision>
    </link>

    <joint name="arm_joint" type="revolute">
      <parent>base_link</parent>
      <child>arm_link</child>
      <axis>
        <xyz>0 0 1</xyz>
        <limit><lower>-1.57</lower><upper>1.57</upper></limit>
      </axis>
    </joint>
  </model>
</sdf>
```

## Environment Customization

### Lighting Effects

```xml
<world name="custom_lighting">
  <!-- Multiple light sources -->
  <light name="main_light" type="directional">
    <pose>0 0 10 0 0 0</pose>
    <diffuse>0.8 0.8 0.8 1</diffuse>
    <specular>0.2 0.2 0.2 1</specular>
    <direction>-0.5 0.1 -0.9</direction>
  </light>

  <light name="spotlight" type="spot">
    <pose>5 5 5 0 0 0</pose>
    <diffuse>1 0.8 0.2 1</diffuse>
    <specular>1 1 1 1</specular>
    <attenuation>
      <range>10</range>
      <constant>0.9</constant>
      <linear>0.045</linear>
      <quadratic>0.0075</quadratic>
    </attenuation>
    <direction>-0.5 -0.5 -1</direction>
    <spot>
      <inner_angle>0.1</inner_angle>
      <outer_angle>0.5</outer_angle>
      <falloff>1</falloff>
    </spot>
  </light>
</world>
```

### Weather and Atmospheric Effects

```xml
<world name="weather_world">
  <scene>
    <ambient>0.3 0.3 0.3 1</ambient>
    <background>0.5 0.6 0.8 1</background>
    <shadows>true</shadows>
  </scene>

  <physics name="default_physics" default="0" type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1</real_time_factor>
    <real_time_update_rate>1000.0</real_time_update_rate>
  </physics>

  <!-- Wind effects -->
  <wind>
    <linear_velocity>0.5 0 0</linear_velocity>
  </wind>
</world>
```

## Using Model Database

### Including Standard Models

```xml
<world name="with_standard_models">
  <!-- Include from Gazebo model database -->
  <include>
    <uri>model://ground_plane</uri>
  </include>

  <include>
    <uri>model://sun</uri>
  </include>

  <include>
    <uri>model://cylinder</uri>
    <pose>2 0 1 0 0 0</pose>
  </include>

  <include>
    <uri>model://unit_box</uri>
    <pose>-2 0 0.5 0 0 0</pose>
  </include>

  <!-- Custom model -->
  <include>
    <uri>model://my_robot</uri>
    <pose>0 0 0.5 0 0 0</pose>
  </include>
</world>
```

## World Optimization

### Performance Considerations

1. **Collision geometry**: Use simplified collision meshes
2. **Visual geometry**: Use detailed meshes only when necessary
3. **Physics parameters**: Adjust step size and update rates appropriately
4. **Model complexity**: Balance detail with performance requirements

### Example Optimized World

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="optimized_world">
    <!-- Optimized physics -->
    <physics name="fast_physics" type="ode">
      <max_step_size>0.01</max_step_size>  <!-- Larger step size for performance -->
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>100.0</real_time_update_rate>
      <ode>
        <solver>
          <type>quick</type>  <!-- Fast solver -->
          <iters>10</iters>    <!-- Fewer iterations -->
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0.000001</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>

    <!-- Simplified ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Optimized models with simple collision -->
    <model name="simple_box">
      <pose>0 0 0.5 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>1 1 1</size></box></geometry>
        </visual>
        <!-- Simple collision geometry -->
        <collision name="collision">
          <geometry><box><size>1 1 1</size></box></geometry>
        </collision>
        <inertial>
          <mass>1.0</mass>
          <inertia><ixx>0.1667</ixx><iyy>0.1667</iyy><izz>0.1667</izz></inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

## Best Practices

1. **Start simple**: Begin with basic models and add complexity gradually
2. **Use standard models**: Leverage existing models from the database when possible
3. **Test performance**: Monitor simulation performance and adjust as needed
4. **Version control**: Keep world files under version control
5. **Documentation**: Document the purpose and configuration of each world
6. **Modularity**: Create reusable components for common elements

## Summary

World modeling in Gazebo is a critical skill for robotics simulation. Creating realistic and well-performing environments requires understanding SDF structure, physics properties, and optimization techniques. Well-designed worlds enable effective testing and validation of robotic systems before deployment on real hardware.