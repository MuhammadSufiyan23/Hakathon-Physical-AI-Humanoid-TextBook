---
sidebar_label: 'Manipulation and Grasping in Isaac'
title: 'Manipulation and Grasping in Isaac'
---

# Manipulation and Grasping in Isaac

## Introduction to Isaac Manipulation

Isaac manipulation provides a comprehensive framework for robotic manipulation tasks, including grasping, pick-and-place operations, and complex manipulation planning. The platform leverages NVIDIA's GPU computing capabilities to enable real-time manipulation planning and execution with visual feedback.

## Isaac Manipulation Architecture

### Manipulation Stack Components

The Isaac manipulation stack consists of several interconnected components:

```
Application Layer
├── Isaac Manipulation Apps
├── Custom Manipulation Logic
└── Task Planning

Manipulation Core
├── Inverse Kinematics
├── Motion Planning
├── Grasp Planning
├── Trajectory Generation
└── Control Interface

Perception Integration
├── Object Detection
├── Pose Estimation
├── 3D Reconstruction
└── Scene Understanding

Hardware Interface
├── Arm Controllers
├── Gripper Controllers
├── Sensor Drivers
└── Communication Modules
```

### Key Manipulation Features

1. **Grasp Planning**: Compute optimal grasp poses for objects
2. **Motion Planning**: Plan collision-free trajectories
3. **Inverse Kinematics**: Solve for joint angles to reach desired poses
4. **Force Control**: Apply appropriate forces during manipulation
5. **Visual Servoing**: Use vision feedback for precise positioning

## Inverse Kinematics in Isaac

### Analytical and Numerical IK Solutions

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import Header
import numpy as np
import math
from scipy.spatial.transform import Rotation as R

class IsaacInverseKinematics(Node):
    def __init__(self):
        super().__init__('isaac_inverse_kinematics')

        # Robot parameters (example for 6-DOF arm)
        self.dh_params = [
            {'a': 0.0, 'alpha': -np.pi/2, 'd': 0.333, 'theta': 0.0},  # Joint 1
            {'a': 0.244, 'alpha': 0.0, 'd': 0.0, 'theta': 0.0},       # Joint 2
            {'a': 0.213, 'alpha': 0.0, 'd': 0.0, 'theta': 0.0},       # Joint 3
            {'a': 0.0, 'alpha': np.pi/2, 'd': 0.125, 'theta': 0.0},   # Joint 4
            {'a': 0.0, 'alpha': -np.pi/2, 'd': 0.095, 'theta': 0.0},  # Joint 5
            {'a': 0.0, 'alpha': 0.0, 'd': 0.08, 'theta': 0.0},        # Joint 6
        ]

        # Joint limits
        self.joint_limits = [
            (-np.pi, np.pi),      # Joint 1
            (-np.pi/2, np.pi/2),  # Joint 2
            (-np.pi/2, np.pi/2),  # Joint 3
            (-np.pi, np.pi),      # Joint 4
            (-np.pi/2, np.pi/2),  # Joint 5
            (-np.pi, np.pi),      # Joint 6
        ]

        # Current joint states
        self.current_joints = [0.0] * 6

        # Publishers and subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.get_logger().info('Isaac Inverse Kinematics initialized')

    def joint_state_callback(self, msg):
        """Update current joint states."""
        if len(msg.position) >= 6:
            self.current_joints = list(msg.position[:6])

    def dh_transform(self, a, alpha, d, theta):
        """Calculate Denavit-Hartenberg transformation matrix."""
        return np.array([
            [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
            [np.sin(theta), np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
            [0, np.sin(alpha), np.cos(alpha), d],
            [0, 0, 0, 1]
        ])

    def forward_kinematics(self, joint_angles):
        """Calculate forward kinematics to get end-effector pose."""
        if len(joint_angles) != len(self.dh_params):
            raise ValueError("Joint angles must match DH parameters length")

        # Update DH parameters with current joint angles
        transforms = []
        for i, (param, angle) in enumerate(zip(self.dh_params, joint_angles)):
            dh = self.dh_params[i].copy()
            dh['theta'] = dh['theta'] + angle
            transform = self.dh_transform(dh['a'], dh['alpha'], dh['d'], dh['theta'])
            transforms.append(transform)

        # Calculate cumulative transformation
        T = np.eye(4)
        for transform in transforms:
            T = T @ transform

        # Extract position and orientation
        position = T[:3, 3]
        rotation_matrix = T[:3, :3]

        # Convert rotation matrix to quaternion
        quat = self.rotation_matrix_to_quaternion(rotation_matrix)

        return position, quat

    def inverse_kinematics(self, target_pose, initial_guess=None):
        """Solve inverse kinematics using numerical methods."""
        if initial_guess is None:
            initial_guess = self.current_joints

        # Use Jacobian-based iterative method
        target_pos = np.array([target_pose.position.x, target_pose.position.y, target_pose.position.z])
        target_rot = np.array([target_pose.orientation.x, target_pose.orientation.y,
                              target_pose.orientation.z, target_pose.orientation.w])

        # Convert quaternion to rotation matrix
        target_rot_matrix = self.quaternion_to_rotation_matrix(target_rot)

        # Iterative solution
        current_joints = np.array(initial_guess)
        max_iterations = 100
        tolerance = 1e-4

        for iteration in range(max_iterations):
            # Calculate current end-effector pose
            current_pos, current_quat = self.forward_kinematics(current_joints)
            current_rot_matrix = self.quaternion_to_rotation_matrix(current_quat)

            # Calculate position and orientation errors
            pos_error = target_pos - current_pos
            rot_error = self.rotation_matrix_error(target_rot_matrix, current_rot_matrix)

            # Check convergence
            if np.linalg.norm(pos_error) < tolerance and np.linalg.norm(rot_error) < tolerance:
                self.get_logger().info(f'IK converged after {iteration} iterations')
                return current_joints.tolist()

            # Calculate Jacobian
            jacobian = self.calculate_jacobian(current_joints)

            # Combine position and orientation errors
            error = np.concatenate([pos_error, rot_error])

            # Solve for joint velocity
            # Use damped least squares to handle singularities
            damping = 0.01
            I = np.eye(len(current_joints))
            joint_vel = np.linalg.solve(jacobian.T @ jacobian + damping * I, jacobian.T @ error)

            # Update joint angles
            current_joints = current_joints + 0.1 * joint_vel  # Step size

            # Apply joint limits
            for i, (min_limit, max_limit) in enumerate(self.joint_limits):
                current_joints[i] = np.clip(current_joints[i], min_limit, max_limit)

        self.get_logger().warn('IK did not converge within maximum iterations')
        return current_joints.tolist()

    def calculate_jacobian(self, joint_angles):
        """Calculate geometric Jacobian matrix."""
        n_joints = len(joint_angles)
        jacobian = np.zeros((6, n_joints))  # 6 DoF: 3 position + 3 orientation

        # Get transformation matrices for each joint
        transforms = []
        T = np.eye(4)
        for i, (param, angle) in enumerate(zip(self.dh_params, joint_angles)):
            dh = self.dh_params[i].copy()
            dh['theta'] = dh['theta'] + angle
            transform = self.dh_transform(dh['a'], dh['alpha'], dh['d'], dh['theta'])
            T = T @ transform
            transforms.append(T.copy())

        # Get end-effector position
        end_effector_pos = transforms[-1][:3, 3]

        # Calculate Jacobian columns
        for i in range(n_joints):
            # Z-axis of joint i in base frame
            z_i = transforms[i][:3, 2]
            # Position of joint i to end-effector
            r_i = end_effector_pos - transforms[i][:3, 3]

            # Position part of Jacobian
            jacobian[:3, i] = np.cross(z_i, r_i)
            # Orientation part of Jacobian
            jacobian[3:, i] = z_i

        return jacobian

    def rotation_matrix_to_quaternion(self, R):
        """Convert rotation matrix to quaternion."""
        # Method from https://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/
        trace = np.trace(R)

        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2  # s = 4 * qw
            qw = 0.25 * s
            qx = (R[2,1] - R[1,2]) / s
            qy = (R[0,2] - R[2,0]) / s
            qz = (R[1,0] - R[0,1]) / s
        elif (R[0,0] > R[1,1]) and (R[0,0] > R[2,2]):
            s = np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2  # s = 4 * qx
            qw = (R[2,1] - R[1,2]) / s
            qx = 0.25 * s
            qy = (R[0,1] + R[1,0]) / s
            qz = (R[0,2] + R[2,0]) / s
        elif R[1,1] > R[2,2]:
            s = np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2  # s = 4 * qy
            qw = (R[0,2] - R[2,0]) / s
            qx = (R[0,1] + R[1,0]) / s
            qy = 0.25 * s
            qz = (R[1,2] + R[2,1]) / s
        else:
            s = np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2  # s = 4 * qz
            qw = (R[1,0] - R[0,1]) / s
            qx = (R[0,2] + R[2,0]) / s
            qy = (R[1,2] + R[2,1]) / s
            qz = 0.25 * s

        return np.array([qx, qy, qz, qw])

    def quaternion_to_rotation_matrix(self, quat):
        """Convert quaternion to rotation matrix."""
        x, y, z, w = quat
        return np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x**2 + z**2), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x**2 + y**2)]
        ])

    def rotation_matrix_error(self, R1, R2):
        """Calculate orientation error between two rotation matrices."""
        R_error = R1.T @ R2
        angle_axis = self.rotation_matrix_to_angle_axis(R_error)
        return angle_axis

    def rotation_matrix_to_angle_axis(self, R):
        """Convert rotation matrix to angle-axis representation."""
        angle = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))

        if np.isclose(angle, 0):
            return np.array([0, 0, 0])

        factor = angle / (2 * np.sin(angle))
        axis = np.array([
            R[2,1] - R[1,2],
            R[0,2] - R[2,0],
            R[1,0] - R[0,1]
        ]) * factor

        return axis
```

## Grasp Planning and Object Manipulation

### Vision-Based Grasp Planning

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image
from geometry_msgs.msg import Pose, PoseArray
from visualization_msgs.msg import Marker, MarkerArray
from cv_bridge import CvBridge
from sensor_msgs_py import point_cloud2
import numpy as np
import cv2
from sklearn.cluster import DBSCAN

class IsaacGraspPlanner(Node):
    def __init__(self):
        super().__init__('isaac_grasp_planner')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Publishers and subscribers
        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            '/camera/depth/points',
            self.pointcloud_callback,
            10
        )

        self.image_sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10
        )

        self.grasp_poses_pub = self.create_publisher(
            PoseArray,
            '/grasp_poses',
            10
        )

        self.visualization_pub = self.create_publisher(
            MarkerArray,
            '/grasp_visualization',
            10
        )

        # Grasp planning parameters
        self.grasp_width = 0.08  # 8cm gripper width
        self.min_object_size = 0.02  # 2cm minimum object size
        self.max_grasp_height = 0.2  # 20cm maximum grasp height
        self.approach_distance = 0.1  # 10cm approach distance

        # Object detection
        self.rgb_image = None
        self.pointcloud = None

        self.get_logger().info('Isaac Grasp Planner initialized')

    def pointcloud_callback(self, msg):
        """Process point cloud for 3D object detection."""
        try:
            # Convert PointCloud2 to numpy array
            points_list = []
            for point in point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
                points_list.append([point[0], point[1], point[2]])

            if points_list:
                self.pointcloud = np.array(points_list)
                self.plan_grasps()
        except Exception as e:
            self.get_logger().error(f'Error processing point cloud: {e}')

    def image_callback(self, msg):
        """Process RGB image for object detection."""
        try:
            self.rgb_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def plan_grasps(self):
        """Plan grasps based on point cloud data."""
        if self.pointcloud is None or len(self.pointcloud) < 10:
            return

        # Segment objects using clustering
        objects = self.segment_objects(self.pointcloud)

        # Plan grasps for each object
        all_grasps = []
        for i, obj_points in enumerate(objects):
            if len(obj_points) > 100:  # Minimum object size
                grasps = self.plan_object_grasps(obj_points)
                all_grasps.extend(grasps)

        # Publish grasps
        self.publish_grasps(all_grasps)

    def segment_objects(self, points):
        """Segment objects using DBSCAN clustering."""
        # Filter points at reasonable height
        height_threshold = 0.1  # Only consider objects above 10cm
        valid_points = points[points[:, 2] > height_threshold]

        if len(valid_points) < 10:
            return []

        # Perform clustering
        clustering = DBSCAN(eps=0.05, min_samples=10)  # 5cm clustering distance
        labels = clustering.fit_predict(valid_points[:, :2])  # Use x,y only for clustering

        # Group points by cluster
        objects = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:  # Noise points
                continue

            cluster_mask = labels == label
            cluster_points = valid_points[cluster_mask]

            # Filter by size
            if len(cluster_points) > 100:  # Minimum 100 points per object
                objects.append(cluster_points)

        return objects

    def plan_object_grasps(self, obj_points):
        """Plan potential grasps for an object."""
        grasps = []

        # Calculate object properties
        centroid = np.mean(obj_points, axis=0)
        bbox_size = np.max(obj_points, axis=0) - np.min(obj_points, axis=0)

        # Plan top grasp
        top_grasp = self.plan_top_grasp(obj_points, centroid)
        if top_grasp:
            grasps.append(top_grasp)

        # Plan side grasps
        side_grasps = self.plan_side_grasps(obj_points, centroid, bbox_size)
        grasps.extend(side_grasps)

        return grasps

    def plan_top_grasp(self, obj_points, centroid):
        """Plan a top-down grasp."""
        # Position above the object
        grasp_pose = Pose()
        grasp_pose.position.x = float(centroid[0])
        grasp_pose.position.y = float(centroid[1])
        grasp_pose.position.z = float(centroid[2] + 0.1)  # 10cm above object

        # Top-down approach (z-axis down)
        grasp_pose.orientation.x = 0.0
        grasp_pose.orientation.y = 1.0
        grasp_pose.orientation.z = 0.0
        grasp_pose.orientation.w = 0.0

        # Check if grasp is feasible (no collision during approach)
        if self.is_grasp_feasible(grasp_pose, obj_points):
            return grasp_pose

        return None

    def plan_side_grasps(self, obj_points, centroid, bbox_size):
        """Plan side grasps around the object."""
        grasps = []

        # Plan grasps at different angles around the object
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            # Calculate grasp position
            grasp_x = centroid[0] + 0.1 * np.cos(angle)  # 10cm from center
            grasp_y = centroid[1] + 0.1 * np.sin(angle)
            grasp_z = centroid[2] + 0.05  # Slightly above center

            # Calculate approach direction (pointing toward object center)
            approach_x = -np.cos(angle)
            approach_y = -np.sin(angle)
            approach_z = 0.0

            # Calculate gripper orientation
            # For side grasp, gripper should be vertical
            grasp_pose = Pose()
            grasp_pose.position.x = grasp_x
            grasp_pose.position.y = grasp_y
            grasp_pose.position.z = grasp_z

            # Set orientation for side grasp
            # This is a simplified orientation - in practice, you'd calculate proper orientation
            grasp_pose.orientation = self.calculate_side_grasp_orientation(
                approach_x, approach_y, approach_z
            )

            if self.is_grasp_feasible(grasp_pose, obj_points):
                grasps.append(grasp_pose)

        return grasps

    def calculate_side_grasp_orientation(self, approach_x, approach_y, approach_z):
        """Calculate gripper orientation for side grasp."""
        # Create a rotation that aligns gripper with approach direction
        # This is a simplified calculation
        import tf_transformations

        # Define gripper frame: z-axis points out of gripper, x-axis points up
        z_axis = np.array([approach_x, approach_y, approach_z])
        z_axis = z_axis / np.linalg.norm(z_axis)

        # Choose up direction (could be refined based on object properties)
        up = np.array([0, 0, 1])

        # Calculate x-axis (gripper width direction)
        x_axis = np.cross(up, z_axis)
        if np.linalg.norm(x_axis) < 0.1:  # If z and up are parallel
            x_axis = np.array([1, 0, 0])
        else:
            x_axis = x_axis / np.linalg.norm(x_axis)

        # Calculate y-axis
        y_axis = np.cross(z_axis, x_axis)

        # Create rotation matrix
        rotation_matrix = np.array([x_axis, y_axis, z_axis]).T

        # Convert to quaternion
        quaternion = self.rotation_matrix_to_quaternion(rotation_matrix)

        return Quaternion(
            x=float(quaternion[0]),
            y=float(quaternion[1]),
            z=float(quaternion[2]),
            w=float(quaternion[3])
        )

    def is_grasp_feasible(self, grasp_pose, obj_points):
        """Check if a grasp is feasible (no collision during approach)."""
        # Check if approach path is clear
        approach_start = np.array([
            grasp_pose.position.x,
            grasp_pose.position.y,
            grasp_pose.position.z + self.approach_distance
        ])

        approach_end = np.array([
            grasp_pose.position.x,
            grasp_pose.position.y,
            grasp_pose.position.z
        ])

        # Simple collision check along approach path
        for point in obj_points:
            # Check if point is in approach path (simplified cylinder check)
            dist_to_path = self.point_to_line_distance(
                point[:2], approach_start[:2], approach_end[:2]
            )

            if dist_to_path < 0.05 and point[2] > approach_end[2]:  # 5cm clearance
                return False  # Collision detected

        return True

    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment."""
        line_vec = line_end - line_start
        point_vec = point - line_start
        line_len = np.linalg.norm(line_vec)
        line_unitvec = line_vec / line_len
        point_vec_scaled = point_vec / line_len

        t = np.dot(line_unitvec, point_vec_scaled)
        t = np.clip(t, 0.0, 1.0)
        nearest = line_vec * t
        dist = np.linalg.norm(point_vec - nearest)
        return dist

    def publish_grasps(self, grasps):
        """Publish grasp poses and visualization."""
        # Publish grasp poses
        pose_array = PoseArray()
        pose_array.header.frame_id = 'camera_depth_optical_frame'
        pose_array.header.stamp = self.get_clock().now().to_msg()
        pose_array.poses = grasps

        self.grasp_poses_pub.publish(pose_array)

        # Publish visualization
        self.visualize_grasps(grasps)

    def visualize_grasps(self, grasps):
        """Visualize grasp poses."""
        marker_array = MarkerArray()

        for i, grasp in enumerate(grasps):
            # Create gripper visualization
            gripper_marker = Marker()
            gripper_marker.header.frame_id = 'camera_depth_optical_frame'
            gripper_marker.header.stamp = self.get_clock().now().to_msg()
            gripper_marker.ns = "grasps"
            gripper_marker.id = i
            gripper_marker.type = Marker.CUBE
            gripper_marker.action = Marker.ADD

            gripper_marker.pose = grasp
            gripper_marker.scale.x = 0.1  # Gripper width
            gripper_marker.scale.y = 0.02  # Gripper thickness
            gripper_marker.scale.z = 0.06  # Gripper height

            gripper_marker.color.r = 1.0
            gripper_marker.color.g = 0.0
            gripper_marker.color.b = 0.0
            gripper_marker.color.a = 0.7

            marker_array.markers.append(gripper_marker)

            # Create approach direction visualization
            approach_marker = Marker()
            approach_marker.header = gripper_marker.header
            approach_marker.ns = "approach"
            approach_marker.id = i
            approach_marker.type = Marker.ARROW
            approach_marker.action = Marker.ADD

            # Set start and end points for approach arrow
            start_point = Point()
            start_point.x = grasp.position.x
            start_point.y = grasp.position.y
            start_point.z = grasp.position.z + self.approach_distance

            end_point = Point()
            end_point.x = grasp.position.x
            end_point.y = grasp.position.y
            end_point.z = grasp.position.z

            approach_marker.points = [start_point, end_point]
            approach_marker.scale.x = 0.01  # Shaft diameter
            approach_marker.scale.y = 0.02  # Head diameter

            approach_marker.color.r = 0.0
            approach_marker.color.g = 1.0
            approach_marker.color.b = 0.0
            approach_marker.color.a = 0.8

            marker_array.markers.append(approach_marker)

        self.visualization_pub.publish(marker_array)
```

## Motion Planning for Manipulation

### Trajectory Planning with Collision Avoidance

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from visualization_msgs.msg import MarkerArray
import numpy as np
from scipy.interpolate import interp1d
import time

class IsaacMotionPlanner(Node):
    def __init__(self):
        super().__init__('isaac_motion_planner')

        # Publishers and subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory',
            10
        )

        self.planning_scene_pub = self.create_publisher(
            PlanningScene,
            '/planning_scene',
            10
        )

        self.visualization_pub = self.create_publisher(
            MarkerArray,
            '/motion_plan_viz',
            10
        )

        # Robot state
        self.current_joints = None
        self.joint_names = []

        # Motion planning parameters
        self.max_velocity = 0.5  # rad/s
        self.max_acceleration = 0.5  # rad/s^2
        self.trajectory_resolution = 0.01  # 1cm resolution

        self.get_logger().info('Isaac Motion Planner initialized')

    def joint_state_callback(self, msg):
        """Update current joint states."""
        self.current_joints = list(msg.position)
        self.joint_names = list(msg.name)

    def plan_trajectory(self, start_joints, goal_joints, obstacles=None):
        """Plan collision-free trajectory using RRT-like approach."""
        if self.current_joints is None:
            self.get_logger().warn('No current joint state, using start_joints')
            current_joints = start_joints
        else:
            current_joints = self.current_joints

        # Simple linear interpolation as base trajectory
        # In practice, you'd use more sophisticated planners like RRT, PRM, etc.
        trajectory = self.linear_interpolation_trajectory(current_joints, goal_joints)

        # Add collision checking and avoidance
        safe_trajectory = self.add_collision_avoidance(trajectory, obstacles)

        # Smooth trajectory
        smoothed_trajectory = self.smooth_trajectory(safe_trajectory)

        return smoothed_trajectory

    def linear_interpolation_trajectory(self, start_joints, goal_joints, steps=50):
        """Create trajectory using linear interpolation in joint space."""
        trajectory = []

        for i in range(steps + 1):
            t = i / steps
            joint_positions = []
            for start_pos, goal_pos in zip(start_joints, goal_joints):
                pos = start_pos + t * (goal_pos - start_pos)
                joint_positions.append(pos)

            point = JointTrajectoryPoint()
            point.positions = joint_positions
            point.time_from_start.sec = int(t * 5)  # 5 seconds total
            point.time_from_start.nanosec = int((t * 5 - int(t * 5)) * 1e9)

            # Add velocities and accelerations (simple calculation)
            if i > 0:
                dt = 5.0 / steps
                prev_positions = trajectory[-1].positions
                velocities = [(curr - prev) / dt for curr, prev in zip(joint_positions, prev_positions)]
                point.velocities = velocities

            trajectory.append(point)

        return trajectory

    def add_collision_avoidance(self, trajectory, obstacles):
        """Add collision avoidance to trajectory."""
        if obstacles is None:
            return trajectory

        # Simple collision checking along trajectory
        safe_trajectory = []
        for point in trajectory:
            if not self.check_collision_at_joints(point.positions, obstacles):
                safe_trajectory.append(point)
            else:
                # Try to find alternative path around collision
                self.get_logger().warn('Collision detected, path planning needed')
                # In a real implementation, this would replan around the obstacle
                break

        return safe_trajectory if safe_trajectory else trajectory

    def check_collision_at_joints(self, joint_positions, obstacles):
        """Check if robot configuration collides with obstacles."""
        # This would involve forward kinematics and collision checking
        # For this example, we'll return False (no collision)
        # In practice, you'd check each link against obstacles
        return False

    def smooth_trajectory(self, trajectory):
        """Smooth trajectory using cubic splines."""
        if len(trajectory) < 3:
            return trajectory

        # Extract time and joint position arrays
        times = [point.time_from_start.sec + point.time_from_start.nanosec * 1e-9 for point in trajectory]
        n_joints = len(trajectory[0].positions)

        # Interpolate each joint separately
        smoothed_trajectory = []
        for i in range(len(trajectory)):
            point = JointTrajectoryPoint()
            point.time_from_start = trajectory[i].time_from_start

            # For each joint, interpolate position, velocity, and acceleration
            for j in range(n_joints):
                joint_positions = [p.positions[j] for p in trajectory]

                # Create spline interpolation
                if len(times) > 3:
                    spline = interp1d(times, joint_positions, kind='cubic', bounds_error=False, fill_value='extrapolate')
                    point.positions.append(float(spline(times[i])))
                else:
                    point.positions.append(trajectory[i].positions[j])

            smoothed_trajectory.append(point)

        return smoothed_trajectory

    def execute_trajectory(self, trajectory):
        """Execute the planned trajectory."""
        if not trajectory:
            self.get_logger().warn('Empty trajectory, nothing to execute')
            return

        # Create and publish trajectory message
        traj_msg = JointTrajectory()
        traj_msg.joint_names = self.joint_names[:len(trajectory[0].positions)]  # Ensure names match
        traj_msg.points = trajectory
        traj_msg.header.stamp = self.get_clock().now().to_msg()
        traj_msg.header.frame_id = 'base_link'

        self.trajectory_pub.publish(traj_msg)
        self.get_logger().info(f'Published trajectory with {len(trajectory)} points')

    def create_collision_object(self, name, primitive_type, dimensions, pose):
        """Create collision object for planning scene."""
        collision_obj = CollisionObject()
        collision_obj.header.frame_id = 'base_link'
        collision_obj.id = name

        # Create primitive
        primitive = SolidPrimitive()
        primitive.type = primitive_type
        primitive.dimensions = dimensions

        collision_obj.primitives.append(primitive)
        collision_obj.primitive_poses.append(pose)
        collision_obj.operation = CollisionObject.ADD

        return collision_obj

    def update_planning_scene(self, collision_objects):
        """Update the planning scene with collision objects."""
        scene = PlanningScene()
        scene.is_diff = True

        for obj in collision_objects:
            scene.world.collision_objects.append(obj)

        self.planning_scene_pub.publish(scene)
```

## Isaac Manipulation with AI Integration

### Learning-Based Grasp Synthesis

```python
import torch
import torch.nn as nn
import numpy as np

class GraspQualityNetwork(nn.Module):
    """Neural network for predicting grasp quality."""

    def __init__(self, point_cloud_size=1024, grasp_dim=7):  # 3 pos + 4 quat
        super().__init__()

        # Point cloud processing
        self.point_cloud_encoder = nn.Sequential(
            nn.Conv1d(3, 64, 1),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.ReLU(),
            nn.Conv1d(128, 256, 1),
            nn.ReLU(),
            nn.AdaptiveMaxPool1d(1)  # Global max pooling
        )

        # Grasp pose processing
        self.grasp_encoder = nn.Sequential(
            nn.Linear(grasp_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU()
        )

        # Fusion and prediction
        self.fusion = nn.Sequential(
            nn.Linear(256 + 128, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),  # Quality score (0-1)
            nn.Sigmoid()
        )

    def forward(self, point_cloud, grasp_pose):
        # Point cloud shape: (batch, 3, num_points)
        pc_features = self.point_cloud_encoder(point_cloud).squeeze(-1)  # (batch, 256)

        # Grasp pose shape: (batch, 7)
        grasp_features = self.grasp_encoder(grasp_pose)  # (batch, 128)

        # Concatenate features
        fused = torch.cat([pc_features, grasp_features], dim=-1)

        # Predict quality
        quality = self.fusion(fused)

        return quality

class IsaacAIGraspPlanner(Node):
    def __init__(self):
        super().__init__('isaac_ai_grasp_planner')

        # Initialize neural network
        self.quality_network = GraspQualityNetwork()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.quality_network.to(self.device)

        # Load pre-trained model if available
        model_path = '/path/to/pretrained/grasp_quality.pth'
        if os.path.exists(model_path):
            self.quality_network.load_state_dict(torch.load(model_path, map_location=self.device))
            self.get_logger().info('AI grasp quality model loaded')
        else:
            self.get_logger().info('Using randomly initialized AI grasp quality model')

        # Publishers and subscribers
        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            '/camera/depth/points',
            self.pointcloud_callback,
            10
        )

        self.grasp_candidates_pub = self.create_publisher(
            PoseArray,
            '/ai_grasp_candidates',
            10
        )

        # Storage
        self.current_pointcloud = None

        self.get_logger().info('Isaac AI Grasp Planner initialized')

    def pointcloud_callback(self, msg):
        """Process point cloud and generate AI-based grasp candidates."""
        try:
            # Convert PointCloud2 to numpy array
            points_list = []
            for point in point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
                points_list.append([point[0], point[1], point[2]])

            if points_list:
                self.current_pointcloud = np.array(points_list).T  # Shape: (3, N)
                self.generate_ai_grasps()
        except Exception as e:
            self.get_logger().error(f'Error processing point cloud: {e}')

    def generate_ai_grasps(self):
        """Generate grasp candidates using AI model."""
        if self.current_pointcloud is None or self.current_pointcloud.shape[1] < 10:
            return

        # Convert to tensor
        pc_tensor = torch.FloatTensor(self.current_pointcloud).unsqueeze(0).to(self.device)

        # Generate candidate grasps
        candidate_grasps = self.generate_grasp_candidates(self.current_pointcloud)

        if not candidate_grasps:
            return

        # Evaluate each grasp with AI model
        best_grasp = None
        best_quality = -1.0

        for grasp in candidate_grasps:
            grasp_tensor = torch.FloatTensor(grasp).unsqueeze(0).to(self.device)

            with torch.no_grad():
                quality = self.quality_network(pc_tensor, grasp_tensor).item()

            if quality > best_quality:
                best_quality = quality
                best_grasp = grasp

        # Publish best grasp if quality is above threshold
        if best_grasp is not None and best_quality > 0.5:  # Quality threshold
            self.publish_best_grasp(best_grasp, best_quality)

    def generate_grasp_candidates(self, pointcloud):
        """Generate grasp candidates based on point cloud geometry."""
        candidates = []

        # Sample points from point cloud
        num_samples = min(100, pointcloud.shape[1])  # Limit samples for efficiency
        indices = np.random.choice(pointcloud.shape[1], num_samples, replace=False)

        for idx in indices:
            point = pointcloud[:, idx]

            # Generate multiple grasp orientations at this point
            for angle in np.linspace(0, 2*np.pi, 8):
                # Simple grasp at this point with different orientations
                grasp = [
                    float(point[0]),  # x
                    float(point[1]),  # y
                    float(point[2] + 0.1),  # z (slightly above point)
                    0.0,  # qx
                    0.0,  # qy
                    np.sin(angle/2),  # qz
                    np.cos(angle/2)   # qw
                ]
                candidates.append(grasp)

        return candidates

    def publish_best_grasp(self, grasp, quality):
        """Publish the best grasp candidate."""
        pose_array = PoseArray()
        pose_array.header.frame_id = 'camera_depth_optical_frame'
        pose_array.header.stamp = self.get_clock().now().to_msg()

        pose = Pose()
        pose.position.x = grasp[0]
        pose.position.y = grasp[1]
        pose.position.z = grasp[2]
        pose.orientation.x = grasp[3]
        pose.orientation.y = grasp[4]
        pose.orientation.z = grasp[5]
        pose.orientation.w = grasp[6]

        pose_array.poses.append(pose)

        self.grasp_candidates_pub.publish(pose_array)
        self.get_logger().info(f'AI selected grasp with quality: {quality:.3f}')
```

## Force Control and Compliance

### Impedance Control for Safe Manipulation

```python
class IsaacImpedanceController(Node):
    def __init__(self):
        super().__init__('isaac_impedance_controller')

        # Impedance control parameters
        self.mass = 1.0  # Equivalent mass
        self.damping = 2.0  # Damping coefficient
        self.stiffness = 100.0  # Stiffness coefficient

        # Desired pose and compliance
        self.desired_pose = None
        self.current_pose = None
        self.external_force = np.array([0.0, 0.0, 0.0])

        # Publishers and subscribers
        self.desired_pose_sub = self.create_subscription(
            PoseStamped,
            '/desired_pose',
            self.desired_pose_callback,
            10
        )

        self.current_pose_sub = self.create_subscription(
            PoseStamped,
            '/current_pose',
            self.current_pose_callback,
            10
        )

        self.wrench_sub = self.create_subscription(
            WrenchStamped,
            '/wrench',
            self.wrench_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Control timer
        self.control_timer = self.create_timer(0.01, self.impedance_control_step)  # 100 Hz

        self.get_logger().info('Isaac Impedance Controller initialized')

    def desired_pose_callback(self, msg):
        """Update desired pose."""
        self.desired_pose = msg.pose

    def current_pose_callback(self, msg):
        """Update current pose."""
        self.current_pose = msg.pose

    def wrench_callback(self, msg):
        """Update external force/torque measurements."""
        self.external_force = np.array([
            msg.wrench.force.x,
            msg.wrench.force.y,
            msg.wrench.force.z
        ])

    def impedance_control_step(self):
        """Execute one step of impedance control."""
        if self.desired_pose is None or self.current_pose is None:
            return

        # Calculate position error
        pos_error = np.array([
            self.desired_pose.position.x - self.current_pose.position.x,
            self.desired_pose.position.y - self.current_pose.position.y,
            self.desired_pose.position.z - self.current_pose.position.z
        ])

        # Calculate velocity (simple approximation)
        # In practice, you'd have actual velocity feedback
        velocity = np.zeros(3)

        # Impedance control law: M*v_dot + B*v + K*x = F_external
        # Rearranged: v_dot = M^(-1) * (F_external - B*v - K*x)
        acceleration = (1.0 / self.mass) * (
            self.external_force -
            self.damping * velocity -
            self.stiffness * pos_error
        )

        # Integrate to get velocity command
        dt = 0.01  # Control period
        target_velocity = velocity + acceleration * dt

        # Create and publish command
        cmd = Twist()
        cmd.linear.x = float(target_velocity[0])
        cmd.linear.y = float(target_velocity[1])
        cmd.linear.z = float(target_velocity[2])

        # Add damping for stability
        cmd.linear.x *= 0.8
        cmd.linear.y *= 0.8
        cmd.linear.z *= 0.8

        self.cmd_pub.publish(cmd)
```

## Isaac Manipulation Best Practices

### Multi-Modal Integration

```python
class IsaacMultiModalManipulator(Node):
    """Integrates vision, force, and motion for robust manipulation."""

    def __init__(self):
        super().__init__('isaac_multi_modal_manipulator')

        # Initialize components
        self.vision_system = IsaacGraspPlanner(self)
        self.motion_planner = IsaacMotionPlanner(self)
        self.impedance_controller = IsaacImpedanceController(self)

        # Manipulation state
        self.manipulation_state = 'IDLE'  # IDLE, APPROACHING, GRASPING, LIFTING, PLACING

        # Object detection and tracking
        self.tracked_objects = {}
        self.current_target = None

        # Publishers
        self.state_pub = self.create_publisher(String, '/manipulation_state', 10)

        # Timer for state machine
        self.state_timer = self.create_timer(0.1, self.manipulation_step)

        self.get_logger().info('Isaac Multi-Modal Manipulator initialized')

    def manipulation_step(self):
        """Main manipulation state machine."""
        if self.manipulation_state == 'IDLE':
            # Look for objects to manipulate
            if self.detect_objects():
                self.manipulation_state = 'APPROACHING'
                self.get_logger().info('Object detected, approaching')

        elif self.manipulation_state == 'APPROACHING':
            # Plan and execute approach trajectory
            if self.execute_approach():
                self.manipulation_state = 'GRASPING'
                self.get_logger().info('Approach complete, grasping')

        elif self.manipulation_state == 'GRASPING':
            # Execute grasp with force control
            if self.execute_grasp():
                self.manipulation_state = 'LIFTING'
                self.get_logger().info('Grasp successful, lifting')

        elif self.manipulation_state == 'LIFTING':
            # Lift object safely
            if self.lift_object():
                self.manipulation_state = 'PLACING'
                self.get_logger().info('Lifted, placing')

        elif self.manipulation_state == 'PLACING':
            # Place object and release
            if self.place_object():
                self.manipulation_state = 'IDLE'
                self.get_logger().info('Object placed, idle')

        # Publish current state
        state_msg = String()
        state_msg.data = self.manipulation_state
        self.state_pub.publish(state_msg)

    def detect_objects(self):
        """Detect objects using vision system."""
        # This would integrate with the vision system
        # For now, return True to simulate object detection
        return True

    def execute_approach(self):
        """Execute approach trajectory."""
        # Plan and execute approach using motion planner
        # Use force feedback to detect contact
        return True

    def execute_grasp(self):
        """Execute grasp with force control."""
        # Use impedance control for safe grasping
        # Monitor grasp quality
        return True

    def lift_object(self):
        """Lift the grasped object."""
        # Use force control to lift with appropriate force
        return True

    def place_object(self):
        """Place the object at target location."""
        # Use vision feedback to align placement
        # Release object with controlled force
        return True
```

## Summary

Isaac manipulation provides a comprehensive framework for robotic manipulation tasks, integrating inverse kinematics, grasp planning, motion planning, and force control. The platform leverages GPU acceleration for real-time processing of sensory data and enables learning-based approaches for improved manipulation capabilities. Understanding the different components of the manipulation stack - from low-level control to high-level task planning - is essential for creating robust and capable manipulation systems.