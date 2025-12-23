---
sidebar_label: 'Week 9 Lab: Isaac AI Vision Pipeline'
title: 'Week 9 Lab: Isaac AI Vision Pipeline'
---

# Week 9 Lab: Isaac AI Vision Pipeline

## Objective

In this lab, you will create a complete AI vision pipeline using Isaac tools, implementing object detection, feature tracking, and depth estimation. You'll learn how to integrate different computer vision components into a cohesive perception system.

## Prerequisites

- Completion of Weeks 1-8 labs
- Isaac ROS packages installed
- Basic knowledge of OpenCV and deep learning
- Understanding of ROS 2 message types

## Step 1: Create a New ROS 2 Package

```bash
# Navigate to your workspace
cd ~/ros2_lab_ws/src

# Create a new package for the Isaac vision lab
ros2 pkg create --build-type ament_python isaac_vision_pipeline --dependencies rclpy std_msgs sensor_msgs geometry_msgs vision_msgs cv_bridge message_filters
```

## Step 2: Create the Vision Pipeline Configuration

Create the necessary directories:

```bash
mkdir -p ~/ros2_lab_ws/src/isaac_vision_pipeline/config
mkdir -p ~/ros2_lab_ws/src/isaac_vision_pipeline/launch
mkdir -p ~/ros2_lab_ws/src/isaac_vision_pipeline/models
```

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/config/vision_pipeline_config.yaml`:

```yaml
vision_pipeline:
  ros__parameters:
    # Processing parameters
    detection_confidence_threshold: 0.5
    tracking_feature_count: 100
    stereo_disparity_range: 128
    stereo_block_size: 5

    # Performance parameters
    processing_rate: 10.0  # Hz
    use_gpu_acceleration: true
    gpu_memory_fraction: 0.8

    # Camera parameters (example values)
    camera:
      width: 640
      height: 480
      focal_length: 320.0
      baseline: 0.12  # Stereo baseline in meters

    # Topic names
    input_topics:
      left_camera: "/camera/left/image_rect_color"
      right_camera: "/camera/right/image_rect_color"
      depth_camera: "/depth_camera/depth/image_rect_raw"

    output_topics:
      detections: "/vision_pipeline/detections"
      features: "/vision_pipeline/features"
      depth_map: "/vision_pipeline/depth_map"
      pointcloud: "/vision_pipeline/pointcloud"
```

## Step 3: Create the Main Vision Pipeline Node

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/isaac_vision_pipeline/vision_pipeline.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, CameraInfo, PointCloud2
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
from message_filters import ApproximateTimeSynchronizer, Subscriber
import numpy as np
import cv2
from typing import Optional, Tuple, List
import threading
import time

class IsaacVisionPipeline(Node):
    def __init__(self):
        super().__init__('isaac_vision_pipeline')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Parameters
        self.detection_conf_threshold = self.declare_parameter(
            'detection_confidence_threshold', 0.5
        ).value
        self.feature_count = self.declare_parameter('tracking_feature_count', 100).value
        self.stereo_disparity_range = self.declare_parameter('stereo_disparity_range', 128).value
        self.stereo_block_size = self.declare_parameter('stereo_block_size', 5).value
        self.processing_rate = self.declare_parameter('processing_rate', 10.0).value

        # Initialize stereo matcher
        self.stereo_matcher = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=self.stereo_disparity_range,
            blockSize=self.stereo_block_size,
            P1=8 * 3 * self.stereo_block_size**2,
            P2=32 * 3 * self.stereo_block_size**2,
            disp12MaxDiff=1,
            uniquenessRatio=15,
            speckleWindowSize=0,
            speckleRange=2,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )

        # Feature tracking
        self.prev_gray = None
        self.tracked_features = None
        self.feature_lock = threading.Lock()

        # Camera info storage
        self.left_camera_info = None
        self.right_camera_info = None

        # Publishers
        self.detection_pub = self.create_publisher(Detection2DArray, '/vision_pipeline/detections', 10)
        self.feature_pub = self.create_publisher(Image, '/vision_pipeline/features', 10)
        self.depth_pub = self.create_publisher(Image, '/vision_pipeline/depth_map', 10)
        self.pc_pub = self.create_publisher(PointCloud2, '/vision_pipeline/pointcloud', 10)

        # Subscribers with synchronization
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Create subscribers for stereo pair
        self.left_sub = Subscriber(self, Image, '/camera/left/image_rect_color', qos_profile=qos_profile)
        self.right_sub = Subscriber(self, Image, '/camera/right/image_rect_color', qos_profile=qos_profile)

        # Synchronize stereo images
        self.sync = ApproximateTimeSynchronizer(
            [self.left_sub, self.right_sub],
            queue_size=10,
            slop=0.1
        )
        self.sync.registerCallback(self.stereo_callback)

        # Camera info subscribers
        self.left_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/left/camera_info',
            self.left_info_callback,
            10
        )

        self.right_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/right/camera_info',
            self.right_info_callback,
            10
        )

        # Processing timer
        self.processing_timer = self.create_timer(1.0/self.processing_rate, self.process_pipeline)

        # Statistics
        self.frame_count = 0
        self.last_process_time = time.time()

        self.get_logger().info('Isaac Vision Pipeline initialized')

    def left_info_callback(self, msg):
        """Handle left camera info."""
        self.left_camera_info = msg

    def right_info_callback(self, msg):
        """Handle right camera info."""
        self.right_camera_info = msg

    def stereo_callback(self, left_msg, right_msg):
        """Process synchronized stereo images."""
        try:
            # Convert ROS images to OpenCV
            self.left_cv = self.bridge.imgmsg_to_cv2(left_msg, "bgr8")
            self.right_cv = self.bridge.imgmsg_to_cv2(right_msg, "bgr8")
            self.stereo_header = left_msg.header

            self.frame_count += 1
        except Exception as e:
            self.get_logger().error(f'Error processing stereo images: {e}')

    def process_pipeline(self):
        """Main processing pipeline."""
        if not hasattr(self, 'left_cv') or not hasattr(self, 'right_cv'):
            return

        start_time = time.time()

        # Convert to grayscale for processing
        left_gray = cv2.cvtColor(self.left_cv, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(self.right_cv, cv2.COLOR_BGR2GRAY)

        # 1. Perform stereo depth estimation
        depth_map = self.estimate_depth(left_gray, right_gray)

        # 2. Perform object detection
        detections = self.perform_object_detection(self.left_cv)

        # 3. Perform feature tracking
        feature_image = self.perform_feature_tracking(left_gray)

        # 4. Generate point cloud from depth
        pointcloud = self.generate_pointcloud(depth_map, self.stereo_header)

        # Publish results
        self.publish_results(detections, feature_image, depth_map, pointcloud, self.stereo_header)

        # Calculate processing time
        process_time = time.time() - start_time
        fps = 1.0 / (time.time() - self.last_process_time) if (time.time() - self.last_process_time) > 0 else 0
        self.last_process_time = time.time()

        self.get_logger().info(
            f'Processed frame {self.frame_count}, '
            f'Processing time: {process_time*1000:.1f}ms, '
            f'FPS: {fps:.1f}'
        )

    def estimate_depth(self, left_gray: np.ndarray, right_gray: np.ndarray) -> np.ndarray:
        """Estimate depth using stereo matching."""
        try:
            # Compute disparity
            disparity = self.stereo_matcher.compute(left_gray, right_gray).astype(np.float32) / 16.0

            # Convert disparity to depth
            if self.left_camera_info:
                baseline = abs(self.left_camera_info.p[3] / self.left_camera_info.p[0])
                focal_length = self.left_camera_info.p[0]

                # Depth = (baseline * focal_length) / disparity
                depth = np.zeros_like(disparity)
                valid_mask = disparity > 0
                depth[valid_mask] = (baseline * focal_length) / disparity[valid_mask]
                depth[disparity <= 0] = 100.0  # Set invalid to max range
            else:
                # Use default parameters if camera info not available
                baseline = 0.12  # 12cm baseline
                focal_length = 320.0
                depth = np.ones_like(disparity) * 10.0  # Default depth

            return depth
        except Exception as e:
            self.get_logger().error(f'Error in depth estimation: {e}')
            return np.ones_like(left_gray) * 10.0

    def perform_object_detection(self, image: np.ndarray) -> Detection2DArray:
        """Perform object detection (simulated with traditional CV)."""
        # In a real implementation, this would use a trained neural network
        # For this lab, we'll simulate detection with traditional computer vision

        detections = Detection2DArray()
        detections.header = self.stereo_header

        # Convert to grayscale and detect contours (simulating object detection)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small contours
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Create detection
                detection = Detection2D()
                detection.bbox.center.x = x + w / 2
                detection.bbox.center.y = y + h / 2
                detection.bbox.size_x = w
                detection.bbox.size_y = h

                # Add dummy classification
                from vision_msgs.msg import ObjectHypothesisWithPose
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.hypothesis.class_id = "object"
                hypothesis.hypothesis.score = min(1.0, area / 10000)  # Confidence based on size

                detection.results.append(hypothesis)
                detections.detections.append(detection)

        return detections

    def perform_feature_tracking(self, gray: np.ndarray) -> np.ndarray:
        """Perform feature tracking using optical flow."""
        with self.feature_lock:
            feature_image = self.left_cv.copy()

            if self.prev_gray is not None and self.tracked_features is not None:
                # Calculate optical flow
                new_features, status, error = cv2.calcOpticalFlowPyrLK(
                    self.prev_gray, gray, self.tracked_features, None,
                    winSize=(15, 15), maxLevel=2,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
                )

                # Filter good features
                good_new = new_features[status.ravel() == 1]
                good_old = self.tracked_features[status.ravel() == 1]

                # Draw feature tracks
                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = new.ravel().astype(int)
                    c, d = old.ravel().astype(int)
                    feature_image = cv2.line(feature_image, (a, b), (c, d), (0, 255, 0), 2)
                    feature_image = cv2.circle(feature_image, (a, b), 3, (255, 0, 0), -1)

                # Update tracked features
                self.tracked_features = good_new.reshape(-1, 1, 2)

                # Add new features if we don't have enough
                if len(self.tracked_features) < self.feature_count // 2:
                    new_features = self.add_new_features(gray)
                    if new_features is not None:
                        self.tracked_features = np.vstack((self.tracked_features, new_features))
            else:
                # Initialize features
                self.tracked_features = self.add_new_features(gray)

            # Update previous frame
            self.prev_gray = gray.copy()

            return feature_image

    def add_new_features(self, gray: np.ndarray) -> Optional[np.ndarray]:
        """Add new features for tracking."""
        # Find good features to track
        features = cv2.goodFeaturesToTrack(
            gray,
            maxCorners=self.feature_count,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )

        if features is not None:
            return features.reshape(-1, 1, 2)
        else:
            return None

    def generate_pointcloud(self, depth: np.ndarray, header) -> PointCloud2:
        """Generate point cloud from depth map."""
        height, width = depth.shape

        if self.left_camera_info:
            # Get camera intrinsic parameters
            fx = self.left_camera_info.p[0]
            fy = self.left_camera_info.p[5]
            cx = self.left_camera_info.p[2]
            cy = self.left_camera_info.p[6]
        else:
            # Use default parameters
            fx = fy = 320.0
            cx = width / 2
            cy = height / 2

        # Create coordinate grids
        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

        # Convert pixel coordinates to 3D points
        x_3d = (x_coords - cx) * depth / fx
        y_3d = (y_coords - cy) * depth / fy
        z_3d = depth

        # Flatten and combine
        points = np.stack([x_3d.flatten(), y_3d.flatten(), z_3d.flatten()], axis=1)

        # Filter valid points
        valid_mask = (z_3d.flatten() > 0.1) & (z_3d.flatten() < 50.0)
        valid_points = points[valid_mask]

        # Create PointCloud2 message
        from sensor_msgs_py import point_cloud2
        from sensor_msgs.msg import PointField

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]

        header.frame_id = 'camera_depth_optical_frame'
        return point_cloud2.create_cloud(header, fields, valid_points)

    def publish_results(self, detections, feature_image, depth_map, pointcloud, header):
        """Publish processing results."""
        # Publish detections
        detections.header = header
        self.detection_pub.publish(detections)

        # Publish feature tracking visualization
        feature_msg = self.bridge.cv2_to_imgmsg(feature_image, "bgr8")
        feature_msg.header = header
        self.feature_pub.publish(feature_msg)

        # Publish depth map
        depth_msg = self.bridge.cv2_to_imgmsg(depth_map, "32FC1")
        depth_msg.header = header
        self.depth_pub.publish(depth_msg)

        # Publish point cloud
        self.pc_pub.publish(pointcloud)

def main(args=None):
    rclpy.init(args=args)
    vision_pipeline = IsaacVisionPipeline()

    try:
        rclpy.spin(vision_pipeline)
    except KeyboardInterrupt:
        vision_pipeline.get_logger().info('Shutting down vision pipeline...')
    finally:
        vision_pipeline.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 4: Create an AI Model Integration Node

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/isaac_vision_pipeline/ai_model_node.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import numpy as np
import cv2
from typing import List, Tuple

class IsaacAIModelNode(Node):
    def __init__(self):
        super().__init__('isaac_ai_model_node')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Publishers and subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_rect_color',
            self.image_callback,
            10
        )

        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/ai_detections',
            10
        )

        # Simulated model parameters
        self.model_initialized = False
        self.confidence_threshold = 0.5

        # For this lab, we'll simulate a detection model
        # In a real implementation, you would load an actual trained model
        self.initialize_model()

        self.get_logger().info('Isaac AI Model Node initialized')

    def initialize_model(self):
        """Initialize the AI model (simulated for this lab)."""
        # In a real implementation, you would load a trained model here
        # For this lab, we'll use a simulated model
        self.model_initialized = True
        self.get_logger().info('Simulated AI model initialized')

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for AI model input."""
        # Resize image to model input size (example: 416x416)
        input_size = (416, 416)

        # Letterbox resize to maintain aspect ratio
        h, w = image.shape[:2]
        scale = min(input_size[0] / w, input_size[1] / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized = cv2.resize(image, (new_w, new_h))

        # Create letterboxed image
        letterboxed = np.full((input_size[1], input_size[0], 3), 128, dtype=np.uint8)
        start_x = (input_size[0] - new_w) // 2
        start_y = (input_size[1] - new_h) // 2
        letterboxed[start_y:start_y+new_h, start_x:start_x+new_w] = resized

        # Convert BGR to RGB and normalize
        letterboxed = letterboxed[:, :, ::-1]  # BGR to RGB
        letterboxed = letterboxed.transpose((2, 0, 1)).astype(np.float32)  # HWC to CHW
        letterboxed /= 255.0  # Normalize to [0, 1]

        return letterboxed

    def postprocess_output(self, output: np.ndarray, original_shape: Tuple[int, int]) -> Detection2DArray:
        """Postprocess AI model output to detections."""
        # In a real implementation, this would decode the actual model output
        # For this lab, we'll simulate detections based on traditional CV

        detections = Detection2DArray()

        # Convert back to original image coordinates
        orig_h, orig_w = original_shape[:2]
        model_h, model_w = 416, 416  # Model input size

        # Simulate detections by finding contours in the original image
        gray = cv2.cvtColor(cv2.resize(self.original_image, (model_w, model_h)), cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filter small contours
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Scale back to original image size
                x_scaled = int(x * orig_w / model_w)
                y_scaled = int(y * orig_h / model_h)
                w_scaled = int(w * orig_w / model_w)
                h_scaled = int(h * orig_h / model_h)

                # Calculate confidence based on area
                confidence = min(1.0, area / 5000)

                if confidence > self.confidence_threshold:
                    # Create detection
                    detection = Detection2D()
                    detection.bbox.center.x = x_scaled + w_scaled / 2
                    detection.bbox.center.y = y_scaled + h_scaled / 2
                    detection.bbox.size_x = w_scaled
                    detection.bbox.size_y = h_scaled

                    # Add classification hypothesis
                    hypothesis = ObjectHypothesisWithPose()
                    hypothesis.hypothesis.class_id = "object"
                    hypothesis.hypothesis.score = confidence

                    detection.results.append(hypothesis)
                    detections.detections.append(detection)

        return detections

    def image_callback(self, msg):
        """Process incoming image with AI model."""
        try:
            # Store original image for postprocessing
            self.original_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Preprocess image
            preprocessed = self.preprocess_image(self.original_image)

            # Simulate AI inference
            # In a real implementation, you would run the actual model here
            # For this lab, we'll simulate the inference output
            simulated_output = np.random.random((1, 100, 6))  # Simulated output format

            # Postprocess output to detections
            detections = self.postprocess_output(simulated_output, self.original_image.shape)
            detections.header = msg.header

            # Publish detections
            self.detection_pub.publish(detections)

            self.get_logger().info(f'AI model processed image, found {len(detections.detections)} detections')

        except Exception as e:
            self.get_logger().error(f'Error in AI model processing: {e}')

def main(args=None):
    rclpy.init(args=args)
    ai_node = IsaacAIModelNode()

    try:
        rclpy.spin(ai_node)
    except KeyboardInterrupt:
        ai_node.get_logger().info('Shutting down AI model node...')
    finally:
        ai_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Step 5: Create Launch Files

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/launch/vision_pipeline_launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    params_file = LaunchConfiguration('params_file', default='vision_pipeline_config.yaml')

    # Package name
    pkg_isaac_vision_pipeline = FindPackageShare('isaac_vision_pipeline')

    # Vision pipeline node
    vision_pipeline = Node(
        package='isaac_vision_pipeline',
        executable='vision_pipeline',
        name='vision_pipeline',
        parameters=[
            PathJoinSubstitution([pkg_isaac_vision_pipeline, 'config', params_file]),
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    # AI model node
    ai_model_node = Node(
        package='isaac_vision_pipeline',
        executable='ai_model_node',
        name='ai_model_node',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # RViz for visualization (optional)
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('isaac_vision_pipeline'),
        'rviz',
        'vision_pipeline.rviz'
    ])

    # Create RViz directory and config if it doesn't exist
    rviz_dir = os.path.join(pkg_isaac_vision_pipeline.find('isaac_vision_pipeline'), 'rviz')
    os.makedirs(rviz_dir, exist_ok=True)

    # Create a basic RViz config file
    rviz_config_path = os.path.join(rviz_dir, 'vision_pipeline.rviz')
    if not os.path.exists(rviz_config_path):
        with open(rviz_config_path, 'w') as f:
            f.write('''Panels:
  - Class: rviz_common/Displays
    Help Height: 78
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Status1
        - /Image1
        - /PointCloud21
      Splitter Ratio: 0.5
    Tree Height: 787
  - Class: rviz_common/Selection
    Name: Selection
  - Class: rviz_common/Tool Properties
    Expanded:
      - /2D Goal Pose1
      - /Publish Point1
    Name: Tool Properties
    Splitter Ratio: 0.5886790156364441
  - Class: rviz_common/Views
    Expanded:
      - /Current View1
    Name: Views
    Splitter Ratio: 0.5
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 10
      Reference Frame: <Fixed Frame>
      Value: true
    - Class: rviz_default_plugins/Image
      Enabled: true
      Max Value: 1
      Min Value: 0
      Name: Image
      Overlay Alpha: 0.5
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /vision_pipeline/features
      Value: true
    - Alpha: 1
      Autocompute Intensity Bounds: true
      Autocompute Value Bounds:
        Max Value: 10
        Min Value: -10
        Value: true
      Axis: Z
      Channel Name: intensity
      Class: rviz_default_plugins/PointCloud2
      Color: 255; 255; 255
      Color Transformer: Intensity
      Decay Time: 0
      Enabled: true
      Invert Rainbow: false
      Max Color: 255; 255; 255
      Max Intensity: 4096
      Min Color: 0; 0; 0
      Min Intensity: 0
      Name: PointCloud2
      Position Transformer: XYZ
      Selectable: true
      Size (Pixels): 3
      Size (m): 0.009999999776482582
      Style: Flat Squares
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Best Effort
        Value: /vision_pipeline/pointcloud
      Use Fixed Frame: true
      Use rainbow: true
      Value: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: camera_depth_optical_frame
    Frame Rate: 30
  Name: root
  Tools:
    - Class: rviz_default_plugins/Interact
      Hide Inactive Objects: true
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure
    - Class: rviz_default_plugins/SetInitialPose
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /initialpose
    - Class: rviz_default_plugins/SetGoal
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /goal_pose
    - Class: rviz_default_plugins/PublishPoint
      Single click: true
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /clicked_point
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 10
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.05999999865889549
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05000000074505806
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.009999999776482582
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Value: Orbit (rviz)
      Yaw: 0.5
    Saved: ~
Window Geometry:
  Displays:
    collapsed: false
  Height: 1025
  Hide Left Dock: false
  Hide Right Dock: false
  Image:
    collapsed: false
  QMainWindow State: 000000ff00000000fd000000040000000000000156000003a7fc0200000008fb0000001200530065006c0065006300740069006f006e00000001e10000009b0000005c00fffffffb0000001e0054006f006f006c002000500072006f007000650072007400690065007302000001ed000001df00000185000000a3fb000000120056006900650077007300200054006f006f02000001df000002110000018500000122fb000000200054006f006f006c002000500072006f0070006500720074006900650073003203000002880000011d000002210000017afb000000100044006900730070006c006100790073010000003d000003a7000000c900fffffffb0000002000730065006c0065006300740069006f006e00200062007500660066006500720200000138000000aa0000023a00000294fb00000014005700690064006500530074006500720065006f02000000e6000000d2000003ee0000030bfb0000000c004b0069006e0065006300740200000186000001060000030c00000261000000010000010f000003a7fc0200000003fb0000001e0054006f006f006c002000500072006f00700065007200740069006500730100000041000000780000000000000000fb0000000a00560069006500770073010000003d000003a7000000a400fffffffb0000001200530065006c0065006300740069006f006e010000025a000000b200000000000000000000000200000490000000a9fc0100000001fb0000000a00560069006500770073030000004e00000080000002e10000019700000003000004420000003efc0100000002fb0000000800540069006d00650100000000000004420000000000000000fb0000000800540069006d00650100000000000004500000000000000000000004ba000003a700000004000000040000000800000008fc0000000100000002000000010000000a0054006f006f006c00730100000000ffffffff0000000000000000''')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='vision_pipeline_rviz',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value='vision_pipeline_config.yaml',
            description='Path to the parameters file'
        ),
        vision_pipeline,
        ai_model_node,
        # Uncomment the following lines if you want to launch RViz automatically
        # TimerAction(
        #     period=3.0,
        #     actions=[rviz]
        # )
    ])
```

## Step 6: Create Setup Files

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_vision_pipeline'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Isaac AI vision pipeline package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_pipeline = isaac_vision_pipeline.vision_pipeline:main',
            'ai_model_node = isaac_vision_pipeline.ai_model_node:main',
        ],
    },
)
```

Update `package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>isaac_vision_pipeline</name>
  <version>0.0.0</version>
  <description>Isaac AI vision pipeline package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_cmake_python</buildtool_depend>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>vision_msgs</depend>
  <depend>cv_bridge</depend>
  <depend>message_filters</depend>

  <exec_depend>rviz2</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Step 7: Build the Package

```bash
# Go back to workspace root
cd ~/ros2_lab_ws

# Build the package
colcon build --packages-select isaac_vision_pipeline

# Source the workspace
source install/setup.bash
```

## Step 8: Test the Vision Pipeline

For this lab, we'll create a simple test node to simulate camera data:

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/isaac_vision_pipeline/test_camera_publisher.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
import cv2
from geometry_msgs.msg import Vector3

class TestCameraPublisher(Node):
    def __init__(self):
        super().__init__('test_camera_publisher')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Create publishers for stereo pair
        self.left_pub = self.create_publisher(Image, '/camera/left/image_rect_color', 10)
        self.right_pub = self.create_publisher(Image, '/camera/right/image_rect_color', 10)

        # Camera info publishers
        self.left_info_pub = self.create_publisher(CameraInfo, '/camera/left/camera_info', 10)
        self.right_info_pub = self.create_publisher(CameraInfo, '/camera/right/camera_info', 10)

        # Create a timer to publish test images
        self.timer = self.create_timer(0.1, self.publish_test_images)  # 10 Hz

        # Generate test pattern
        self.frame_id = 0
        self.get_logger().info('Test camera publisher initialized')

    def create_test_image(self, width=640, height=480, offset_x=0):
        """Create a test image with geometric shapes."""
        # Create a base image
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Add some geometric shapes
        # Circle
        center_x = width // 2 + offset_x
        center_y = height // 2
        cv2.circle(img, (center_x, center_y), 50, (255, 0, 0), -1)

        # Rectangle
        cv2.rectangle(img, (100 + offset_x, 100), (200 + offset_x, 200), (0, 255, 0), -1)

        # Triangle
        points = np.array([[300 + offset_x, 300], [350 + offset_x, 250], [400 + offset_x, 300]], np.int32)
        cv2.fillPoly(img, [points], (0, 0, 255))

        return img

    def create_camera_info(self, width, height, baseline=0.0):
        """Create camera info message."""
        info = CameraInfo()
        info.width = width
        info.height = height

        # Example camera matrix (for 640x480 with 320px focal length)
        info.k = [320.0, 0.0, width/2, 0.0, 320.0, height/2, 0.0, 0.0, 1.0]

        # Example projection matrix (for stereo)
        info.p = [320.0, 0.0, 320.0, -320.0 * baseline, 0.0, 320.0, 240.0, 0.0, 0.0, 0.0, 1.0, 0.0]

        return info

    def publish_test_images(self):
        """Publish synchronized stereo test images."""
        # Create test images (with small offset to simulate stereo)
        left_img = self.create_test_image(offset_x=0)
        right_img = self.create_test_image(offset_x=-20)  # 20px offset for stereo effect

        # Create ROS Image messages
        left_msg = self.bridge.cv2_to_imgmsg(left_img, "bgr8")
        right_msg = self.bridge.cv2_to_imgmsg(right_img, "bgr8")

        # Set headers
        timestamp = self.get_clock().now().to_msg()
        left_msg.header.stamp = timestamp
        left_msg.header.frame_id = 'left_camera_optical_frame'
        right_msg.header.stamp = timestamp
        right_msg.header.frame_id = 'right_camera_optical_frame'

        # Create camera info messages
        left_info = self.create_camera_info(640, 480)
        right_info = self.create_camera_info(640, 480, baseline=0.12)  # 12cm baseline

        left_info.header = left_msg.header
        right_info.header = right_msg.header

        # Publish images and camera info
        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)
        self.left_info_pub.publish(left_info)
        self.right_info_pub.publish(right_info)

        self.frame_id += 1
        if self.frame_id % 100 == 0:
            self.get_logger().info(f'Published test images, frame {self.frame_id}')

def main(args=None):
    rclpy.init(args=args)
    publisher = TestCameraPublisher()

    try:
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        publisher.get_logger().info('Shutting down test publisher...')
    finally:
        publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Update `setup.py` to include the test publisher:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_vision_pipeline'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Isaac AI vision pipeline package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_pipeline = isaac_vision_pipeline.vision_pipeline:main',
            'ai_model_node = isaac_vision_pipeline.ai_model_node:main',
            'test_camera_publisher = isaac_vision_pipeline.test_camera_publisher:main',
        ],
    },
)
```

Rebuild the package:

```bash
cd ~/ros2_lab_ws
colcon build --packages-select isaac_vision_pipeline
source install/setup.bash
```

## Step 9: Run the Complete Vision Pipeline

**Terminal 1 - Start the test camera publisher:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run isaac_vision_pipeline test_camera_publisher
```

**Terminal 2 - Start the vision pipeline:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run isaac_vision_pipeline vision_pipeline
```

**Terminal 3 - Start the AI model node:**
```bash
source ~/ros2_lab_ws/install/setup.bash
ros2 run isaac_vision_pipeline ai_model_node
```

**Terminal 4 - Monitor the results:**
```bash
source ~/ros2_lab_ws/install/setup.bash
# Check published topics
ros2 topic list | grep vision_pipeline

# Echo detection results
ros2 topic echo /vision_pipeline/detections

# Echo feature tracking results
ros2 topic echo /vision_pipeline/features --field data
```

## Step 10: Create a Monitoring Script

Create `~/ros2_lab_ws/src/isaac_vision_pipeline/isaac_vision_pipeline/monitor_pipeline.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from vision_msgs.msg import Detection2DArray
from std_msgs.msg import Header
import time

class VisionPipelineMonitor(Node):
    def __init__(self):
        super().__init__('vision_pipeline_monitor')

        # Initialize statistics
        self.stats = {
            'detection_count': 0,
            'depth_frame_count': 0,
            'feature_frame_count': 0,
            'pointcloud_count': 0,
            'start_time': time.time()
        }

        # Create subscribers to monitor pipeline output
        self.detection_sub = self.create_subscription(
            Detection2DArray,
            '/vision_pipeline/detections',
            self.detection_callback,
            10
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/vision_pipeline/depth_map',
            self.depth_callback,
            10
        )

        self.feature_sub = self.create_subscription(
            Image,
            '/vision_pipeline/features',
            self.feature_callback,
            10
        )

        self.pc_sub = self.create_subscription(
            PointCloud2,
            '/vision_pipeline/pointcloud',
            self.pc_callback,
            10
        )

        # Timer for periodic statistics
        self.stats_timer = self.create_timer(5.0, self.print_statistics)

        self.get_logger().info('Vision Pipeline Monitor initialized')

    def detection_callback(self, msg):
        """Handle detection messages."""
        self.stats['detection_count'] += len(msg.detections)
        self.get_logger().debug(f'Received detection message with {len(msg.detections)} objects')

    def depth_callback(self, msg):
        """Handle depth map messages."""
        self.stats['depth_frame_count'] += 1

    def feature_callback(self, msg):
        """Handle feature tracking messages."""
        self.stats['feature_frame_count'] += 1

    def pc_callback(self, msg):
        """Handle point cloud messages."""
        self.stats['pointcloud_count'] += 1

    def print_statistics(self):
        """Print pipeline statistics."""
        elapsed_time = time.time() - self.stats['start_time']

        detection_rate = self.stats['detection_count'] / elapsed_time if elapsed_time > 0 else 0
        depth_rate = self.stats['depth_frame_count'] / elapsed_time if elapsed_time > 0 else 0
        feature_rate = self.stats['feature_frame_count'] / elapsed_time if elapsed_time > 0 else 0
        pc_rate = self.stats['pointcloud_count'] / elapsed_time if elapsed_time > 0 else 0

        self.get_logger().info(
            f'\n=== Vision Pipeline Statistics ===\n'
            f'Runtime: {elapsed_time:.1f}s\n'
            f'Detections: {self.stats["detection_count"]} (avg: {detection_rate:.2f}/s)\n'
            f'Depth frames: {self.stats["depth_frame_count"]} (avg: {depth_rate:.2f}/s)\n'
            f'Feature frames: {self.stats["feature_frame_count"]} (avg: {feature_rate:.2f}/s)\n'
            f'Point clouds: {self.stats["pointcloud_count"]} (avg: {pc_rate:.2f}/s)\n'
            f'========================='
        )

def main(args=None):
    rclpy.init(args=args)
    monitor = VisionPipelineMonitor()

    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        monitor.get_logger().info('Shutting down monitor...')
    finally:
        monitor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Update `setup.py` to include the monitor:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'isaac_vision_pipeline'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Isaac AI vision pipeline package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_pipeline = isaac_vision_pipeline.vision_pipeline:main',
            'ai_model_node = isaac_vision_pipeline.ai_model_node:main',
            'test_camera_publisher = isaac_vision_pipeline.test_camera_publisher:main',
            'monitor_pipeline = isaac_vision_pipeline.monitor_pipeline:main',
        ],
    },
)
```

Rebuild and test the complete system:

```bash
cd ~/ros2_lab_ws
colcon build --packages-select isaac_vision_pipeline
source install/setup.bash

# In separate terminals:
# Terminal 1: ros2 run isaac_vision_pipeline test_camera_publisher
# Terminal 2: ros2 run isaac_vision_pipeline vision_pipeline
# Terminal 3: ros2 run isaac_vision_pipeline ai_model_node
# Terminal 4: ros2 run isaac_vision_pipeline monitor_pipeline
```

## Lab Questions

1. How does the stereo vision pipeline estimate depth from two camera images?
2. What is the purpose of feature tracking in the vision pipeline?
3. How does the AI model node integrate with traditional computer vision techniques?
4. What are the advantages of using GPU acceleration for computer vision tasks?
5. How could you extend this pipeline to include semantic segmentation?

## Summary

In this lab, you learned how to:
- Create a complete vision pipeline with multiple processing components
- Integrate stereo vision, object detection, and feature tracking
- Implement AI model integration with traditional computer vision
- Use message synchronization for multi-camera systems
- Monitor and analyze pipeline performance

This comprehensive vision pipeline demonstrates the integration of various Isaac computer vision capabilities into a cohesive perception system.