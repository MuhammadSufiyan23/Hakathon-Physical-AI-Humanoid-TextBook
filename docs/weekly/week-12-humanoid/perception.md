---
sidebar_label: 'Humanoid Perception Systems'
title: 'Humanoid Perception Systems'
---

# Humanoid Perception Systems

## Introduction to Humanoid Perception

Humanoid perception systems enable robots to understand their environment and interact with humans effectively. Unlike simple robots, humanoids need to process multiple sensor modalities simultaneously while maintaining balance and performing complex tasks. This requires specialized perception algorithms optimized for real-time processing on humanoid platforms.

## Perception Architecture for Humanoids

### Multi-Sensor Integration Architecture

```
Perception Layer
├── Sensor Abstraction Layer
│   ├── Camera Interface
│   ├── LIDAR Interface
│   ├── IMU Interface
│   ├── Force/Torque Sensors
│   └── Tactile Sensors
├── Preprocessing Layer
│   ├── Image Enhancement
│   ├── Noise Filtering
│   ├── Calibration Correction
│   └── Data Synchronization
├── Processing Layer
│   ├── Object Detection
│   ├── Person Tracking
│   ├── Environment Mapping
│   ├── Human Pose Estimation
│   └── Scene Understanding
└── Interpretation Layer
    ├── Situation Assessment
    ├── Intent Recognition
    ├── Behavior Prediction
    └── Action Planning
```

### Real-Time Processing Requirements

Humanoid robots require perception systems with strict real-time constraints:

- **Balance feedback**: < 5ms latency
- **Obstacle avoidance**: < 20ms latency
- **Person tracking**: < 50ms latency
- **Scene understanding**: < 100ms latency

## Visual Perception Systems

### Camera Systems and Calibration

```python
import cv2
import numpy as np
import math
from scipy.spatial.transform import Rotation as R
import torch
import torchvision.transforms as transforms

class HumanoidCameraSystem:
    def __init__(self, camera_params):
        """
        Initialize humanoid camera system with multiple cameras.

        camera_params: Dictionary with camera calibration parameters
        """
        self.cameras = {}
        self.camera_matrix = {}
        self.distortion_coeffs = {}
        self.extrinsics = {}  # Camera to robot transformations

        for cam_name, params in camera_params.items():
            self.cameras[cam_name] = {
                'resolution': params['resolution'],
                'fov': params['fov'],
                'frame_rate': params['frame_rate']
            }

            # Intrinsic parameters
            self.camera_matrix[cam_name] = np.array(params['intrinsics'])
            self.distortion_coeffs[cam_name] = np.array(params['distortion'])

            # Extrinsics (camera pose relative to robot base)
            self.extrinsics[cam_name] = np.array(params['extrinsics'])

    def undistort_image(self, image, camera_name):
        """
        Undistort image using camera calibration parameters.
        """
        if camera_name not in self.camera_matrix:
            return image

        # Get camera parameters
        K = self.camera_matrix[camera_name]
        dist_coeffs = self.distortion_coeffs[camera_name]

        # Undistort image
        undistorted = cv2.undistort(image, K, dist_coeffs)
        return undistorted

    def rectify_stereo_pair(self, left_img, right_img, left_cam, right_cam):
        """
        Rectify stereo camera pair for dense stereo processing.
        """
        # Get calibration parameters
        K1 = self.camera_matrix[left_cam]
        K2 = self.camera_matrix[right_cam]
        dist1 = self.distortion_coeffs[left_cam]
        dist2 = self.distortion_coeffs[right_cam]

        # Get extrinsics (relative pose between cameras)
        T = self.get_relative_transform(left_cam, right_cam)
        R_rel = T[:3, :3]
        t_rel = T[:3, 3]

        # Compute rectification parameters
        R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
            K1, dist1, K2, dist2,
            (640, 480),  # Image size
            R_rel, t_rel,
            flags=cv2.CALIB_ZERO_DISPARITY,
            alpha=0  # Crop to valid region
        )

        # Compute rectification maps
        map1x, map1y = cv2.initUndistortRectifyMap(K1, dist1, R1, P1, (640, 480), cv2.CV_32FC1)
        map2x, map2y = cv2.initUndistortRectifyMap(K2, dist2, R2, P2, (640, 480), cv2.CV_32FC1)

        # Apply rectification
        rectified_left = cv2.remap(left_img, map1x, map1y, cv2.INTER_LINEAR)
        rectified_right = cv2.remap(right_img, map2x, map2y, cv2.INTER_LINEAR)

        return rectified_left, rectified_right, Q

    def compute_disparity(self, left_img, right_img):
        """
        Compute disparity map from rectified stereo pair.
        """
        # Convert to grayscale
        gray_left = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        gray_right = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

        # Create stereo matcher
        stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=128,  # Must be divisible by 16
            blockSize=5,
            P1=8 * 3 * 5**2,
            P2=32 * 3 * 5**2,
            disp12MaxDiff=1,
            uniquenessRatio=15,
            speckleWindowSize=0,
            speckleRange=2,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )

        # Compute disparity
        disparity = stereo.compute(gray_left, gray_right).astype(np.float32) / 16.0

        return disparity

    def get_relative_transform(self, cam1, cam2):
        """
        Get transformation from camera 1 to camera 2.
        """
        T1 = self.extrinsics[cam1]
        T2 = self.extrinsics[cam2]

        # T2_to_1 = T1^(-1) * T2
        T1_inv = np.linalg.inv(T1)
        T_rel = T1_inv @ T2

        return T_rel

    def project_3d_to_2d(self, point_3d, camera_name):
        """
        Project 3D point to 2D image coordinates.
        """
        K = self.camera_matrix[camera_name]
        dist = self.distortion_coeffs[camera_name]

        # Project point
        point_2d, _ = cv2.projectPoints(
            point_3d.reshape(1, 1, 3),
            np.zeros(3),  # Rotation vector (identity)
            np.zeros(3),  # Translation vector (identity)
            K, dist
        )

        return point_2d[0, 0]

    def triangulate_3d_point(self, left_uv, right_uv, Q_matrix):
        """
        Triangulate 3D point from stereo correspondences.
        """
        # Convert to homogeneous coordinates
        uv_left = np.array([left_uv[0], left_uv[1], 1.0])
        uv_right = np.array([right_uv[0], right_uv[1], 1.0])

        # Triangulate using disparity and Q matrix
        point_3d = cv2.perspectiveTransform(
            np.array([[uv_left]]),
            Q
        )[0, 0]

        return point_3d

class HumanoidVisualPerception:
    def __init__(self, camera_system):
        self.camera_system = camera_system

        # Initialize AI models
        self.object_detector = self.load_object_detection_model()
        self.pose_estimator = self.load_pose_estimation_model()
        self.segmentation_model = self.load_segmentation_model()

        # Processing pipeline
        self.preprocessor = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((416, 416)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_object_detection_model(self):
        """
        Load pre-trained object detection model (e.g., YOLOv5).
        """
        # In practice, this would load a model like YOLO or SSD
        # For this example, we'll return a placeholder
        return None

    def load_pose_estimation_model(self):
        """
        Load human pose estimation model.
        """
        # In practice, this would load models like OpenPose or MediaPipe
        return None

    def load_segmentation_model(self):
        """
        Load semantic segmentation model.
        """
        # In practice, this would load models like DeepLab or Mask R-CNN
        return None

    def process_visual_scene(self, image_data):
        """
        Process visual scene for comprehensive understanding.
        """
        results = {}

        # Object detection
        objects = self.detect_objects(image_data)
        results['objects'] = objects

        # Human detection and pose estimation
        humans = self.detect_and_pose_estimate(image_data)
        results['humans'] = humans

        # Semantic segmentation
        segmentation = self.semantic_segmentation(image_data)
        results['segmentation'] = segmentation

        # Scene understanding
        scene_description = self.understand_scene(objects, humans, segmentation)
        results['scene_description'] = scene_description

        return results

    def detect_objects(self, image):
        """
        Detect objects in the image using deep learning model.
        """
        # Preprocess image
        input_tensor = self.preprocessor(image).unsqueeze(0)

        # Run inference (placeholder - would use actual model)
        if self.object_detector is not None:
            with torch.no_grad():
                detections = self.object_detector(input_tensor)
        else:
            # Simulate detections
            detections = self.simulate_object_detections(image)

        # Process detections
        objects = []
        for det in detections:
            if det['confidence'] > 0.5:  # Confidence threshold
                objects.append({
                    'class': det['class'],
                    'confidence': det['confidence'],
                    'bbox': det['bbox'],  # [x1, y1, x2, y2]
                    'center_2d': [(det['bbox'][0] + det['bbox'][2])/2, (det['bbox'][1] + det['bbox'][3])/2]
                })

        return objects

    def detect_and_pose_estimate(self, image):
        """
        Detect humans and estimate their pose.
        """
        # This would typically use MediaPipe, OpenPose, or similar
        # For this example, we'll simulate the functionality

        # Detect human figures
        humans = []

        # Simulate human detection and pose estimation
        for i in range(2):  # Simulate detecting 2 humans
            human = {
                'bbox': [50 + i*100, 100, 150 + i*100, 300],  # [x1, y1, x2, y2]
                'pose_keypoints': self.simulate_pose_keypoints(i),  # 17 keypoints (COCO format)
                'pose_confidence': 0.8,
                'gaze_direction': [0.1, -0.2, 0.95],  # Normalized vector
                'gaze_confidence': 0.7
            }
            humans.append(human)

        return humans

    def semantic_segmentation(self, image):
        """
        Perform semantic segmentation on the image.
        """
        # This would use models like DeepLab, UNet, etc.
        # For this example, we'll simulate segmentation

        height, width = image.shape[:2]
        segmentation_mask = np.zeros((height, width), dtype=np.uint8)

        # Simulate segmentation (in reality, this would be from a neural network)
        # For example, create some segmented regions
        for i in range(5):  # 5 different object classes
            # Create random region
            center_x = np.random.randint(0, width)
            center_y = np.random.randint(0, height)
            radius = np.random.randint(20, 80)

            y, x = np.ogrid[:height, :width]
            mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
            segmentation_mask[mask] = i + 1  # Class ID

        return segmentation_mask

    def understand_scene(self, objects, humans, segmentation):
        """
        Perform high-level scene understanding.
        """
        scene_description = {
            'objects_count': len(objects),
            'humans_count': len(humans),
            'social_interactions': [],
            'spatial_relationships': [],
            'activity_recognition': [],
            'intention_prediction': []
        }

        # Analyze spatial relationships
        for obj in objects:
            for human in humans:
                spatial_rel = self.analyze_spatial_relationship(obj, human)
                scene_description['spatial_relationships'].append(spatial_rel)

        # Detect social interactions
        if len(humans) > 1:
            interactions = self.detect_social_interactions(humans)
            scene_description['social_interactions'] = interactions

        # Recognize activities
        for human in humans:
            activity = self.recognize_human_activity(human)
            scene_description['activity_recognition'].append(activity)

        # Predict intentions
        for human in humans:
            intention = self.predict_human_intention(human)
            scene_description['intention_prediction'].append(intention)

        return scene_description

    def analyze_spatial_relationship(self, object_info, human_info):
        """
        Analyze spatial relationship between object and human.
        """
        # Calculate 2D distance in image space
        obj_center = np.array(object_info['center_2d'])
        human_center = np.array([
            (human_info['bbox'][0] + human_info['bbox'][2]) / 2,
            (human_info['bbox'][1] + human_info['bbox'][3]) / 2
        ])

        distance_2d = np.linalg.norm(obj_center - human_center)

        # Determine relationship based on distance and context
        if distance_2d < 50:  # Pixels
            relationship = 'close_interaction'
        elif distance_2d < 150:
            relationship = 'proximity'
        else:
            relationship = 'distant'

        return {
            'object': object_info['class'],
            'human': 'person',
            'relationship': relationship,
            'distance_2d': distance_2d
        }

    def detect_social_interactions(self, humans):
        """
        Detect social interactions between multiple humans.
        """
        interactions = []

        for i in range(len(humans)):
            for j in range(i + 1, len(humans)):
                human1 = humans[i]
                human2 = humans[j]

                # Calculate distance between humans
                center1 = np.array([
                    (human1['bbox'][0] + human1['bbox'][2]) / 2,
                    (human1['bbox'][1] + human1['bbox'][3]) / 2
                ])
                center2 = np.array([
                    (human2['bbox'][0] + human2['bbox'][2]) / 2,
                    (human2['bbox'][1] + human2['bbox'][3]) / 2
                ])

                distance = np.linalg.norm(center1 - center2)

                # Check if humans are facing each other
                gaze1 = np.array(human1['gaze_direction'])
                gaze2 = np.array(human2['gaze_direction'])

                # Vector from human1 to human2
                vector_1_to_2 = center2 - center1
                vector_2_to_1 = center1 - center2

                # Check if looking toward each other
                looking_at_each_other = (
                    np.dot(gaze1[:2], vector_1_to_2) > 0 and
                    np.dot(gaze2[:2], vector_2_to_1) > 0
                )

                if distance < 200 and looking_at_each_other:  # Within 200 pixels and facing each other
                    interactions.append({
                        'humans': [i, j],
                        'type': 'conversation',
                        'confidence': 0.8
                    })
                elif distance < 100:  # Close proximity
                    interactions.append({
                        'humans': [i, j],
                        'type': 'proximity_interaction',
                        'confidence': 0.6
                    })

        return interactions

    def recognize_human_activity(self, human_info):
        """
        Recognize human activity from pose and context.
        """
        # Extract pose keypoints
        keypoints = human_info['pose_keypoints']

        # Simple activity recognition based on pose
        # In practice, this would use LSTM or Transformer models
        if len(keypoints) >= 17:
            # Extract key body parts
            nose = keypoints[0]  # Nose
            left_shoulder = keypoints[5]
            right_shoulder = keypoints[6]
            left_elbow = keypoints[7]
            right_elbow = keypoints[8]
            left_wrist = keypoints[9]
            right_wrist = keypoints[10]
            left_hip = keypoints[11]
            right_hip = keypoints[12]
            left_knee = keypoints[13]
            right_knee = keypoints[14]
            left_ankle = keypoints[15]
            right_ankle = keypoints[16]

            # Activity recognition logic
            if abs(left_wrist[1] - left_shoulder[1]) < 20:  # Left hand near shoulder
                if abs(right_wrist[1] - right_shoulder[1]) < 20:  # Both hands near shoulders
                    activity = 'resting'
                else:
                    activity = 'raising_left_arm'
            elif abs(right_wrist[1] - right_shoulder[1]) < 20:  # Right hand near shoulder
                activity = 'raising_right_arm'
            elif abs(left_knee[1] - left_hip[1]) < 30:  # Left knee bent
                if abs(right_knee[1] - right_hip[1]) < 30:  # Both knees bent
                    activity = 'sitting'
                else:
                    activity = 'stepping_left'
            elif abs(right_knee[1] - right_hip[1]) < 30:  # Right knee bent
                activity = 'stepping_right'
            else:
                activity = 'standing'

            return {
                'activity': activity,
                'confidence': 0.7,
                'keypoints_used': [0, 5, 6, 9, 10, 11, 12, 13, 14]  # Relevant keypoints
            }

        return {'activity': 'unknown', 'confidence': 0.1}

    def predict_human_intention(self, human_info):
        """
        Predict human intention based on pose and activity.
        """
        # Use pose and activity to predict intention
        activity = self.recognize_human_activity(human_info)

        if activity['activity'] == 'raising_right_arm':
            intention = 'waving'  # Greeting or trying to get attention
        elif activity['activity'] == 'raising_left_arm':
            intention = 'signaling'  # Possibly signaling for help
        elif activity['activity'] == 'sitting':
            intention = 'resting'  # Just resting
        elif activity['activity'] == 'stepping_left':
            intention = 'moving_left'  # Planning to move left
        elif activity['activity'] == 'stepping_right':
            intention = 'moving_right'  # Planning to move right
        else:
            intention = 'neutral'  # Uncertain intention

        return {
            'predicted_intention': intention,
            'confidence': activity['confidence'] * 0.8,  # Scale by activity confidence
            'based_on': activity['activity']
        }

    def simulate_object_detections(self, image):
        """
        Simulate object detections for demonstration purposes.
        """
        # In a real implementation, this would run a trained object detection model
        # For this example, we'll create simulated detections

        height, width = image.shape[:2]
        detections = []

        # Simulate detecting some common objects
        common_objects = ['person', 'chair', 'table', 'bottle', 'cup', 'laptop', 'phone']

        for i in range(5):  # Create 5 simulated detections
            obj_class = np.random.choice(common_objects)
            x1 = np.random.randint(0, width - 100)
            y1 = np.random.randint(0, height - 100)
            x2 = x1 + np.random.randint(50, 150)
            y2 = y1 + np.random.randint(50, 150)

            confidence = 0.5 + np.random.random() * 0.4  # 0.5 to 0.9 confidence

            detections.append({
                'class': obj_class,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2]
            })

        return detections

    def simulate_pose_keypoints(self, person_id):
        """
        Simulate pose keypoints for demonstration.
        """
        # In COCO format (17 keypoints)
        # [nose, left_eye, right_eye, left_ear, right_ear,
        #  left_shoulder, right_shoulder, left_elbow, right_elbow,
        #  left_wrist, right_wrist, left_hip, right_hip,
        #  left_knee, right_knee, left_ankle, right_ankle]

        base_x = 100 + person_id * 200
        base_y = 100

        keypoints = [
            [base_x, base_y],           # nose
            [base_x - 10, base_y - 10], # left_eye
            [base_x + 10, base_y - 10], # right_eye
            [base_x - 20, base_y],      # left_ear
            [base_x + 20, base_y],      # right_ear
            [base_x - 30, base_y + 20], # left_shoulder
            [base_x + 30, base_y + 20], # right_shoulder
            [base_x - 50, base_y + 60], # left_elbow
            [base_x + 50, base_y + 60], # right_elbow
            [base_x - 70, base_y + 100], # left_wrist
            [base_x + 70, base_y + 100], # right_wrist
            [base_x - 20, base_y + 80],  # left_hip
            [base_x + 20, base_y + 80],  # right_hip
            [base_x - 20, base_y + 140], # left_knee
            [base_x + 20, base_y + 140], # right_knee
            [base_x - 20, base_y + 200], # left_ankle
            [base_x + 20, base_y + 200]  # right_ankle
        ]

        # Add confidence values
        keypoint_data = []
        for kp in keypoints:
            keypoint_data.extend([kp[0], kp[1], 0.8])  # x, y, confidence

        return np.array(keypoint_data).reshape(-1, 3)  # Shape: (17, 3)
```

## Depth Perception and 3D Understanding

### Point Cloud Processing

```python
import open3d as o3d
from sklearn.cluster import DBSCAN
import pcl  # Python-PCL

class HumanoidDepthPerception:
    def __init__(self):
        # Initialize point cloud processing
        self.segmentation_algorithm = 'dbscan'  # Clustering-based segmentation
        self.min_cluster_size = 100
        self.max_cluster_size = 50000

    def process_pointcloud(self, pointcloud_data):
        """
        Process 3D point cloud data for environment understanding.
        """
        # Convert to Open3D format
        pcd = self.convert_to_open3d(pointcloud_data)

        # Filter point cloud
        filtered_pcd = self.filter_pointcloud(pcd)

        # Segment objects
        segmented_objects = self.segment_objects(filtered_pcd)

        # Analyze each segment
        object_analysis = []
        for obj_pcd in segmented_objects:
            analysis = self.analyze_object_segment(obj_pcd)
            object_analysis.append(analysis)

        return {
            'objects': object_analysis,
            'filtered_pointcloud': filtered_pcd,
            'ground_plane': self.extract_ground_plane(filtered_pcd)
        }

    def convert_to_open3d(self, pointcloud_msg):
        """
        Convert ROS PointCloud2 message to Open3D point cloud.
        """
        # This would use sensor_msgs_py.point_cloud2 to convert
        # For this example, we'll assume input is already in Open3D format
        return pointcloud_msg

    def filter_pointcloud(self, pointcloud, voxel_size=0.01):
        """
        Filter point cloud using voxel grid downsampling.
        """
        # Downsample using voxel grid
        downsampled = pointcloud.voxel_down_sample(voxel_size=voxel_size)

        # Remove statistical outliers
        cl, ind = downsampled.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
        filtered = downsampled.select_by_index(ind)

        return filtered

    def segment_objects(self, pointcloud):
        """
        Segment objects using clustering algorithm.
        """
        # Convert to numpy array
        points = np.asarray(pointcloud.points)

        # Apply DBSCAN clustering
        clustering = DBSCAN(
            eps=0.05,  # 5cm distance threshold
            min_samples=50,  # Minimum points per cluster
            n_jobs=-1  # Use all cores
        )

        labels = clustering.fit_predict(points)

        # Separate clusters
        objects = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:  # Noise points
                continue

            # Get points belonging to this cluster
            cluster_mask = labels == label
            cluster_points = points[cluster_mask]

            if len(cluster_points) < self.min_cluster_size:
                continue  # Skip small clusters

            # Create point cloud from cluster
            cluster_pcd = o3d.geometry.PointCloud()
            cluster_pcd.points = o3d.utility.Vector3dVector(cluster_points)

            objects.append(cluster_pcd)

        return objects

    def analyze_object_segment(self, pointcloud_segment):
        """
        Analyze a segmented object to extract features.
        """
        points = np.asarray(pointcloud_segment.points)

        # Calculate bounding box
        bbox = pointcloud_segment.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent()

        # Calculate convex hull for shape analysis
        hull, _ = pointcloud_segment.compute_convex_hull()

        # Calculate surface normals
        pointcloud_segment.estimate_normals()
        normals = np.asarray(pointcloud_segment.normals)

        # Analyze shape features
        shape_features = self.calculate_shape_features(points, hull, normals)

        # Calculate position relative to robot
        # This would use robot's coordinate system
        world_position = center  # Simplified - would transform to world coordinates

        return {
            'center': center.tolist(),
            'extent': extent.tolist(),
            'points_count': len(points),
            'convex_hull_volume': hull.get_volume(),
            'bounding_box': {
                'center': center.tolist(),
                'extent': extent.tolist(),
                'min_bound': bbox.min_bound.tolist(),
                'max_bound': bbox.max_bound.tolist()
            },
            'shape_features': shape_features,
            'world_position': world_position.tolist(),
            'is_table': self.is_flat_surface(extent, normals),
            'is_person': self.is_person_shape(extent, len(points))
        }

    def calculate_shape_features(self, points, hull, normals):
        """
        Calculate shape features for object classification.
        """
        features = {}

        # Compactness (ratio of volume to surface area)
        if len(points) > 0:
            # Calculate volume using convex hull
            volume = hull.get_volume()
            surface_area = hull.get_surface_area() if hasattr(hull, 'get_surface_area') else 0
            compactness = volume / (surface_area + 1e-6)  # Add small value to avoid division by zero
            features['compactness'] = compactness

        # Planarity (how flat the surface is)
        if len(normals) > 0:
            # Calculate variance of normals to determine planarity
            normal_variance = np.var(normals, axis=0)
            planarity = 1.0 / (1.0 + np.sum(normal_variance))
            features['planarity'] = planarity

        # Symmetry analysis
        centroid = np.mean(points, axis=0)
        centered_points = points - centroid

        # Calculate principal components
        cov_matrix = np.cov(centered_points.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

        # Sort by eigenvalue magnitude
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        features['eigenvalues'] = eigenvalues.tolist()
        features['eigenvectors'] = eigenvectors.tolist()

        # Shape descriptors
        if len(eigenvalues) >= 3:
            ev1, ev2, ev3 = eigenvalues
            features['elongation'] = ev2 / (ev1 + 1e-6)
            features['flatness'] = ev3 / (ev1 + 1e-6)
            features['linearity'] = (ev1 - ev2) / (ev1 + 1e-6)

        return features

    def is_flat_surface(self, extent, normals):
        """
        Determine if the object is a flat surface (like a table).
        """
        # Check if Z extent is much smaller than X/Y extents
        if extent[2] < 0.05 and extent[0] > 0.3 and extent[1] > 0.3:
            # Check if normals are mostly vertical
            if len(normals) > 0:
                z_normals = np.abs(normals[:, 2])  # Z component of normals
                vertical_normal_ratio = np.sum(z_normals > 0.8) / len(normals)
                return vertical_normal_ratio > 0.7  # 70% of normals are vertical

        return False

    def is_person_shape(self, extent, point_count):
        """
        Determine if the object has human-like proportions.
        """
        height = extent[2]
        width = max(extent[0], extent[1])

        # Check if height/width ratio is reasonable for a person
        if 1.5 < height/width < 5.0 and 500 < point_count < 5000:
            return True

        return False

    def extract_ground_plane(self, pointcloud):
        """
        Extract ground plane using RANSAC.
        """
        plane_model, inliers = pointcloud.segment_plane(
            distance_threshold=0.02,
            ransac_n=3,
            num_iterations=1000
        )

        # Extract ground points
        ground_cloud = pointcloud.select_by_index(inliers)
        non_ground_cloud = pointcloud.select_by_index(inliers, invert=True)

        return {
            'plane_model': plane_model.tolist(),
            'ground_points': np.asarray(ground_cloud.points).tolist(),
            'non_ground_points': np.asarray(non_ground_cloud.points).tolist()
        }

    def track_objects_over_time(self, current_objects, previous_objects):
        """
        Track objects across time frames using point cloud registration.
        """
        tracked_objects = []

        for current_obj in current_objects:
            best_match = None
            best_distance = float('inf')

            for prev_obj in previous_objects:
                # Calculate distance between object centers
                dist = np.linalg.norm(
                    np.array(current_obj['center']) - np.array(prev_obj['center'])
                )

                if dist < best_distance and dist < 0.3:  # Within 30cm threshold
                    best_distance = dist
                    best_match = prev_obj

            if best_match:
                # Update tracked object
                tracked_obj = best_match.copy()
                tracked_obj['position'] = current_obj['center']
                tracked_obj['velocity'] = self.calculate_velocity(
                    current_obj['center'], best_match['position'], delta_time=0.1
                )
                tracked_obj['updated'] = True
            else:
                # New object
                tracked_obj = current_obj.copy()
                tracked_obj['velocity'] = [0, 0, 0]
                tracked_obj['updated'] = False

            tracked_objects.append(tracked_obj)

        return tracked_objects

    def calculate_velocity(self, current_pos, previous_pos, delta_time):
        """
        Calculate velocity from position changes.
        """
        displacement = np.array(current_pos) - np.array(previous_pos)
        velocity = displacement / delta_time
        return velocity.tolist()
```

## Tactile and Proprioceptive Perception

### Force/Torque Sensing

```python
class HumanoidTactilePerception:
    def __init__(self):
        self.force_thresholds = {
            'grip': 5.0,      # Newtons for gripper
            'foot': 10.0,     # Newtons for foot contact
            'hand': 2.0,      # Newtons for hand contact
            'torso': 20.0     # Newtons for torso contact
        }

        self.torque_limits = {
            'arm': 50.0,      # Nm for arm joints
            'leg': 100.0,     # Nm for leg joints
            'torso': 80.0     # Nm for torso joints
        }

    def process_force_torque_data(self, sensor_data):
        """
        Process force/torque sensor data for contact detection and manipulation.
        """
        analysis_results = {}

        # Process foot force/torque sensors
        for foot_side in ['left', 'right']:
            foot_data = sensor_data.get(f'{foot_side}_foot_force_torque', {})
            analysis_results[f'{foot_side}_foot_analysis'] = self.analyze_foot_contact(foot_data)

        # Process hand force/torque sensors
        for hand_side in ['left', 'right']:
            hand_data = sensor_data.get(f'{hand_side}_hand_force_torque', {})
            analysis_results[f'{hand_side}_hand_analysis'] = self.analyze_hand_contact(hand_data)

        # Process joint torque sensors
        joint_torques = sensor_data.get('joint_torques', [])
        analysis_results['joint_analysis'] = self.analyze_joint_torques(joint_torques)

        return analysis_results

    def analyze_foot_contact(self, ft_data):
        """
        Analyze foot force/torque data for contact state and balance.
        """
        if not ft_data:
            return {'contact': False, 'pressure_distribution': [0, 0, 0, 0]}

        # Extract force and torque components
        force = np.array(ft_data.get('force', [0, 0, 0]))
        torque = np.array(ft_data.get('torque', [0, 0, 0]))

        # Calculate total force magnitude
        total_force = np.linalg.norm(force)

        # Determine contact state
        contact = total_force > self.force_thresholds['foot'] * 0.5

        # Calculate center of pressure (CoP)
        # CoP = (M_y/F_z, -M_x/F_z) where M is moments and F_z is vertical force
        fz = force[2] if abs(force[2]) > 0.1 else 0.1  # Avoid division by zero
        cop_x = torque[1] / fz
        cop_y = -torque[0] / fz

        # Pressure distribution (simplified - real sensors have 4 corners)
        pressure_distribution = [
            force[0] * 0.25 + torque[1] * 0.1,  # Front-left
            force[0] * 0.25 - torque[1] * 0.1,  # Front-right
            -force[0] * 0.25 + torque[1] * 0.1, # Back-left
            -force[0] * 0.25 - torque[1] * 0.1  # Back-right
        ]

        return {
            'contact': contact,
            'total_force': total_force,
            'center_of_pressure': [cop_x, cop_y],
            'pressure_distribution': pressure_distribution,
            'moments': torque.tolist()
        }

    def analyze_hand_contact(self, ft_data):
        """
        Analyze hand force/torque data for manipulation.
        """
        if not ft_data:
            return {'contact': False, 'grasp_quality': 0.0}

        force = np.array(ft_data.get('force', [0, 0, 0]))
        torque = np.array(ft_data.get('torque', [0, 0, 0]))

        total_force = np.linalg.norm(force)
        contact = total_force > self.force_thresholds['hand']

        # Calculate grasp quality based on force distribution
        grasp_quality = self.calculate_grasp_quality(force, torque)

        return {
            'contact': contact,
            'total_force': total_force,
            'grasp_quality': grasp_quality,
            'force_vector': force.tolist(),
            'torque_vector': torque.tolist()
        }

    def calculate_grasp_quality(self, force, torque):
        """
        Calculate grasp quality metric.
        """
        # Simple grasp quality based on force alignment
        # In practice, this would use more sophisticated metrics like grasp wrench space
        force_magnitude = np.linalg.norm(force)
        torque_magnitude = np.linalg.norm(torque)

        # Normalize and combine
        force_quality = min(1.0, force_magnitude / 20.0)  # Normalize to 0-1 based on 20N max
        torque_quality = 1.0 - min(1.0, torque_magnitude / 5.0)  # Torque should be low for good grasp

        grasp_quality = 0.7 * force_quality + 0.3 * torque_quality
        return grasp_quality

    def analyze_joint_torques(self, joint_torques):
        """
        Analyze joint torques for contact detection and safety.
        """
        analysis = {
            'contact_events': [],
            'safety_violations': [],
            'joint_loads': []
        }

        for i, torque in enumerate(joint_torques):
            joint_load = abs(torque)
            joint_analysis = {
                'joint_index': i,
                'torque': torque,
                'load_percentage': joint_load / self.torque_limits.get('arm', 50.0)  # Default to arm limit
            }

            # Check for contact events (sudden torque changes)
            if joint_load > 0.8 * self.torque_limits.get('arm', 50.0):
                contact_event = {
                    'joint': i,
                    'type': 'high_torque_contact',
                    'magnitude': joint_load,
                    'timestamp': self.get_current_time()
                }
                analysis['contact_events'].append(contact_event)

            # Check for safety violations
            if joint_load > self.torque_limits.get('arm', 50.0):
                safety_violation = {
                    'joint': i,
                    'type': 'torque_limit_exceeded',
                    'current_value': joint_load,
                    'limit': self.torque_limits.get('arm', 50.0)
                }
                analysis['safety_violations'].append(safety_violation)

            analysis['joint_loads'].append(joint_analysis)

        return analysis

    def detect_contact_events(self, current_data, previous_data):
        """
        Detect contact events by analyzing changes in sensor data.
        """
        contact_events = []

        # Compare current and previous force/torque readings
        for sensor_type in ['left_foot', 'right_foot', 'left_hand', 'right_hand']:
            current_ft = current_data.get(f'{sensor_type}_force_torque', {})
            previous_ft = previous_data.get(f'{sensor_type}_force_torque', {})

            if current_ft and previous_ft:
                current_force = np.array(current_ft.get('force', [0, 0, 0]))
                previous_force = np.array(previous_ft.get('force', [0, 0, 0]))

                force_change = np.linalg.norm(current_force - previous_force)

                # Detect contact onset
                if force_change > 10.0 and np.linalg.norm(current_force) > 5.0:
                    contact_event = {
                        'sensor': sensor_type,
                        'type': 'contact_onset',
                        'force_change': force_change,
                        'timestamp': self.get_current_time()
                    }
                    contact_events.append(contact_event)

                # Detect contact removal
                elif force_change > 10.0 and np.linalg.norm(current_force) < 2.0:
                    contact_event = {
                        'sensor': sensor_type,
                        'type': 'contact_release',
                        'force_change': force_change,
                        'timestamp': self.get_current_time()
                    }
                    contact_events.append(contact_event)

        return contact_events

class HumanoidProprioceptivePerception:
    def __init__(self):
        self.joint_position_thresholds = {
            'arm': 0.1,    # Radians for position deviation
            'leg': 0.2,    # Radians for position deviation
            'torso': 0.05  # Radians for position deviation
        }

        self.joint_velocity_thresholds = {
            'arm': 2.0,    # Rad/s for velocity
            'leg': 3.0,    # Rad/s for velocity
            'torso': 1.0   # Rad/s for velocity
        }

    def process_proprioceptive_data(self, joint_data):
        """
        Process proprioceptive data from joint sensors.
        """
        results = {}

        # Analyze joint positions
        results['position_analysis'] = self.analyze_joint_positions(joint_data)

        # Analyze joint velocities
        results['velocity_analysis'] = self.analyze_joint_velocities(joint_data)

        # Analyze joint accelerations
        results['acceleration_analysis'] = self.analyze_joint_accelerations(joint_data)

        # Detect anomalies
        results['anomalies'] = self.detect_joint_anomalies(joint_data)

        return results

    def analyze_joint_positions(self, joint_data):
        """
        Analyze joint position data.
        """
        position_analysis = []

        current_positions = joint_data.get('positions', [])
        desired_positions = joint_data.get('desired_positions', [])

        for i, (current_pos, desired_pos) in enumerate(zip(current_positions, desired_positions)):
            position_error = abs(current_pos - desired_pos)

            analysis = {
                'joint_index': i,
                'current_position': current_pos,
                'desired_position': desired_pos,
                'position_error': position_error,
                'within_tolerance': position_error < self.joint_position_thresholds.get('arm', 0.1)
            }

            position_analysis.append(analysis)

        return position_analysis

    def analyze_joint_velocities(self, joint_data):
        """
        Analyze joint velocity data.
        """
        velocity_analysis = []

        current_velocities = joint_data.get('velocities', [])

        for i, velocity in enumerate(current_velocities):
            velocity_magnitude = abs(velocity)

            analysis = {
                'joint_index': i,
                'velocity': velocity,
                'magnitude': velocity_magnitude,
                'within_limits': velocity_magnitude < self.joint_velocity_thresholds.get('arm', 2.0)
            }

            velocity_analysis.append(analysis)

        return velocity_analysis

    def analyze_joint_accelerations(self, joint_data):
        """
        Analyze joint acceleration data (calculated from velocity changes).
        """
        acceleration_analysis = []

        current_velocities = joint_data.get('velocities', [])
        previous_velocities = getattr(self, 'previous_velocities', [0] * len(current_velocities))

        dt = 0.01  # Assuming 100Hz control rate

        for i, (current_vel, prev_vel) in enumerate(zip(current_velocities, previous_velocities)):
            acceleration = (current_vel - prev_vel) / dt if dt > 0 else 0

            analysis = {
                'joint_index': i,
                'acceleration': acceleration,
                'magnitude': abs(acceleration)
            }

            acceleration_analysis.append(analysis)

        # Store for next iteration
        self.previous_velocities = current_velocities

        return acceleration_analysis

    def detect_joint_anomalies(self, joint_data):
        """
        Detect anomalies in joint behavior.
        """
        anomalies = []

        # Check for joint limit violations
        positions = joint_data.get('positions', [])
        joint_limits = joint_data.get('joint_limits', [])

        for i, (pos, limits) in enumerate(zip(positions, joint_limits)):
            if pos < limits[0] or pos > limits[1]:  # Outside joint limits
                anomaly = {
                    'type': 'joint_limit_violation',
                    'joint': i,
                    'position': pos,
                    'limits': limits,
                    'timestamp': self.get_current_time()
                }
                anomalies.append(anomaly)

        # Check for excessive joint velocities
        velocities = joint_data.get('velocities', [])
        for i, vel in enumerate(velocities):
            if abs(vel) > self.joint_velocity_thresholds.get('arm', 2.0) * 1.5:  # 150% of threshold
                anomaly = {
                    'type': 'excessive_velocity',
                    'joint': i,
                    'velocity': vel,
                    'threshold': self.joint_velocity_thresholds.get('arm', 2.0),
                    'timestamp': self.get_current_time()
                }
                anomalies.append(anomaly)

        # Check for sudden position changes (possible collision)
        positions = joint_data.get('positions', [])
        previous_positions = getattr(self, 'previous_positions', positions)

        for i, (pos, prev_pos) in enumerate(zip(positions, previous_positions)):
            pos_change = abs(pos - prev_pos)
            if pos_change > 0.5:  # Sudden change of 0.5 radians
                anomaly = {
                    'type': 'sudden_position_change',
                    'joint': i,
                    'change': pos_change,
                    'timestamp': self.get_current_time()
                }
                anomalies.append(anomaly)

        # Update previous positions
        self.previous_positions = positions

        return anomalies

    def calculate_balance_metrics(self, proprioceptive_data, force_data):
        """
        Calculate balance metrics from proprioceptive and force data.
        """
        balance_metrics = {}

        # Calculate joint configuration entropy (measure of configuration complexity)
        joint_positions = proprioceptive_data.get('positions', [])
        if joint_positions:
            # Simplified entropy calculation
            abs_positions = [abs(pos) for pos in joint_positions]
            avg_abs_position = sum(abs_positions) / len(abs_positions)
            balance_metrics['configuration_entropy'] = avg_abs_position

        # Calculate joint effort (sum of absolute torques)
        joint_torques = proprioceptive_data.get('torques', [])
        if joint_torques:
            total_effort = sum(abs(torque) for torque in joint_torques)
            balance_metrics['total_joint_effort'] = total_effort

        # Calculate force distribution symmetry (between left and right sides)
        left_foot_force = force_data.get('left_foot_force', [0, 0, 0])
        right_foot_force = force_data.get('right_foot_force', [0, 0, 0])

        left_vertical_force = abs(left_foot_force[2])
        right_vertical_force = abs(right_foot_force[2])

        if left_vertical_force + right_vertical_force > 0:
            symmetry = abs(left_vertical_force - right_vertical_force) / (left_vertical_force + right_vertical_force)
            balance_metrics['weight_symmetry'] = 1.0 - symmetry  # Higher is more symmetric

        return balance_metrics
```

## Sensor Fusion and State Estimation

### Extended Kalman Filter for State Estimation

```python
import numpy as np
from scipy.linalg import block_diag

class HumanoidStateEstimator:
    def __init__(self):
        # State vector: [com_x, com_y, com_z, com_dx, com_dy, com_dz,
        #                orientation_w, orientation_x, orientation_y, orientation_z,
        #                angular_velocity_x, angular_velocity_y, angular_velocity_z]
        self.state_dim = 13
        self.state = np.zeros(self.state_dim)
        self.covariance = np.eye(self.state_dim) * 100  # Initial uncertainty

        # Process noise
        self.process_noise = np.eye(self.state_dim) * 0.1

        # Measurement noise for different sensors
        self.measurement_noise = {
            'imu': np.diag([0.01, 0.01, 0.01, 0.001, 0.001, 0.001]),  # [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]
            'kinect': np.diag([0.02, 0.02, 0.02, 0.01, 0.01, 0.01]),  # [pos_x, pos_y, pos_z, orient_x, orient_y, orient_z]
            'force_plate': np.diag([5.0, 5.0, 5.0])  # [force_x, force_y, force_z]
        }

    def predict(self, control_input, dt):
        """
        Prediction step of EKF.

        Args:
            control_input: Control commands affecting the system
            dt: Time step
        """
        # State transition model (simplified - in reality would be more complex)
        # For this example, we'll use a simple constant velocity model
        F = np.eye(self.state_dim)

        # Position integration from velocity
        F[0:3, 3:6] = np.eye(3) * dt  # Position from velocity

        # Orientation integration from angular velocity
        # This is simplified - real implementation would use quaternion integration
        F[6:9, 9:12] = np.eye(3) * dt  # Orientation from angular velocity

        # Update state prediction
        self.state = F @ self.state

        # Update covariance prediction
        self.covariance = F @ self.covariance @ F.T + self.process_noise * dt

    def update_imu(self, imu_measurement):
        """
        Update state estimate using IMU measurement.

        Args:
            imu_measurement: [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]
        """
        # Measurement model: extract acceleration and angular velocity from state
        H = np.zeros((6, self.state_dim))
        H[0:3, 0:3] = np.eye(3) / dt  # Acceleration from position (finite difference approximation)
        H[3:6, 9:12] = np.eye(3)  # Angular velocity directly observable

        # Innovation
        innovation = np.array(imu_measurement) - H @ self.state

        # Innovation covariance
        innovation_cov = H @ self.covariance @ H.T + self.measurement_noise['imu']

        # Kalman gain
        kalman_gain = self.covariance @ H.T @ np.linalg.inv(innovation_cov)

        # Update state
        self.state = self.state + kalman_gain @ innovation

        # Update covariance
        self.covariance = (np.eye(self.state_dim) - kalman_gain @ H) @ self.covariance

    def update_kinect(self, kinect_measurement):
        """
        Update state estimate using Kinect/pose measurement.

        Args:
            kinect_measurement: [pos_x, pos_y, pos_z, orient_x, orient_y, orient_z, orient_w]
        """
        # Measurement model: extract position and orientation from state
        H = np.zeros((7, self.state_dim))
        H[0:3, 0:3] = np.eye(3)  # Position is directly observable
        H[3:7, 6:10] = np.eye(4)  # Orientation is directly observable

        # Innovation
        innovation = np.array(kinect_measurement) - H @ self.state

        # Normalize quaternion innovation
        if len(innovation) >= 7:
            # Ensure quaternion is normalized
            quat_measured = kinect_measurement[3:7] / np.linalg.norm(kinect_measurement[3:7])
            quat_predicted = self.state[6:10] / np.linalg.norm(self.state[6:10])

            # Calculate quaternion error
            quat_error = self.quaternion_error(quat_measured, quat_predicted)
            innovation[3:7] = quat_error[1:]  # Use vector part of error quaternion

        # Innovation covariance
        innovation_cov = H @ self.covariance @ H.T + self.measurement_noise['kinect']

        # Kalman gain
        kalman_gain = self.covariance @ H.T @ np.linalg.inv(innovation_cov)

        # Update state
        self.state = self.state + kalman_gain @ innovation

        # Update covariance
        self.covariance = (np.eye(self.state_dim) - kalman_gain @ H) @ self.covariance

    def update_force_plate(self, force_measurement):
        """
        Update state estimate using force plate measurement.

        Args:
            force_measurement: [force_x, force_y, force_z]
        """
        # For this simplified model, we'll use a direct mapping
        # In reality, force measurements would be used in a more complex way
        # to estimate contact forces and CoP
        pass

    def quaternion_error(self, q1, q2):
        """
        Calculate error quaternion between two orientations.
        """
        # q_error = q1 * q2^(-1) where q2^(-1) is conjugate of q2
        q2_conj = np.array([q2[0], -q2[1], -q2[2], -q2[3]])  # Conjugate
        q_error = self.multiply_quaternions(q1, q2_conj)
        return q_error

    def multiply_quaternions(self, q1, q2):
        """
        Multiply two quaternions: q1 * q2.
        """
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2

        return np.array([w, x, y, z])

    def get_state_estimate(self):
        """
        Get current state estimate.
        """
        return {
            'com_position': self.state[0:3],
            'com_velocity': self.state[3:6],
            'orientation': self.state[6:10],
            'angular_velocity': self.state[10:13],
            'covariance': self.covariance
        }

    def reset_state(self):
        """
        Reset state estimator to initial values.
        """
        self.state = np.zeros(self.state_dim)
        self.covariance = np.eye(self.state_dim) * 100

class MultiSensorFusion:
    def __init__(self):
        self.state_estimator = HumanoidStateEstimator()
        self.sensor_weights = {
            'imu': 0.4,
            'kinect': 0.3,
            'lidar': 0.2,
            'force_sensors': 0.1
        }

    def fuse_sensor_data(self, sensor_measurements, dt=0.01):
        """
        Fuse multiple sensor measurements into coherent state estimate.

        Args:
            sensor_measurements: Dictionary with sensor data
            dt: Time step for prediction
        """
        # Prediction step
        self.state_estimator.predict(control_input=None, dt=dt)

        # Update with each sensor type
        if 'imu' in sensor_measurements:
            self.state_estimator.update_imu(sensor_measurements['imu'])

        if 'kinect' in sensor_measurements:
            self.state_estimator.update_kinect(sensor_measurements['kinect'])

        if 'lidar' in sensor_measurements:
            self.state_estimator.update_lidar(sensor_measurements['lidar'])

        if 'force_sensors' in sensor_measurements:
            self.state_estimator.update_force_plate(sensor_measurements['force_sensors'])

        # Get fused state estimate
        state_estimate = self.state_estimator.get_state_estimate()

        # Additional processing to extract meaningful information
        balance_metrics = self.calculate_balance_metrics(state_estimate)
        contact_state = self.estimate_contact_state(sensor_measurements)

        return {
            'state_estimate': state_estimate,
            'balance_metrics': balance_metrics,
            'contact_state': contact_state,
            'confidence': self.calculate_fusion_confidence(sensor_measurements)
        }

    def calculate_balance_metrics(self, state_estimate):
        """
        Calculate balance-related metrics from state estimate.
        """
        com_pos = state_estimate['com_position']
        com_vel = state_estimate['com_velocity']
        orientation = state_estimate['orientation']

        # Calculate tilt angle from upright position
        tilt_angle = self.calculate_tilt_from_orientation(orientation)

        # Calculate ZMP (simplified)
        com_height = com_pos[2]
        gravity = 9.81
        omega = math.sqrt(gravity / com_height) if com_height > 0 else 0

        if omega > 0:
            zmp_x = com_pos[0] - com_vel[0] / omega**2
            zmp_y = com_pos[1] - com_vel[1] / omega**2
        else:
            zmp_x, zmp_y = com_pos[0], com_pos[1]

        return {
            'com_position': com_pos.tolist(),
            'tilt_angle': tilt_angle,
            'zmp_position': [zmp_x, zmp_y],
            'angular_velocity': state_estimate['angular_velocity'].tolist()
        }

    def calculate_tilt_from_orientation(self, orientation):
        """
        Calculate tilt angle from quaternion orientation.
        """
        # Convert quaternion to Euler angles (simplified)
        # Extract roll and pitch from quaternion
        w, x, y, z = orientation

        # Calculate roll (rotation around x-axis)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Calculate pitch (rotation around y-axis)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        # Combined tilt angle
        tilt_angle = math.sqrt(roll**2 + pitch**2)
        return tilt_angle

    def estimate_contact_state(self, sensor_measurements):
        """
        Estimate robot's contact state (which feet are in contact).
        """
        contact_state = {
            'left_foot_contact': False,
            'right_foot_contact': False,
            'contact_confidence': 0.0,
            'support_polygon': []
        }

        # Check force sensors
        if 'left_foot_force' in sensor_measurements:
            left_force_magnitude = np.linalg.norm(sensor_measurements['left_foot_force'])
            contact_state['left_foot_contact'] = left_force_magnitude > 10.0  # 10N threshold

        if 'right_foot_force' in sensor_measurements:
            right_force_magnitude = np.linalg.norm(sensor_measurements['right_foot_force'])
            contact_state['right_foot_contact'] = right_force_magnitude > 10.0

        # Calculate support polygon based on contact feet
        if contact_state['left_foot_contact'] and contact_state['right_foot_contact']:
            # Double support - use both feet
            contact_state['support_polygon'] = self.calculate_double_support_polygon(
                sensor_measurements.get('left_foot_position', [0, -0.1, 0]),
                sensor_measurements.get('right_foot_position', [0, 0.1, 0])
            )
            contact_state['contact_confidence'] = 0.9
        elif contact_state['left_foot_contact']:
            # Left foot support
            contact_state['support_polygon'] = self.calculate_single_support_polygon(
                sensor_measurements.get('left_foot_position', [0, -0.1, 0])
            )
            contact_state['contact_confidence'] = 0.8
        elif contact_state['right_foot_contact']:
            # Right foot support
            contact_state['support_polygon'] = self.calculate_single_support_polygon(
                sensor_measurements.get('right_foot_position', [0, 0.1, 0])
            )
            contact_state['contact_confidence'] = 0.8
        else:
            # No contact (flying phase in walking)
            contact_state['support_polygon'] = []
            contact_state['contact_confidence'] = 0.3

        return contact_state

    def calculate_double_support_polygon(self, left_foot_pos, right_foot_pos):
        """
        Calculate support polygon for double support phase.
        """
        # Simple rectangular approximation between feet
        center_x = (left_foot_pos[0] + right_foot_pos[0]) / 2
        center_y = (left_foot_pos[1] + right_foot_pos[1]) / 2

        # Foot dimensions (typical humanoid foot)
        foot_length = 0.20  # 20cm
        foot_width = 0.10   # 10cm

        # Create polygon vertices
        vertices = [
            [center_x - foot_length/2, center_y - foot_width],
            [center_x + foot_length/2, center_y - foot_width],
            [center_x + foot_length/2, center_y + foot_width],
            [center_x - foot_length/2, center_y + foot_width]
        ]

        return vertices

    def calculate_single_support_polygon(self, foot_pos):
        """
        Calculate support polygon for single support phase.
        """
        foot_length = 0.20
        foot_width = 0.10

        center_x, center_y = foot_pos[0], foot_pos[1]

        vertices = [
            [center_x - foot_length/2, center_y - foot_width/2],
            [center_x + foot_length/2, center_y - foot_width/2],
            [center_x + foot_length/2, center_y + foot_width/2],
            [center_x - foot_length/2, center_y + foot_width/2]
        ]

        return vertices

    def calculate_fusion_confidence(self, sensor_measurements):
        """
        Calculate overall confidence in the fused state estimate.
        """
        confidence_factors = []

        # IMU confidence based on signal quality
        if 'imu' in sensor_measurements:
            imu_data = sensor_measurements['imu']
            # Check for reasonable accelerometer values (should be around 9.81 m/s² when stationary)
            acc_magnitude = np.linalg.norm(imu_data[:3])
            if 8.0 < acc_magnitude < 12.0:  # Reasonable range
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)  # Low confidence if accelerometer seems wrong

        # Kinect confidence based on tracking quality
        if 'kinect_confidence' in sensor_measurements:
            confidence_factors.append(sensor_measurements['kinect_confidence'])
        else:
            confidence_factors.append(0.7)  # Default confidence

        # Overall confidence is average of individual confidences
        overall_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

        return overall_confidence
```

## Perception-Action Integration

### Closed-Loop Control with Perception Feedback

```python
class PerceptionActionController:
    def __init__(self, robot_interface, perception_system):
        self.robot = robot_interface
        self.perception = perception_system
        self.control_loop_active = False

        # Control parameters
        self.control_frequency = 100  # Hz
        self.dt = 1.0 / self.control_frequency

        # Task-specific controllers
        self.balance_controller = ZMPController()
        self.manipulation_controller = OperationalSpaceController()
        self.walking_controller = MPCWalkingController()

        # State estimation
        self.state_estimator = MultiSensorFusion()

    def start_closed_loop_control(self):
        """
        Start the closed-loop perception-action control system.
        """
        self.control_loop_active = True
        self.control_thread = threading.Thread(target=self.control_loop)
        self.control_thread.start()

    def stop_closed_loop_control(self):
        """
        Stop the closed-loop perception-action control system.
        """
        self.control_loop_active = False
        if hasattr(self, 'control_thread'):
            self.control_thread.join()

    def control_loop(self):
        """
        Main perception-action control loop.
        """
        last_time = time.time()

        while self.control_loop_active:
            current_time = time.time()
            dt = current_time - last_time

            if dt < 1.0 / self.control_frequency:
                time.sleep(1.0 / self.control_frequency - dt)
                continue

            # 1. Acquire sensor data
            sensor_data = self.robot.get_sensor_data()

            # 2. Process perception
            perception_results = self.perception.process_visual_scene(sensor_data['camera'])
            proprioceptive_results = self.perception.process_proprioceptive_data(sensor_data['joint_states'])
            force_results = self.perception.process_force_torque_data(sensor_data['force_torque'])

            # 3. Fuse sensor data
            fused_state = self.state_estimator.fuse_sensor_data({
                'imu': sensor_data['imu'],
                'kinect': perception_results.get('pose_estimate'),
                'force_sensors': force_results
            }, dt)

            # 4. Plan actions based on perception
            control_commands = self.plan_control_actions(fused_state, perception_results)

            # 5. Execute control commands
            self.robot.send_control_commands(control_commands)

            # 6. Update timing
            last_time = current_time

    def plan_control_actions(self, fused_state, perception_results):
        """
        Plan control actions based on fused state and perception results.
        """
        control_commands = {
            'balance_torques': np.zeros(self.robot.n_joints),
            'walking_commands': [],
            'manipulation_commands': [],
            'head_movement': []
        }

        # Balance control based on state estimate
        balance_metrics = fused_state['balance_metrics']
        contact_state = fused_state['contact_state']

        if contact_state['contact_confidence'] > 0.5:
            # Calculate balance correction torques
            zmp_error = self.calculate_zmp_error(balance_metrics, contact_state)
            balance_torques = self.balance_controller.compute_balance_correction(
                zmp_error, fused_state['state_estimate']['com_velocity']
            )
            control_commands['balance_torques'] = balance_torques

        # Manipulation based on object detection
        if 'objects' in perception_results:
            for obj in perception_results['objects']:
                if obj['class'] == 'person' and obj['confidence'] > 0.8:
                    # Plan interaction with detected person
                    interaction_commands = self.plan_person_interaction(obj, fused_state)
                    control_commands['manipulation_commands'].extend(interaction_commands)

        # Walking based on environment understanding
        if perception_results.get('scene_description', {}).get('navigation_needed', False):
            walking_commands = self.plan_navigation(perception_results, fused_state)
            control_commands['walking_commands'] = walking_commands

        # Head movement for attention
        attention_target = self.select_attention_target(perception_results)
        if attention_target:
            head_commands = self.plan_head_movement(attention_target, fused_state)
            control_commands['head_movement'] = head_commands

        return control_commands

    def calculate_zmp_error(self, balance_metrics, contact_state):
        """
        Calculate ZMP error for balance control.
        """
        zmp_current = balance_metrics['zmp_position']
        support_polygon = contact_state['support_polygon']

        if not support_polygon:
            # No support - robot is likely falling
            return np.array([100.0, 100.0])  # Large error to trigger emergency response

        # Check if ZMP is within support polygon
        zmp_inside = self.is_point_in_polygon(zmp_current, support_polygon)

        if not zmp_inside:
            # Calculate closest point in polygon to current ZMP
            closest_point = self.find_closest_point_in_polygon(zmp_current, support_polygon)
            zmp_error = np.array(closest_point) - np.array(zmp_current)
        else:
            # ZMP is inside support polygon - error is small
            zmp_error = np.zeros(2)

        return zmp_error

    def is_point_in_polygon(self, point, polygon):
        """
        Check if point is inside polygon using ray casting algorithm.
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def find_closest_point_in_polygon(self, point, polygon):
        """
        Find the closest point to the given point that is inside the polygon.
        """
        # This is a simplified implementation
        # In practice, this would use more sophisticated geometric algorithms
        px, py = point

        # Find the closest vertex
        closest_vertex = min(polygon, key=lambda v: (v[0]-px)**2 + (v[1]-py)**2)

        # Return the closest vertex as the "closest interior point"
        # (This is an approximation - a real implementation would find the true closest point)
        return closest_vertex

    def plan_person_interaction(self, person_obj, fused_state):
        """
        Plan interaction with detected person.
        """
        # Calculate person's position relative to robot
        person_pos = person_obj['center_2d']  # This would be converted to 3D in practice

        # Determine appropriate interaction based on distance and context
        com_pos = fused_state['state_estimate']['com_position']
        distance_to_person = np.linalg.norm(np.array(person_pos[:2]) - com_pos[:2])

        interaction_commands = []

        if distance_to_person > 2.0:  # Person is far away
            # Turn head to look at person
            head_yaw = math.atan2(person_pos[1] - com_pos[1], person_pos[0] - com_pos[0])
            interaction_commands.append(('head_yaw', head_yaw))

        elif distance_to_person > 0.5:  # Person is at interaction distance
            # Wave to greet person
            interaction_commands.append(('wave_greeting', True))
            interaction_commands.append(('speak', f"Hello! I see you at position {person_pos[:2]}"))

        else:  # Person is very close
            # Be cautious and maintain personal space
            interaction_commands.append(('step_back', True))
            interaction_commands.append(('speak', "Please maintain appropriate distance"))

        return interaction_commands

    def plan_navigation(self, perception_results, fused_state):
        """
        Plan navigation based on environment understanding.
        """
        # Analyze scene for navigable paths
        scene_description = perception_results.get('scene_description', {})
        objects = perception_results.get('objects', [])

        # Find free space for navigation
        free_space = self.identify_free_space(objects)

        # Plan path to navigate around obstacles
        navigation_path = self.plan_path_to_goal(free_space, fused_state)

        # Generate walking commands
        walking_commands = self.generate_walking_commands(navigation_path)

        return walking_commands

    def identify_free_space(self, objects):
        """
        Identify free space in the environment based on object positions.
        """
        # In practice, this would create a costmap or occupancy grid
        # For this example, we'll return a simplified representation
        occupied_areas = []

        for obj in objects:
            if obj['confidence'] > 0.6:  # Confident object detection
                # Create bounding area around object
                bbox = obj['bbox']
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]

                # Inflate area to account for robot size
                safety_margin = 0.3  # 30cm safety margin
                inflated_area = {
                    'center': [center_x, center_y],
                    'size': [width + safety_margin*2, height + safety_margin*2],
                    'bbox': [center_x - width/2 - safety_margin,
                            center_y - height/2 - safety_margin,
                            center_x + width/2 + safety_margin,
                            center_y + height/2 + safety_margin]
                }
                occupied_areas.append(inflated_area)

        return occupied_areas

    def select_attention_target(self, perception_results):
        """
        Select target for robot attention based on salience and relevance.
        """
        objects = perception_results.get('objects', [])
        humans = perception_results.get('humans', [])

        # Prioritize humans over objects
        if humans:
            # Select closest human as attention target
            closest_human = min(humans, key=lambda h: self.calculate_distance_to_robot(h))
            return {
                'type': 'human',
                'position': closest_human['bbox'][:2],  # Simplified position
                'confidence': closest_human['pose_confidence']
            }

        elif objects:
            # Select most salient object (largest or closest)
            most_salient = max(objects, key=lambda obj: obj['confidence'] * self.calculate_salience(obj))
            return {
                'type': 'object',
                'position': most_salient['center_2d'],
                'confidence': most_salient['confidence']
            }

        return None

    def calculate_distance_to_robot(self, human_info):
        """
        Calculate distance from robot to human (simplified).
        """
        # This would use actual robot position in real implementation
        return np.linalg.norm(np.array(human_info['bbox'][:2]))

    def calculate_salience(self, object_info):
        """
        Calculate visual salience of an object.
        """
        # Salience based on size (larger objects are more salient)
        bbox = object_info['bbox']
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        return area

    def plan_head_movement(self, attention_target, fused_state):
        """
        Plan head movement to attend to target.
        """
        # Calculate required head rotation to look at target
        robot_pos = fused_state['state_estimate']['com_position']
        target_pos = attention_target['position']

        # Calculate required yaw and pitch angles
        delta_x = target_pos[0] - robot_pos[0]
        delta_y = target_pos[1] - robot_pos[1]
        delta_z = target_pos[2] - robot_pos[2] if len(target_pos) > 2 else 0

        required_yaw = math.atan2(delta_y, delta_x)
        required_pitch = math.atan2(delta_z, math.sqrt(delta_x**2 + delta_y**2))

        return {
            'head_yaw': required_yaw,
            'head_pitch': required_pitch,
            'attention_confidence': attention_target['confidence']
        }

    def generate_walking_commands(self, path):
        """
        Generate walking commands from planned path.
        """
        walking_commands = []

        for i, waypoint in enumerate(path):
            # Generate step commands for each waypoint
            step_command = {
                'step_type': 'normal',  # 'normal', 'turn', 'avoid'
                'target_position': waypoint,
                'timing': i * 0.8,  # Assume 0.8s per step
                'foot': 'left' if i % 2 == 0 else 'right'  # Alternate feet
            }
            walking_commands.append(step_command)

        return walking_commands
```

## Safety and Robustness

### Perception-Based Safety Systems

```python
class PerceptionBasedSafetySystem:
    def __init__(self, perception_controller):
        self.perception_controller = perception_controller
        self.safety_active = True
        self.emergency_stop_triggered = False

        # Safety thresholds
        self.safety_thresholds = {
            'approaching_object_velocity': 2.0,  # m/s
            'person_too_close_distance': 0.3,   # meters
            'object_falling_velocity': 1.0,     # m/s
            'unexpected_contact_force': 100.0,  # Newtons
            'balance_loss_angle': 30.0,        # degrees
            'fall_detected_threshold': 0.5      # arbitrary unit for fall detection
        }

    def monitor_safety_conditions(self, sensor_data, perception_results):
        """
        Monitor safety conditions based on perception and sensor data.
        """
        safety_violations = []

        # Check for approaching objects
        approaching_objects = self.detect_approaching_objects(perception_results)
        for obj in approaching_objects:
            if obj['velocity'] > self.safety_thresholds['approaching_object_velocity']:
                safety_violations.append({
                    'type': 'approaching_object',
                    'object': obj['name'],
                    'velocity': obj['velocity'],
                    'severity': 'warning'
                })

        # Check for people in danger zone
        people_in_danger = self.detect_people_in_danger_zone(perception_results)
        for person in people_in_danger:
            safety_violations.append({
                'type': 'person_too_close',
                'person_id': person['id'],
                'distance': person['distance'],
                'severity': 'critical'
            })

        # Check for falling objects
        falling_objects = self.detect_falling_objects(perception_results)
        for obj in falling_objects:
            if obj['velocity'] > self.safety_thresholds['object_falling_velocity']:
                safety_violations.append({
                    'type': 'falling_object',
                    'object': obj['name'],
                    'velocity': obj['velocity'],
                    'severity': 'critical'
                })

        # Check balance based on perception
        balance_metrics = perception_results.get('balance_metrics', {})
        tilt_angle = balance_metrics.get('tilt_angle', 0)
        if tilt_angle > self.safety_thresholds['balance_loss_angle']:
            safety_violations.append({
                'type': 'balance_loss',
                'tilt_angle': tilt_angle,
                'severity': 'critical'
            })

        # Trigger safety responses
        self.handle_safety_violations(safety_violations)

        return safety_violations

    def detect_approaching_objects(self, perception_results):
        """
        Detect objects that are approaching the robot.
        """
        approaching_objects = []

        # This would compare object positions across time frames
        # For this example, we'll simulate detection
        objects = perception_results.get('objects', [])

        for obj in objects:
            if obj['class'] in ['person', 'ball', 'cart'] and obj['confidence'] > 0.7:
                # Calculate apparent motion toward robot
                # In practice, this would use object tracking across frames
                if 'velocity' in obj:  # If velocity is available from tracking
                    obj_velocity = np.array(obj['velocity'])
                    robot_pos = np.array([0, 0, 0])  # Simplified robot position
                    obj_pos = np.array(obj['center_2d'] + [0])  # Simplified 3D position

                    # Check if object is moving toward robot
                    direction_to_robot = robot_pos - obj_pos
                    if np.dot(obj_velocity, direction_to_robot) > 0:  # Moving toward robot
                        approaching_objects.append({
                            'name': obj['class'],
                            'velocity': np.linalg.norm(obj_velocity),
                            'position': obj_pos.tolist()
                        })

        return approaching_objects

    def detect_people_in_danger_zone(self, perception_results):
        """
        Detect people in robot's danger zone (too close).
        """
        people_in_danger = []

        humans = perception_results.get('humans', [])

        for human in humans:
            if human['pose_confidence'] > 0.6:
                # Calculate distance to robot (simplified)
                human_pos = np.array([
                    (human['bbox'][0] + human['bbox'][2]) / 2,
                    (human['bbox'][1] + human['bbox'][3]) / 2,
                    0  # Simplified Z coordinate
                ])

                distance = np.linalg.norm(human_pos)  # Distance from robot (at origin)

                if distance < self.safety_thresholds['person_too_close_distance']:
                    people_in_danger.append({
                        'id': len(people_in_danger),  # Simplified ID
                        'distance': distance,
                        'position': human_pos.tolist()
                    })

        return people_in_danger

    def detect_falling_objects(self, perception_results):
        """
        Detect objects that are falling toward the robot.
        """
        falling_objects = []

        objects = perception_results.get('objects', [])

        for obj in objects:
            if obj['confidence'] > 0.7:
                # Check if object Z velocity indicates falling
                # This would require tracking object motion over time
                if 'velocity' in obj and len(obj['velocity']) >= 3:
                    z_velocity = obj['velocity'][2]  # Z component (vertical)
                    if z_velocity < -self.safety_thresholds['object_falling_velocity']:
                        falling_objects.append({
                            'name': obj['class'],
                            'velocity': abs(z_velocity),
                            'position': obj['center_2d'] + [obj.get('estimated_z', 0)]
                        })

        return falling_objects

    def handle_safety_violations(self, violations):
        """
        Handle detected safety violations.
        """
        critical_violations = [v for v in violations if v['severity'] == 'critical']
        warning_violations = [v for v in violations if v['severity'] == 'warning']

        if critical_violations:
            # Trigger emergency stop
            self.trigger_emergency_stop()
            print(f"CRITICAL SAFETY VIOLATIONS: {critical_violations}")

        elif warning_violations:
            # Log warnings and adjust behavior
            for violation in warning_violations:
                print(f"SAFETY WARNING: {violation}")

            # Adjust robot behavior to be more cautious
            self.adjust_behavior_for_safety()

    def trigger_emergency_stop(self):
        """
        Trigger emergency stop procedures.
        """
        if not self.emergency_stop_triggered:
            print("EMERGENCY STOP TRIGGERED - HALTING ALL MOTIONS")
            self.emergency_stop_triggered = True

            # Send emergency stop to robot
            self.perception_controller.robot.send_emergency_stop()

            # Activate protective behaviors
            self.activate_protective_posture()

    def adjust_behavior_for_safety(self):
        """
        Adjust robot behavior to improve safety.
        """
        # Reduce walking speed
        self.perception_controller.walking_controller.max_speed *= 0.5

        # Increase safety margins
        self.perception_controller.walking_controller.safety_margin *= 1.5

        # Increase caution in navigation
        self.perception_controller.walking_controller.caution_level = 'high'

    def activate_protective_posture(self):
        """
        Activate protective posture to minimize injury risk.
        """
        # Move arms to protect head and torso
        protective_joints = {
            'left_shoulder_pitch': -0.5,
            'left_shoulder_roll': 0.5,
            'left_elbow_pitch': 1.0,
            'right_shoulder_pitch': -0.5,
            'right_shoulder_roll': -0.5,
            'right_elbow_pitch': 1.0,
            'head_pitch': 0.5  # Tuck head
        }

        # Send protective joint commands
        self.perception_controller.robot.set_joint_positions(protective_joints)

    def reset_safety_system(self):
        """
        Reset safety system after emergency stop.
        """
        self.emergency_stop_triggered = False
        print("Safety system reset - robot ready for operation")
```

## Implementation Example: Complete Perception-Action System

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu, Image, PointCloud2
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float64MultiArray
import threading
import time

class HumanoidPerceptionActionNode(Node):
    def __init__(self):
        super().__init__('humanoid_perception_action_node')

        # Initialize perception and control systems
        self.perception_system = HumanoidVisualPerception(None)  # Will initialize later
        self.state_estimator = MultiSensorFusion()
        self.controller = PerceptionActionController(None, self.perception_system)
        self.safety_system = PerceptionBasedSafetySystem(self.controller)

        # Publishers and subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )

        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )

        self.camera_sub = self.create_subscription(
            Image, '/camera/image_raw', self.camera_callback, 10
        )

        self.pointcloud_sub = self.create_subscription(
            PointCloud2, '/camera/depth/points', self.pointcloud_callback, 10
        )

        self.force_torque_sub = self.create_subscription(
            WrenchStamped, '/l_foot_force', self.left_foot_force_callback, 10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joint_cmd_pub = self.create_publisher(Float64MultiArray, '/joint_commands', 10)

        # Data storage
        self.sensor_data = {
            'joint_states': None,
            'imu': None,
            'camera': None,
            'pointcloud': None,
            'force_torque': {'left': None, 'right': None}
        }

        # Control loop
        self.control_active = False
        self.control_thread = None

        self.get_logger().info('Humanoid Perception-Action Node initialized')

    def joint_state_callback(self, msg):
        self.sensor_data['joint_states'] = msg

    def imu_callback(self, msg):
        self.sensor_data['imu'] = msg

    def camera_callback(self, msg):
        self.sensor_data['camera'] = msg

    def pointcloud_callback(self, msg):
        self.sensor_data['pointcloud'] = msg

    def left_foot_force_callback(self, msg):
        self.sensor_data['force_torque']['left'] = msg

    def right_foot_force_callback(self, msg):
        self.sensor_data['force_torque']['right'] = msg

    def start_control_loop(self):
        """Start the perception-action control loop."""
        self.control_active = True
        self.control_thread = threading.Thread(target=self.control_loop)
        self.control_thread.start()

    def stop_control_loop(self):
        """Stop the perception-action control loop."""
        self.control_active = False
        if self.control_thread:
            self.control_thread.join()

    def control_loop(self):
        """Main perception-action control loop."""
        last_time = time.time()

        while self.control_active:
            current_time = time.time()
            dt = current_time - last_time

            if dt < 0.01:  # 100Hz control
                time.sleep(0.01 - dt)
                continue

            # Acquire all sensor data
            current_sensor_data = self.get_current_sensor_data()

            # Process perception
            perception_results = self.process_perception(current_sensor_data)

            # Monitor safety
            safety_violations = self.safety_system.monitor_safety_conditions(
                current_sensor_data, perception_results
            )

            if safety_violations:
                # Handle safety violations
                if any(v['severity'] == 'critical' for v in safety_violations):
                    continue  # Skip control if critical safety violation

            # Plan and execute actions
            if self.safety_system.emergency_stop_triggered:
                # Only perform safety-related actions
                self.execute_safety_procedures()
            else:
                control_commands = self.controller.plan_control_actions({}, perception_results)
                self.execute_control_commands(control_commands)

            last_time = current_time

    def get_current_sensor_data(self):
        """Get current sensor data."""
        return self.sensor_data.copy()

    def process_perception(self, sensor_data):
        """Process perception data from all sensors."""
        if sensor_data['camera'] is not None:
            # Process visual data
            image_data = self.bridge.imgmsg_to_cv2(sensor_data['camera'], "bgr8")
            visual_results = self.perception_system.process_visual_scene(image_data)
        else:
            visual_results = {}

        if sensor_data['pointcloud'] is not None:
            # Process depth data
            depth_results = self.perception_system.process_pointcloud(sensor_data['pointcloud'])
        else:
            depth_results = {}

        # Combine results
        perception_results = {**visual_results, **depth_results}

        # Add balance metrics
        if sensor_data['imu'] and sensor_data['joint_states']:
            balance_metrics = self.calculate_balance_metrics(sensor_data)
            perception_results['balance_metrics'] = balance_metrics

        return perception_results

    def calculate_balance_metrics(self, sensor_data):
        """Calculate balance-related metrics."""
        # Extract relevant data from sensor readings
        imu = sensor_data['imu']
        joint_states = sensor_data['joint_states']

        # Calculate tilt from IMU
        if imu:
            # Convert IMU orientation to tilt angles (simplified)
            orientation = imu.orientation
            tilt_angle = math.sqrt(orientation.x**2 + orientation.y**2) * 180/math.pi

            # Calculate angular velocity
            ang_vel = imu.angular_velocity
            angular_velocity_magnitude = math.sqrt(ang_vel.x**2 + ang_vel.y**2 + ang_vel.z**2)
        else:
            tilt_angle = 0.0
            angular_velocity_magnitude = 0.0

        return {
            'tilt_angle': tilt_angle,
            'angular_velocity': angular_velocity_magnitude,
            'imu_data': [imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z,
                        imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z] if imu else [0, 0, 0, 0, 0, 0]
        }

    def execute_control_commands(self, commands):
        """Execute control commands."""
        # Publish balance torques
        if 'balance_torques' in commands:
            torque_msg = Float64MultiArray()
            torque_msg.data = commands['balance_torques'].tolist()
            self.joint_cmd_pub.publish(torque_msg)

        # Handle walking commands
        if 'walking_commands' in commands and commands['walking_commands']:
            # Execute first walking command
            walking_cmd = commands['walking_commands'][0]
            twist_msg = Twist()
            # Convert walking command to velocity command
            twist_msg.linear.x = 0.2  # Simplified forward velocity
            self.cmd_vel_pub.publish(twist_msg)

        # Handle manipulation commands
        if 'manipulation_commands' in commands:
            for cmd in commands['manipulation_commands']:
                self.execute_manipulation_command(cmd)

        # Handle head movement
        if 'head_movement' in commands and commands['head_movement']:
            head_cmd = commands['head_movement']
            self.move_head(head_cmd)

    def execute_manipulation_command(self, command):
        """Execute a manipulation command."""
        cmd_type, cmd_value = command[0], command[1]

        if cmd_type == 'wave_greeting':
            if cmd_value:
                self.wave_greeting()
        elif cmd_type == 'speak':
            self.speak_text(cmd_value)

    def wave_greeting(self):
        """Execute waving greeting motion."""
        # This would send specific joint commands to make waving motion
        wave_joints = {
            'left_shoulder_pitch': -0.3,
            'left_shoulder_roll': 0.5,
            'left_elbow_pitch': 1.2,
            'left_wrist_yaw': 0.5
        }

        # Send joint commands (implementation would depend on specific robot)
        self.get_logger().info('Executing wave greeting')

    def move_head(self, head_command):
        """Move robot head to attend to target."""
        if 'head_yaw' in head_command:
            # Send head yaw command
            pass
        if 'head_pitch' in head_command:
            # Send head pitch command
            pass

    def execute_safety_procedures(self):
        """Execute safety procedures when emergency stop is active."""
        # Stop all motion
        zero_torques = Float64MultiArray()
        zero_torques.data = [0.0] * 28  # Assuming 28 joints
        self.joint_cmd_pub.publish(zero_torques)

        # Send stop command to velocity controller
        stop_twist = Twist()
        self.cmd_vel_pub.publish(stop_twist)

        self.get_logger().warn('Safety procedures active - all motion stopped')

def main(args=None):
    rclpy.init(args=args)
    perception_action_node = HumanoidPerceptionActionNode()

    try:
        # Start control loop
        perception_action_node.start_control_loop()

        rclpy.spin(perception_action_node)
    except KeyboardInterrupt:
        perception_action_node.get_logger().info('Shutting down perception-action node...')
        perception_action_node.stop_control_loop()
    finally:
        perception_action_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

Humanoid perception and control systems form the backbone of autonomous humanoid robot operation. These systems must integrate multiple sensor modalities in real-time to enable:

1. **Environmental Understanding**: Recognizing objects, people, and spatial relationships
2. **State Estimation**: Accurately determining robot state using sensor fusion
3. **Balance Control**: Maintaining stability through ZMP-based control
4. **Safe Operation**: Monitoring and responding to safety conditions
5. **Natural Interaction**: Engaging with humans in intuitive ways

The complexity of these systems requires sophisticated algorithms and careful integration to ensure reliable, safe, and effective humanoid robot operation in human environments.