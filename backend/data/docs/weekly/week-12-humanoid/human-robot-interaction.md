---
sidebar_label: 'Human-Robot Interaction for Humanoid Robots'
title: 'Human-Robot Interaction for Humanoid Robots'
---

# Human-Robot Interaction for Humanoid Robots

## Introduction to Human-Robot Interaction (HRI)

Human-Robot Interaction (HRI) is a critical field that focuses on how humans and robots can effectively communicate and collaborate. For humanoid robots, HRI becomes particularly important as these robots are designed to operate in human environments and interact naturally with humans.

## HRI Fundamentals for Humanoid Robots

### Social Interaction Principles

Humanoid robots must follow social interaction principles to be accepted and effective in human environments:

1. **Proxemics**: Respect personal space and appropriate distances
2. **Turn-taking**: Follow natural conversation rhythms
3. **Gaze behavior**: Use appropriate eye contact and gaze direction
4. **Gestures**: Employ human-like gestures for communication
5. **Emotional expression**: Show appropriate emotional responses

### Trust and Acceptance Models

```python
import numpy as np
import math
from enum import Enum

class InteractionStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    INTIMATE = "intimate"
    PUBLIC = "public"

class TrustLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class HumanoidHRIController:
    def __init__(self):
        # Interaction state
        self.trust_level = TrustLevel.MEDIUM
        self.interaction_style = InteractionStyle.CASUAL
        self.social_distance = 1.0  # meters
        self.gaze_target = None
        self.familiarity_level = 0.0  # 0.0 to 1.0

        # User tracking
        self.tracked_users = {}
        self.current_interlocutor = None

        # HRI parameters
        self.hri_gains = {
            'engagement': 0.1,
            'trust': 0.05,
            'familiarity': 0.02
        }

    def calculate_trust_level(self, user_id):
        """
        Calculate trust level based on interaction history.

        Args:
            user_id: Unique identifier for the user

        Returns:
            trust_level: Calculated trust level (0.0 to 1.0)
        """
        if user_id not in self.tracked_users:
            return 0.5  # Neutral trust for new users

        user_data = self.tracked_users[user_id]

        # Factors affecting trust:
        # 1. Interaction success rate
        success_rate = user_data.get('successful_interactions', 0) / max(1, user_data.get('total_interactions', 1))

        # 2. Time since last interaction (decay factor)
        time_decay = math.exp(-(time.time() - user_data.get('last_interaction', time.time())) / (24 * 3600))  # 1 day half-life

        # 3. Robot behavior consistency
        consistency = user_data.get('behavior_consistency', 0.7)

        # 4. Safety compliance (no accidents)
        safety_factor = 1.0 if user_data.get('accidents', 0) == 0 else 0.3

        # Weighted trust calculation
        trust = (0.4 * success_rate +
                0.2 * time_decay +
                0.2 * consistency +
                0.2 * safety_factor)

        return min(1.0, max(0.0, trust))

    def update_user_interaction(self, user_id, success=True, safety_compliant=True):
        """
        Update user interaction data for trust calculation.
        """
        if user_id not in self.tracked_users:
            self.tracked_users[user_id] = {
                'total_interactions': 0,
                'successful_interactions': 0,
                'behavior_consistency': 0.7,
                'accidents': 0,
                'last_interaction': time.time()
            }

        user_data = self.tracked_users[user_id]
        user_data['total_interactions'] += 1

        if success:
            user_data['successful_interactions'] += 1

        if not safety_compliant:
            user_data['accidents'] += 1

        user_data['last_interaction'] = time.time()

        # Update trust level
        self.trust_level = self.calculate_trust_level(user_id)

    def determine_interaction_style(self, user_id, context):
        """
        Determine appropriate interaction style based on user and context.

        Args:
            user_id: User identifier
            context: Current interaction context

        Returns:
            interaction_style: Appropriate interaction style
        """
        trust = self.calculate_trust_level(user_id)
        familiarity = self.get_user_familiarity(user_id)
        environment = context.get('environment', 'public')

        if environment == 'home':
            if trust > 0.8 and familiarity > 0.7:
                return InteractionStyle.INTIMATE
            elif trust > 0.5:
                return InteractionStyle.CASUAL
            else:
                return InteractionStyle.FORMAL
        elif environment == 'office':
            return InteractionStyle.FORMAL
        elif environment == 'public':
            return InteractionStyle.PUBLIC
        else:
            # Default based on trust and familiarity
            if trust > 0.8 and familiarity > 0.8:
                return InteractionStyle.CASUAL
            elif trust > 0.5:
                return InteractionStyle.FORMAL
            else:
                return InteractionStyle.PUBLIC

    def get_user_familiarity(self, user_id):
        """
        Get user familiarity level based on interaction history.
        """
        if user_id not in self.tracked_users:
            return 0.0

        user_data = self.tracked_users[user_id]
        interaction_count = user_data.get('total_interactions', 0)

        # Familiarity increases with interactions but saturates
        familiarity = min(1.0, interaction_count * 0.1)
        return familiarity

    def calculate_appropriate_distance(self, interaction_style, user_id):
        """
        Calculate appropriate social distance based on interaction style.

        Uses Edward T. Hall's proxemics model:
        - Intimate: 0-0.5m
        - Personal: 0.5-1.2m
        - Social: 1.2-3.7m
        - Public: 3.7+m
        """
        trust = self.calculate_trust_level(user_id)

        distance_ranges = {
            InteractionStyle.INTIMATE: (0.2, 0.5),
            InteractionStyle.CASUAL: (0.5, 1.0),
            InteractionStyle.FORMAL: (1.0, 2.0),
            InteractionStyle.PUBLIC: (2.0, 4.0)
        }

        base_min, base_max = distance_ranges.get(interaction_style, (1.0, 2.0))

        # Adjust based on trust (higher trust allows closer approach)
        trust_adjustment = (1.0 - trust) * 0.3  # Up to 30cm adjustment based on trust
        min_dist = base_min + trust_adjustment
        max_dist = base_max + trust_adjustment

        return (min_dist, max_dist)
```

## Gaze Control and Attention Management

### Gaze Behavior Implementation

```python
class GazeController:
    def __init__(self, head_joints=['neck_yaw', 'neck_pitch']):
        self.head_joints = head_joints
        self.current_gaze_target = None
        self.gaze_mode = 'passive'  # passive, active, scanning, avoiding

        # Gaze parameters
        self.gaze_params = {
            'fixation_duration': 0.3,  # seconds to look at target
            'saccade_speed': 300,      # degrees per second
            'blink_frequency': 0.2,    # blinks per second
            'attention_span': 5.0      # seconds to maintain attention
        }

        # Tracking state
        self.fixation_start_time = 0
        self.blink_timer = 0
        self.attention_timer = 0

    def update_gaze_target(self, target_position, target_type='person'):
        """
        Update gaze target based on visual tracking.

        Args:
            target_position: [x, y, z] position of target in robot frame
            target_type: Type of target ('person', 'object', 'location')
        """
        if target_type == 'person':
            # For people, look at eye level
            target_position[2] += 0.15  # Eye level offset for average person

        self.current_gaze_target = {
            'position': target_position,
            'type': target_type,
            'timestamp': time.time()
        }

        # Calculate required head joint angles for looking at target
        head_angles = self.calculate_gaze_angles(target_position)

        # Apply gaze control
        self.apply_gaze_control(head_angles)

    def calculate_gaze_angles(self, target_pos):
        """
        Calculate required head joint angles to look at target position.

        Args:
            target_pos: [x, y, z] target position in robot frame

        Returns:
            head_angles: [yaw, pitch] angles for head joints
        """
        # Calculate azimuth (yaw) and elevation (pitch) angles
        x, y, z = target_pos

        # Calculate distance to target
        distance = math.sqrt(x**2 + y**2 + z**2)

        if distance < 0.1:  # Too close, don't look
            return [0.0, 0.0]

        # Azimuth angle (horizontal)
        yaw = math.atan2(y, x)

        # Elevation angle (vertical)
        pitch = math.atan2(z, math.sqrt(x**2 + y**2))

        # Convert to joint space (simplified)
        # In reality, this would use inverse kinematics for neck joints
        joint_yaw = yaw * 0.8  # Scale factor for neck flexibility
        joint_pitch = pitch * 0.7  # Scale factor for neck flexibility

        return [joint_yaw, joint_pitch]

    def apply_gaze_control(self, target_angles):
        """
        Apply gaze control to head joints.
        """
        # This would send commands to head joint controllers
        # For this example, we'll just store the target
        self.target_head_angles = target_angles

    def execute_gaze_behavior(self, behavior_type='follow'):
        """
        Execute specific gaze behavior.

        Args:
            behavior_type: Type of gaze behavior ('follow', 'scan', 'avoid', 'engage')
        """
        if behavior_type == 'follow':
            self.follow_gaze_behavior()
        elif behavior_type == 'scan':
            self.scanning_gaze_behavior()
        elif behavior_type == 'avoid':
            self.avoidance_gaze_behavior()
        elif behavior_type == 'engage':
            self.engagement_gaze_behavior()

    def follow_gaze_behavior(self):
        """
        Follow gaze behavior - maintain focus on target.
        """
        if self.current_gaze_target:
            target_pos = self.current_gaze_target['position']
            head_angles = self.calculate_gaze_angles(target_pos)
            self.apply_gaze_control(head_angles)

    def scanning_gaze_behavior(self):
        """
        Scanning gaze behavior - look around environment.
        """
        # Implement systematic scanning pattern
        scan_pattern = [
            [0.0, 0.0],      # Center
            [0.3, 0.1],      # Upper right
            [0.0, 0.2],      # Up
            [-0.3, 0.1],     # Upper left
            [-0.3, -0.1],    # Lower left
            [0.0, -0.2],     # Down
            [0.3, -0.1],     # Lower right
        ]

        current_time = time.time()
        pattern_index = int(current_time * 2) % len(scan_pattern)  # 2 Hz scanning

        self.apply_gaze_control(scan_pattern[pattern_index])

    def engagement_gaze_behavior(self):
        """
        Engagement gaze behavior - show active attention.
        """
        # More dynamic gaze with occasional "looking away" then back
        if self.current_gaze_target:
            base_angles = self.calculate_gaze_angles(self.current_gaze_target['position'])

            # Add subtle variations to appear engaged
            current_time = time.time()
            variation = 0.05 * math.sin(current_time * 2)  # Small oscillation

            engaged_angles = [
                base_angles[0] + variation,
                base_angles[1] + variation * 0.5
            ]

            self.apply_gaze_control(engaged_angles)

    def select_gaze_target(self, visual_targets, social_context):
        """
        Select appropriate gaze target based on social context.

        Args:
            visual_targets: List of detected visual targets
            social_context: Current social interaction context

        Returns:
            selected_target: Best target to focus gaze on
        """
        if not visual_targets:
            return None

        # Priority ranking for gaze targets
        target_scores = []

        for target in visual_targets:
            score = 0.0

            # Social priority (people first)
            if target['type'] == 'person':
                score += 100.0

                # Higher priority for current interlocutor
                if target.get('user_id') == social_context.get('current_interlocutor'):
                    score += 50.0

                # Higher priority for people making eye contact
                if target.get('making_eye_contact', False):
                    score += 30.0

            # Movement priority (moving objects)
            elif target.get('velocity', 0) > 0.1:
                score += 20.0

            # Novelty priority (newly detected objects)
            elif target.get('time_since_detection', float('inf')) < 5.0:
                score += 10.0

            # Static objects
            else:
                score += 5.0

            target_scores.append((target, score))

        # Sort by score and return highest
        target_scores.sort(key=lambda x: x[1], reverse=True)
        return target_scores[0][0] if target_scores else None

    def handle_multiple_people(self, people_positions):
        """
        Handle gaze behavior when multiple people are present.
        """
        if len(people_positions) == 0:
            return

        elif len(people_positions) == 1:
            # Single person - focus on them
            self.update_gaze_target(people_positions[0], 'person')

        else:
            # Multiple people - implement social gaze behavior
            # Look at current speaker, then occasionally glance at others
            current_time = time.time()

            if (current_time - self.attention_timer) > self.gaze_params['attention_span']:
                # Switch attention to different person
                next_person_idx = (self.current_person_idx + 1) % len(people_positions)
                self.update_gaze_target(people_positions[next_person_idx], 'person')
                self.current_person_idx = next_person_idx
                self.attention_timer = current_time

            # Implement smooth transitions between people
            self.smooth_gaze_transition(people_positions)

    def smooth_gaze_transition(self, targets):
        """
        Smoothly transition gaze between multiple targets.
        """
        if not hasattr(self, 'current_target_idx'):
            self.current_target_idx = 0

        # Calculate smooth interpolation between targets
        current_target = targets[self.current_target_idx]
        next_target = targets[(self.current_target_idx + 1) % len(targets)]

        # Interpolate based on time
        transition_duration = 2.0  # seconds for transition
        current_time = time.time()
        progress = ((current_time - self.last_transition_time) % transition_duration) / transition_duration

        if progress < 0.5:
            # Moving toward next target
            self.update_gaze_target(
                self.interpolate_positions(current_target, next_target, progress * 2),
                'person'
            )
        else:
            # Moving back to current target
            self.update_gaze_target(
                self.interpolate_positions(next_target, current_target, (progress - 0.5) * 2),
                'person'
            )

    def interpolate_positions(self, pos1, pos2, t):
        """
        Linearly interpolate between two positions.
        """
        t = max(0.0, min(1.0, t))
        return [(1-t)*p1 + t*p2 for p1, p2 in zip(pos1, pos2)]
```

## Gesture Recognition and Generation

### Human Gesture Recognition

```python
import cv2
import numpy as np
from collections import deque
import mediapipe as mp

class HumanGestureRecognizer:
    def __init__(self):
        # Initialize MediaPipe for pose estimation
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7
        )

        # Gesture recognition state
        self.gesture_history = deque(maxlen=10)
        self.hand_landmarks_history = deque(maxlen=5)
        self.body_landmarks_history = deque(maxlen=5)

        # Define gesture patterns
        self.gesture_patterns = {
            'wave': self.is_wave_gesture,
            'point': self.is_pointing_gesture,
            'come_here': self.is_come_here_gesture,
            'stop': self.is_stop_gesture,
            'follow_me': self.is_follow_me_gesture,
            'help': self.is_help_gesture
        }

    def recognize_human_gestures(self, image):
        """
        Recognize human gestures from camera image.

        Args:
            image: Input image from camera

        Returns:
            recognized_gestures: List of recognized gestures with confidence
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process pose
        pose_results = self.pose.process(rgb_image)
        hand_results = self.hands.process(rgb_image)

        recognized_gestures = []

        # Analyze hand gestures
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                gesture = self.analyze_hand_gesture(hand_landmarks, pose_results.pose_landmarks)
                if gesture:
                    recognized_gestures.append(gesture)

        # Analyze body gestures
        if pose_results.pose_landmarks:
            body_gesture = self.analyze_body_gesture(pose_results.pose_landmarks)
            if body_gesture:
                recognized_gestures.append(body_gesture)

        return recognized_gestures

    def analyze_hand_gesture(self, hand_landmarks, body_landmarks=None):
        """
        Analyze hand gesture from hand landmarks.
        """
        # Convert landmarks to numpy array
        hand_points = []
        for landmark in hand_landmarks.landmark:
            hand_points.append([landmark.x, landmark.y, landmark.z])

        hand_points = np.array(hand_points)

        # Check for different gestures
        for gesture_name, gesture_func in self.gesture_patterns.items():
            if gesture_func['hand'](hand_points, body_landmarks):
                return {
                    'type': gesture_name,
                    'confidence': self.calculate_gesture_confidence(gesture_name, hand_points),
                    'timestamp': time.time(),
                    'location': self.estimate_gesture_location(hand_landmarks, body_landmarks)
                }

        return None

    def analyze_body_gesture(self, body_landmarks):
        """
        Analyze body gesture from pose landmarks.
        """
        if not body_landmarks:
            return None

        body_points = []
        for landmark in body_landmarks.landmark:
            body_points.append([landmark.x, landmark.y, landmark.z])

        body_points = np.array(body_points)

        # Check for body-based gestures
        if self.is_waving_body_gesture(body_points):
            return {
                'type': 'wave',
                'confidence': 0.8,
                'timestamp': time.time(),
                'location': 'body'
            }

        if self.is_pointing_body_gesture(body_points):
            return {
                'type': 'point',
                'confidence': 0.7,
                'timestamp': time.time(),
                'location': 'body'
            }

        return None

    def is_wave_gesture(self, hand_points, body_landmarks=None):
        """
        Detect waving gesture.
        """
        # Check if index finger is extended and palm is moving
        index_tip = hand_points[8]  # Index finger tip
        middle_tip = hand_points[12]  # Middle finger tip
        wrist = hand_points[0]  # Wrist

        # Calculate if fingers are extended
        index_extended = self.is_finger_extended(hand_points, 5, 8)
        middle_extended = self.is_finger_extended(hand_points, 9, 12)

        # Check if other fingers are curled
        other_curled = all([
            not self.is_finger_extended(hand_points, 1, 4),  # Thumb
            not self.is_finger_extended(hand_points, 13, 16),  # Ring finger
            not self.is_finger_extended(hand_points, 17, 20)  # Pinky
        ])

        return index_extended and middle_extended and other_curled

    def is_pointing_gesture(self, hand_points, body_landmarks=None):
        """
        Detect pointing gesture.
        """
        # Check if index finger is extended and other fingers are curled
        index_extended = self.is_finger_extended(hand_points, 5, 8)
        middle_curled = not self.is_finger_extended(hand_points, 9, 12)
        other_curled = all([
            not self.is_finger_extended(hand_points, 1, 4),   # Thumb
            not self.is_finger_extended(hand_points, 13, 16), # Ring finger
            not self.is_finger_extended(hand_points, 17, 20)  # Pinky
        ])

        return index_extended and middle_curled and other_curled

    def is_come_here_gesture(self, hand_points, body_landmarks=None):
        """
        Detect "come here" gesture (palm facing toward robot with fingers moving).
        """
        # Check if palm is facing toward robot (simplified)
        wrist = hand_points[0]
        index_mcp = hand_points[5]
        pinky_mcp = hand_points[17]
        index_tip = hand_points[8]
        pinky_tip = hand_points[20]

        # Calculate palm direction
        palm_direction = (index_mcp + pinky_mcp) / 2 - wrist
        palm_direction = palm_direction / (np.linalg.norm(palm_direction) + 1e-6)

        # Check if palm is facing robot (negative x direction in robot frame)
        # This assumes robot coordinate system - in practice would need proper calibration
        return True  # Simplified for example

    def is_stop_gesture(self, hand_points, body_landmarks=None):
        """
        Detect stop gesture (open palm facing robot).
        """
        # Check if all fingers are extended and palm is facing robot
        fingers_extended = all([
            self.is_finger_extended(hand_points, 5, 8),   # Index
            self.is_finger_extended(hand_points, 9, 12), # Middle
            self.is_finger_extended(hand_points, 13, 16), # Ring
            self.is_finger_extended(hand_points, 17, 20)  # Pinky
        ])

        thumb_position = hand_points[4]
        wrist = hand_points[0]
        thumb_extended = np.linalg.norm(thumb_position - wrist) > 0.1  # Thumb extended

        return fingers_extended and thumb_extended

    def is_follow_me_gesture(self, hand_points, body_landmarks=None):
        """
        Detect follow me gesture (pointing in a direction).
        """
        return self.is_pointing_gesture(hand_points, body_landmarks)

    def is_help_gesture(self, hand_points, body_landmarks=None):
        """
        Detect help gesture (both hands raised or waving).
        """
        # This would typically require seeing both hands in a specific configuration
        return False  # Simplified for example

    def is_finger_extended(self, hand_points, start_idx, end_idx):
        """
        Check if finger is extended by comparing tip position to base.
        """
        base = hand_points[start_idx - 1]  # MCP joint
        tip = hand_points[end_idx]        # Tip joint

        # Calculate if finger is extended (tip is significantly away from base)
        distance = np.linalg.norm(tip[:2] - base[:2])  # Only x,y for 2D gesture
        return distance > 0.1  # Threshold for extension

    def calculate_gesture_confidence(self, gesture_name, hand_points):
        """
        Calculate confidence for gesture recognition.
        """
        # This would use machine learning model in practice
        # For this example, return fixed confidence based on gesture type
        return 0.8

    def estimate_gesture_location(self, hand_landmarks, body_landmarks):
        """
        Estimate 3D location of gesture.
        """
        # In practice, this would use stereo vision or depth information
        # For this example, return a simplified location
        if body_landmarks:
            # Use body pose to estimate location
            nose = body_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            return [nose.x, nose.y, nose.z]
        else:
            # Use hand position as estimate
            wrist = hand_landmarks.landmark[0]
            return [wrist.x, wrist.y, wrist.z]

    def process_gesture_history(self, current_gesture):
        """
        Process gesture history for temporal pattern recognition.
        """
        self.gesture_history.append(current_gesture)

        # Look for gesture sequences that have meaning
        if len(self.gesture_history) >= 2:
            last_gestures = [g['type'] for g in list(self.gesture_history)[-3:]]

            # Example: Wave twice means "hello"
            if last_gestures[-2:] == ['wave', 'wave']:
                return {'type': 'hello_sequence', 'confidence': 0.9}

            # Example: Point then wave means "attention"
            if len(last_gestures) >= 2 and last_gestures[-2] == 'point' and last_gestures[-1] == 'wave':
                return {'type': 'attention_sequence', 'confidence': 0.85}

        return current_gesture
```

### Robot Gesture Generation

```python
class RobotGestureGenerator:
    def __init__(self, robot_model):
        self.robot = robot_model
        self.gesture_library = self.create_gesture_library()

    def create_gesture_library(self):
        """
        Create library of predefined robot gestures.
        """
        return {
            'wave': self.generate_wave_gesture,
            'nod': self.generate_nod_gesture,
            'shake_head': self.generate_shake_head_gesture,
            'point': self.generate_point_gesture,
            'beckon': self.generate_beckon_gesture,
            'stop': self.generate_stop_gesture,
            'think': self.generate_thinking_gesture,
            'agree': self.generate_agreement_gesture,
            'disagree': self.generate_disagreement_gesture,
            'celebrate': self.generate_celebration_gesture
        }

    def generate_wave_gesture(self, duration=2.0, amplitude=0.3, frequency=1.0):
        """
        Generate waving gesture with arm.

        Args:
            duration: Duration of gesture in seconds
            amplitude: Amplitude of waving motion
            frequency: Frequency of waving motion

        Returns:
            trajectory: Joint trajectory for waving
        """
        n_points = int(duration * 100)  # 100 Hz
        dt = duration / n_points

        trajectory = []

        # Use right arm for waving (or left if preferred)
        arm_joints = ['right_shoulder_pitch', 'right_shoulder_roll', 'right_elbow_pitch',
                     'right_wrist_yaw', 'right_wrist_pitch']

        for i in range(n_points + 1):
            t = i * dt
            progress = t / duration

            # Create waving motion using sinusoidal functions
            wave_motion = amplitude * math.sin(2 * math.pi * frequency * t)

            # Set arm joints for waving position
            joint_positions = []
            for joint_idx, joint_name in enumerate(arm_joints):
                if joint_idx == 0:  # Shoulder pitch - raise arm
                    pos = 0.5 + 0.2 * math.sin(2 * math.pi * frequency/2 * t)
                elif joint_idx == 1:  # Shoulder roll - position arm
                    pos = 0.5
                elif joint_idx == 2:  # Elbow pitch - bend elbow
                    pos = 1.0
                elif joint_idx == 3:  # Wrist yaw - waving motion
                    pos = wave_motion
                elif joint_idx == 4:  # Wrist pitch - supplementary motion
                    pos = 0.2 * math.sin(2 * math.pi * frequency * t)
                else:
                    pos = 0.0  # Default position

                joint_positions.append(pos)

            trajectory.append({
                'time': t,
                'joint_positions': joint_positions,
                'joint_names': arm_joints
            })

        return trajectory

    def generate_nod_gesture(self, n_nods=3, duration=3.0):
        """
        Generate nodding gesture for agreement.
        """
        n_points = int(duration * 100)  # 100 Hz
        dt = duration / n_points

        trajectory = []

        # Use neck joints for nodding
        neck_joints = ['neck_pitch']

        for i in range(n_points + 1):
            t = i * dt
            progress = t / duration

            # Create nodding motion
            nod_amplitude = 0.3
            nod_frequency = n_nods / duration
            nod_motion = nod_amplitude * math.sin(2 * math.pi * nod_frequency * t)

            joint_positions = [nod_motion]  # Only neck pitch moves

            trajectory.append({
                'time': t,
                'joint_positions': joint_positions,
                'joint_names': neck_joints
            })

        return trajectory

    def generate_point_gesture(self, target_position=None, duration=2.0):
        """
        Generate pointing gesture toward target.

        Args:
            target_position: [x, y, z] target position in robot frame (None for forward)
            duration: Duration of gesture in seconds
        """
        n_points = int(duration * 100)  # 100 Hz
        dt = duration / n_points

        trajectory = []

        # Use right arm for pointing
        arm_joints = ['right_shoulder_pitch', 'right_shoulder_roll', 'right_elbow_pitch',
                     'right_wrist_yaw', 'right_wrist_pitch']

        # Calculate pointing angles based on target
        if target_position is not None:
            # Calculate angles to point at target
            x, y, z = target_position
            distance = math.sqrt(x**2 + y**2 + z**2)

            if distance > 0.1:  # Valid target
                azimuth = math.atan2(y, x)
                elevation = math.atan2(z, math.sqrt(x**2 + y**2))
            else:
                # Default forward pointing
                azimuth = 0.0
                elevation = 0.0
        else:
            # Default forward pointing
            azimuth = 0.0
            elevation = 0.0

        for i in range(n_points + 1):
            t = i * dt
            progress = t / duration

            # Smooth interpolation to pointing position
            smooth_progress = 6*progress**5 - 15*progress**4 + 10*progress**3

            joint_positions = []
            for joint_idx, joint_name in enumerate(arm_joints):
                if joint_idx == 0:  # Shoulder pitch
                    pos = smooth_progress * (0.3 + elevation)  # Raise arm based on elevation
                elif joint_idx == 1:  # Shoulder roll
                    pos = smooth_progress * (0.2 + azimuth)   # Position arm based on azimuth
                elif joint_idx == 2:  # Elbow pitch
                    pos = smooth_progress * 1.5  # Fully extend elbow
                elif joint_idx == 3:  # Wrist yaw
                    pos = smooth_progress * 0.0  # Keep wrist neutral
                elif joint_idx == 4:  # Wrist pitch
                    pos = smooth_progress * 0.0  # Keep wrist neutral
                else:
                    pos = 0.0

                joint_positions.append(pos)

            trajectory.append({
                'time': t,
                'joint_positions': joint_positions,
                'joint_names': arm_joints
            })

        return trajectory

    def generate_beckon_gesture(self, duration=3.0):
        """
        Generate beckoning gesture to come closer.
        """
        n_points = int(duration * 100)  # 100 Hz
        dt = duration / n_points

        trajectory = []

        # Use right arm with fingers extended
        arm_joints = ['right_shoulder_pitch', 'right_shoulder_roll', 'right_elbow_pitch',
                     'right_wrist_yaw', 'right_wrist_pitch']

        for i in range(n_points + 1):
            t = i * dt
            progress = t / duration

            # Create beckoning motion (arm extended, fingers moving)
            joint_positions = []
            for joint_idx, joint_name in enumerate(arm_joints):
                if joint_idx == 0:  # Shoulder pitch - extend arm forward
                    pos = 0.2
                elif joint_idx == 1:  # Shoulder roll - position arm
                    pos = 0.8
                elif joint_idx == 2:  # Elbow pitch - keep arm extended
                    pos = 0.0
                elif joint_idx == 3:  # Wrist yaw - beckoning motion
                    pos = 0.3 * math.sin(2 * math.pi * 2 * t)  # Faster waving motion
                elif joint_idx == 4:  # Wrist pitch - slight variation
                    pos = 0.1 * math.sin(2 * math.pi * 1.5 * t)
                else:
                    pos = 0.0

                joint_positions.append(pos)

            trajectory.append({
                'time': t,
                'joint_positions': joint_positions,
                'joint_names': arm_joints
            })

        return trajectory

    def generate_thinking_gesture(self, duration=3.0):
        """
        Generate thinking gesture (touching chin, looking up, etc.).
        """
        n_points = int(duration * 100)  # 100 Hz
        dt = duration / n_points

        trajectory = []

        # Use neck and left arm for thinking gesture
        gesture_joints = ['neck_pitch', 'neck_yaw', 'left_shoulder_pitch',
                         'left_shoulder_roll', 'left_elbow_pitch']

        for i in range(n_points + 1):
            t = i * dt
            progress = t / duration

            # Smooth interpolation with thinking motion
            smooth_progress = 6*progress**5 - 15*progress**4 + 10*progress**3

            joint_positions = []
            for joint_idx, joint_name in enumerate(gesture_joints):
                if joint_idx == 0:  # Neck pitch - look up slightly then down
                    pos = -0.1 + 0.2 * math.sin(2 * math.pi * 0.5 * t)
                elif joint_idx == 1:  # Neck yaw - slight head turning
                    pos = 0.1 * math.sin(2 * math.pi * 0.3 * t)
                elif joint_idx == 2:  # Left shoulder pitch - raise hand to chin
                    pos = 0.3 + 0.4 * smooth_progress
                elif joint_idx == 3:  # Left shoulder roll - position hand
                    pos = 0.5
                elif joint_idx == 4:  # Left elbow pitch - bend elbow
                    pos = 1.5 * smooth_progress
                else:
                    pos = 0.0

                joint_positions.append(pos)

            trajectory.append({
                'time': t,
                'joint_positions': joint_positions,
                'joint_names': gesture_joints
            })

        return trajectory

    def execute_gesture(self, gesture_name, **kwargs):
        """
        Execute a specific gesture on the robot.

        Args:
            gesture_name: Name of gesture to execute
            **kwargs: Additional parameters for the gesture

        Returns:
            success: Boolean indicating if gesture was executed successfully
        """
        if gesture_name not in self.gesture_library:
            self.get_logger().error(f'Unknown gesture: {gesture_name}')
            return False

        # Generate gesture trajectory
        trajectory = self.gesture_library[gesture_name](**kwargs)

        if not trajectory:
            self.get_logger().error(f'Could not generate trajectory for gesture: {gesture_name}')
            return False

        # Execute trajectory
        success = self.execute_trajectory(trajectory)

        if success:
            self.get_logger().info(f'Executed gesture: {gesture_name}')
        else:
            self.get_logger().error(f'Failed to execute gesture: {gesture_name}')

        return success

    def execute_trajectory(self, trajectory):
        """
        Execute joint trajectory on robot.
        """
        for point in trajectory:
            # Send joint positions to robot
            joint_msg = JointTrajectory()
            joint_msg.header.stamp = self.get_clock().now().to_msg()
            joint_msg.header.frame_id = 'base_link'
            joint_msg.joint_names = point['joint_names']

            trajectory_point = JointTrajectoryPoint()
            trajectory_point.positions = point['joint_positions']
            trajectory_point.time_from_start = Duration(sec=int(point['time']), nanosec=int((point['time'] % 1) * 1e9))

            joint_msg.points = [trajectory_point]

            # Publish trajectory
            self.joint_trajectory_pub.publish(joint_msg)

            # Wait for appropriate time
            time.sleep(0.01)  # 100 Hz

        return True

    def combine_gestures(self, gesture_sequence, timing_offsets=None):
        """
        Combine multiple gestures into a sequence.

        Args:
            gesture_sequence: List of gesture names to combine
            timing_offsets: Optional list of timing offsets between gestures

        Returns:
            combined_trajectory: Combined joint trajectory
        """
        if timing_offsets is None:
            timing_offsets = [1.0] * len(gesture_sequence)  # 1 second between gestures

        combined_trajectory = []
        current_time = 0.0

        for gesture_name, offset in zip(gesture_sequence, timing_offsets):
            if gesture_name in self.gesture_library:
                gesture_traj = self.gesture_library[gesture_name](duration=2.0)  # Default duration

                # Adjust timing for combined sequence
                for point in gesture_traj:
                    point['time'] += current_time
                    combined_trajectory.append(point)

                current_time += 2.0 + offset  # Gesture duration + offset

        return combined_trajectory
```

## Emotional Expression and Personality

### Emotional State Management

```python
class EmotionalStateController:
    def __init__(self):
        # Emotional state variables
        self.current_emotion = 'neutral'
        self.emotion_intensity = 0.5
        self.emotion_duration = 0.0
        self.emotion_decay_rate = 0.01

        # Personality traits
        self.personality_traits = {
            'extraversion': 0.6,
            'agreeableness': 0.8,
            'conscientiousness': 0.7,
            'emotional_stability': 0.7,
            'openness': 0.6
        }

        # Emotional expression mappings
        self.emotion_expressions = {
            'happy': {
                'facial': 'smile',
                'posture': 'upright',
                'gesture': ['wave', 'nod'],
                'voice': 'upbeat',
                'gaze': 'engaged'
            },
            'sad': {
                'facial': 'frown',
                'posture': 'slouched',
                'gesture': ['head_down', 'slow_movement'],
                'voice': 'soothing',
                'gaze': 'avoiding'
            },
            'angry': {
                'facial': 'frown',
                'posture': 'rigid',
                'gesture': ['stop', 'sharp_moves'],
                'voice': 'firm',
                'gaze': 'direct'
            },
            'surprised': {
                'facial': 'wide_eyes',
                'posture': 'upright',
                'gesture': ['raise_eyebrows', 'step_back'],
                'voice': 'varied',
                'gaze': 'focused'
            },
            'excited': {
                'facial': 'bright_eyes',
                'posture': 'energetic',
                'gesture': ['wave', 'point'],
                'voice': 'enthusiastic',
                'gaze': 'animated'
            },
            'neutral': {
                'facial': 'normal',
                'posture': 'natural',
                'gesture': 'controlled',
                'voice': 'steady',
                'gaze': 'appropriate'
            }
        }

        # Emotional transition rules
        self.emotion_transitions = {
            'happy': ['neutral', 'excited'],
            'sad': ['neutral', 'concerned'],
            'angry': ['neutral', 'frustrated'],
            'surprised': ['neutral', 'interested'],
            'excited': ['happy', 'neutral'],
            'neutral': ['happy', 'sad', 'interested'],
            'concerned': ['neutral', 'helpful'],
            'frustrated': ['neutral', 'apologetic'],
            'interested': ['neutral', 'engaged']
        }

    def update_emotional_state(self, trigger_event, intensity=0.5, duration=5.0):
        """
        Update emotional state based on trigger event.

        Args:
            trigger_event: Event that triggers emotional response
            intensity: Intensity of emotional response (0.0 to 1.0)
            duration: Duration of emotional state in seconds
        """
        # Determine new emotion based on trigger
        new_emotion = self.determine_emotion_from_event(trigger_event)

        if new_emotion:
            # Update emotional state
            self.current_emotion = new_emotion
            self.emotion_intensity = intensity
            self.emotion_duration = duration
            self.emotion_start_time = time.time()

            self.get_logger().info(f'Emotional state updated: {new_emotion} (intensity: {intensity})')

    def determine_emotion_from_event(self, event):
        """
        Determine appropriate emotion from triggering event.
        """
        event_lower = event.lower()

        # Map events to emotions
        if any(word in event_lower for word in ['good', 'great', 'excellent', 'wonderful', 'fantastic']):
            return 'happy'
        elif any(word in event_lower for word in ['bad', 'terrible', 'awful', 'sad', 'unfortunate']):
            return 'sad'
        elif any(word in event_lower for word in ['angry', 'frustrated', 'annoying', 'mad']):
            return 'angry'
        elif any(word in event_lower for word in ['surprise', 'wow', 'amazing', 'incredible']):
            return 'surprised'
        elif any(word in event_lower for word in ['exciting', 'excited', 'awesome', 'cool']):
            return 'excited'
        else:
            return 'neutral'

    def get_current_emotional_expression(self):
        """
        Get current emotional expression based on emotional state.
        """
        if self.current_emotion in self.emotion_expressions:
            expression = self.emotion_expressions[self.current_emotion].copy()

            # Adjust based on intensity
            expression['intensity'] = self.emotion_intensity

            # Apply personality modifications
            expression = self.apply_personality_modifications(expression)

            # Check if emotion should decay
            elapsed = time.time() - self.emotion_start_time
            if elapsed > self.emotion_duration:
                # Emotion has expired, transition to neutral
                self.current_emotion = 'neutral'
                self.emotion_intensity = max(0.0, self.emotion_intensity - self.emotion_decay_rate)

            return expression

        return self.emotion_expressions['neutral']

    def apply_personality_modifications(self, expression):
        """
        Apply personality-based modifications to emotional expression.
        """
        # Adjust expression based on personality traits
        if self.personality_traits['extraversion'] > 0.7:
            # More expressive personality
            expression['intensity'] = min(1.0, expression['intensity'] * 1.2)
            if 'gesture' in expression:
                expression['gesture'].append('animated')
        elif self.personality_traits['extraversion'] < 0.3:
            # Less expressive personality
            expression['intensity'] = max(0.1, expression['intensity'] * 0.8)

        if self.personality_traits['agreeableness'] > 0.8:
            # More agreeable personality - soften expressions
            if self.current_emotion == 'angry':
                expression['intensity'] = max(0.1, expression['intensity'] * 0.5)

        if self.personality_traits['conscientiousness'] > 0.8:
            # More careful personality - more controlled gestures
            if 'gesture' in expression:
                expression['gesture'] = [g for g in expression['gesture'] if g not in ['sharp_moves', 'sudden']]

        return expression

    def express_emotion(self, emotion, intensity=0.5, duration=3.0):
        """
        Express a specific emotion through facial expression, gestures, and voice.

        Args:
            emotion: Emotion to express ('happy', 'sad', 'angry', 'surprised', etc.)
            intensity: Intensity of expression (0.0 to 1.0)
            duration: Duration of expression in seconds
        """
        if emotion not in self.emotion_expressions:
            self.get_logger().warn(f'Unknown emotion: {emotion}')
            return False

        # Update emotional state
        self.update_emotional_state(f'express_{emotion}', intensity, duration)

        # Generate appropriate expressions
        expression = self.emotion_expressions[emotion]

        # Apply facial expression
        self.apply_facial_expression(expression['facial'], intensity)

        # Apply posture
        self.apply_posture(expression['posture'], intensity)

        # Execute gesture
        if expression.get('gesture'):
            for gesture in expression['gesture']:
                self.execute_gesture(gesture, duration=duration/len(expression['gesture']))

        # Adjust voice characteristics
        self.adjust_voice_characteristics(expression['voice'], intensity)

        # Adjust gaze behavior
        self.adjust_gaze_behavior(expression['gaze'])

        return True

    def apply_facial_expression(self, expression_type, intensity):
        """
        Apply facial expression to robot's face display.
        """
        # This would control the robot's facial display system
        # For this example, we'll just log the expression
        self.get_logger().info(f'Applying facial expression: {expression_type} at intensity {intensity}')

    def apply_posture(self, posture_type, intensity):
        """
        Apply posture modification to robot's stance.
        """
        # This would adjust the robot's overall posture
        self.get_logger().info(f'Adjusting posture: {posture_type} at intensity {intensity}')

    def adjust_voice_characteristics(self, voice_type, intensity):
        """
        Adjust voice synthesis characteristics.
        """
        # This would modify speech synthesis parameters
        self.get_logger().info(f'Adjusting voice: {voice_type} at intensity {intensity}')

    def adjust_gaze_behavior(self, gaze_type):
        """
        Adjust gaze behavior based on emotion.
        """
        gaze_modes = {
            'engaged': 'follow_interlocutor',
            'avoiding': 'periodic_breaks',
            'direct': 'maintain_eye_contact',
            'focused': 'attend_to_speaker',
            'animated': 'dynamic_scanning'
        }

        if gaze_type in gaze_modes:
            self.gaze_controller.set_behavior(gaze_modes[gaze_type])
```

## Social Interaction Management

### Turn-Taking and Conversation Flow

```python
class SocialInteractionManager:
    def __init__(self):
        # Conversation state
        self.conversation_state = 'idle'
        self.interaction_queue = deque()
        self.current_interlocutor = None
        self.interaction_timers = {}

        # Turn-taking parameters
        self.turn_timeout = 5.0  # seconds before robot takes turn
        self.response_delay = 0.5  # seconds before responding
        self.gesture_delay = 0.2   # seconds before gesture response

        # Social behavior parameters
        self.waiting_behavior = 'polite_attention'
        self.interruption_handling = 'graceful_transition'
        self.multiple_person_handling = 'inclusive_attention'

    def start_interaction(self, user_id, interaction_type='conversation'):
        """
        Start interaction with user.

        Args:
            user_id: Unique identifier for user
            interaction_type: Type of interaction ('conversation', 'task', 'greeting')
        """
        if self.current_interlocutor is None:
            # No current interaction, start directly
            self.current_interlocutor = user_id
            self.conversation_state = 'active'
            self.interaction_timers[user_id] = time.time()

            # Apply appropriate social behavior
            self.apply_social_behavior(interaction_type)

            self.get_logger().info(f'Started interaction with user: {user_id}')
            return True
        else:
            # Queue interaction
            self.interaction_queue.append({
                'user_id': user_id,
                'type': interaction_type,
                'timestamp': time.time()
            })

            self.get_logger().info(f'Queued interaction for user: {user_id}')
            return False

    def apply_social_behavior(self, interaction_type):
        """
        Apply appropriate social behavior based on interaction type.
        """
        behaviors = {
            'greeting': {
                'gaze': 'direct',
                'posture': 'open',
                'gesture': 'wave',
                'voice': 'warm'
            },
            'conversation': {
                'gaze': 'engaged',
                'posture': 'attentive',
                'gesture': 'responsive',
                'voice': 'conversational'
            },
            'task': {
                'gaze': 'focused',
                'posture': 'professional',
                'gesture': 'precise',
                'voice': 'clear'
            }
        }

        if interaction_type in behaviors:
            behavior = behaviors[interaction_type]

            # Apply behavior parameters
            self.gaze_controller.set_behavior(behavior['gaze'])
            self.posture_controller.set_posture(behavior['posture'])
            self.voice_controller.set_voice_style(behavior['voice'])

    def process_speech_input(self, speech_data, user_id):
        """
        Process speech input and determine appropriate response.

        Args:
            speech_data: Recognized speech text
            user_id: User who spoke
        """
        if user_id != self.current_interlocutor and self.current_interlocutor is not None:
            # Handle interruption
            if self.can_interrupt_current_interaction():
                self.interrupt_current_interaction(user_id)
            else:
                # Acknowledge but wait
                self.acknowledge_user_waiting(user_id)
                return

        # Process the speech input
        intent = self.classify_intent(speech_data)
        entities = self.extract_entities(speech_data)

        # Generate appropriate response
        response = self.generate_response(intent, entities, user_id)

        # Execute response
        self.execute_response(response, user_id)

    def classify_intent(self, text):
        """
        Classify intent of user speech.
        """
        # This would use NLP models in practice
        # For this example, use simple keyword matching
        text_lower = text.lower()

        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(word in text_lower for word in ['help', 'assist', 'can you', 'could you']):
            return 'request'
        elif any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why']):
            return 'question'
        elif any(word in text_lower for word in ['goodbye', 'bye', 'see you']):
            return 'farewell'
        elif any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
            return 'gratitude'
        else:
            return 'statement'

    def extract_entities(self, text):
        """
        Extract entities from user speech.
        """
        # This would use NLP models in practice
        # For this example, return simple location and object entities
        entities = {
            'location': [],
            'object': [],
            'person': [],
            'time': []
        }

        # Simple keyword-based entity extraction
        words = text.lower().split()
        locations = ['kitchen', 'office', 'bedroom', 'living room', 'bathroom', 'hallway']
        objects = ['cup', 'bottle', 'book', 'ball', 'box', 'pen', 'phone', 'computer']

        for word in words:
            if word in locations:
                entities['location'].append(word)
            elif word in objects:
                entities['object'].append(word)

        return entities

    def generate_response(self, intent, entities, user_id):
        """
        Generate appropriate response based on intent and entities.
        """
        responses = {
            'greeting': [
                f"Hello {user_id}! How can I assist you today?",
                f"Hi there! It's nice to see you.",
                f"Greetings! What brings you here?"
            ],
            'request': [
                f"I can help with that. Could you be more specific?",
                f"What exactly would you like me to do?",
                f"I'm ready to assist. Please tell me more."
            ],
            'question': [
                f"That's an interesting question about {entities.get('object', ['something'])[0] if entities['object'] else 'that'}.",
                f"I'd be happy to answer your question.",
                f"Let me think about that for you."
            ],
            'farewell': [
                f"Goodbye {user_id}! It was nice talking with you.",
                f"See you later! Have a great day.",
                f"Farewell! Feel free to come back anytime."
            ],
            'gratitude': [
                "You're welcome! I'm happy to help.",
                "No problem! I enjoy assisting.",
                "Thank you for the appreciation!"
            ],
            'statement': [
                f"I understand you're saying: {text[:50]}...",
                f"Interesting! Tell me more about that.",
                f"Thanks for sharing that with me."
            ]
        }

        import random
        response_list = responses.get(intent, responses['statement'])
        return random.choice(response_list)

    def execute_response(self, response_text, user_id):
        """
        Execute response including speech, gestures, and expressions.
        """
        # Speak the response
        self.speech_controller.speak(response_text)

        # Apply appropriate gesture based on response content
        gesture = self.select_appropriate_gesture(response_text)
        if gesture:
            self.gesture_generator.execute_gesture(gesture, duration=2.0)

        # Apply appropriate emotional expression
        emotion = self.determine_response_emotion(response_text)
        self.emotional_controller.express_emotion(emotion, intensity=0.6)

        # Update interaction timer
        self.interaction_timers[user_id] = time.time()

    def select_appropriate_gesture(self, response_text):
        """
        Select appropriate gesture based on response content.
        """
        text_lower = response_text.lower()

        if 'hello' in text_lower or 'hi' in text_lower:
            return 'wave'
        elif 'think' in text_lower or 'consider' in text_lower:
            return 'think'
        elif 'help' in text_lower or 'assist' in text_lower:
            return 'beckon'
        elif 'stop' in text_lower:
            return 'stop'
        elif 'yes' in text_lower or 'agree' in text_lower:
            return 'nod'
        elif 'no' in text_lower or 'disagree' in text_lower:
            return 'shake_head'
        else:
            return 'polite_attention'  # Default gesture

    def determine_response_emotion(self, response_text):
        """
        Determine appropriate emotion for response.
        """
        text_lower = response_text.lower()

        if 'happy' in text_lower or 'great' in text_lower or 'wonderful' in text_lower:
            return 'happy'
        elif 'concern' in text_lower or 'worry' in text_lower:
            return 'concerned'
        elif 'think' in text_lower or 'consider' in text_lower:
            return 'thoughtful'
        elif 'thank' in text_lower:
            return 'appreciative'
        else:
            return 'neutral'

    def can_interrupt_current_interaction(self):
        """
        Determine if current interaction can be interrupted.
        """
        # Check if current interaction is low-priority
        current_duration = time.time() - self.interaction_timers.get(self.current_interlocutor, time.time())

        # Allow interruption if current interaction is long or if it's a high-priority request
        return current_duration > 30.0  # Allow interruption after 30 seconds

    def interrupt_current_interaction(self, new_user_id):
        """
        Interrupt current interaction and switch to new user.
        """
        old_user = self.current_interlocutor
        self.current_interlocutor = new_user_id

        self.get_logger().info(f'Interrupted interaction with {old_user}, switching to {new_user_id}')

        # Acknowledge new user
        self.speech_controller.speak(f"Excuse me {old_user}, I'll be right with you.")
        self.speech_controller.speak(f"Hello {new_user_id}, how can I help you?")

    def acknowledge_user_waiting(self, user_id):
        """
        Acknowledge that user is waiting for interaction.
        """
        if user_id not in [item['user_id'] for item in self.interaction_queue]:
            self.interaction_queue.append({
                'user_id': user_id,
                'type': 'waiting_acknowledgment',
                'timestamp': time.time()
            })

        # Brief acknowledgment
        self.speech_controller.speak("I see you're waiting. I'll be with you shortly.")
        self.gesture_generator.execute_gesture('wave', duration=1.0)

    def manage_multiple_interactions(self):
        """
        Manage interactions when multiple people are present.
        """
        if len(self.interaction_queue) > 0 and self.conversation_state == 'idle':
            # Process queued interactions
            next_interaction = self.interaction_queue.popleft()
            self.start_interaction(next_interaction['user_id'], next_interaction['type'])

        # Handle multiple people in current interaction
        if self.current_interlocutor and len(self.tracked_people) > 1:
            # Apply inclusive attention behavior
            self.apply_inclusive_attention()

    def apply_inclusive_attention(self):
        """
        Apply attention behavior that includes multiple people.
        """
        # Alternate gaze between people
        if hasattr(self, 'gaze_controller'):
            self.gaze_controller.handle_multiple_people(list(self.tracked_people.values()))

        # Use gestures that acknowledge everyone
        if hasattr(self, 'gesture_generator'):
            self.gesture_generator.execute_gesture('wave_to_group', duration=3.0)

        # Adjust speech to address group
        if hasattr(self, 'speech_controller'):
            self.speech_controller.set_group_addressing(True)

    def end_interaction(self, user_id):
        """
        End interaction with specific user.
        """
        if self.current_interlocutor == user_id:
            self.current_interlocutor = None
            self.conversation_state = 'idle'

            # Apply farewell behavior
            self.apply_farewell_behavior()

            # Process next in queue if available
            if self.interaction_queue:
                next_interaction = self.interaction_queue.popleft()
                self.start_interaction(next_interaction['user_id'], next_interaction['type'])

    def apply_farewell_behavior(self):
        """
        Apply appropriate behavior when ending interaction.
        """
        # Reduce gaze intensity
        if hasattr(self, 'gaze_controller'):
            self.gaze_controller.set_behavior('polite_attention')

        # Apply neutral posture
        if hasattr(self, 'posture_controller'):
            self.posture_controller.set_posture('neutral')

        # Apply neutral emotional state
        if hasattr(self, 'emotional_controller'):
            self.emotional_controller.express_emotion('neutral', intensity=0.3)

    def get_interaction_status(self):
        """
        Get current interaction status.
        """
        return {
            'current_interlocutor': self.current_interlocutor,
            'conversation_state': self.conversation_state,
            'queue_size': len(self.interaction_queue),
            'active_interactions': len(self.interaction_timers),
            'last_interaction_time': max(self.interaction_timers.values(), default=0)
        }
```

## Integration Example

### Complete HRI System Integration

```python
class HumanoidHRIIntegrator:
    def __init__(self):
        # Initialize all HRI components
        self.hri_controller = HumanoidHRIController()
        self.gaze_controller = GazeController()
        self.gesture_recognizer = HumanGestureRecognizer()
        self.gesture_generator = RobotGestureGenerator()
        self.emotional_controller = EmotionalStateController()
        self.social_manager = SocialInteractionManager()

        # Initialize with robot model
        self.robot_model = None  # Would be passed in or loaded

    def setup_hri_system(self, robot_model):
        """
        Setup complete HRI system with robot model.
        """
        self.robot_model = robot_model
        self.gesture_generator = RobotGestureGenerator(robot_model)

        # Initialize all controllers with robot model
        self.hri_controller.robot_model = robot_model
        self.social_manager.robot_model = robot_model

        self.get_logger().info('Complete HRI system initialized')

    def process_human_interaction(self, sensor_data):
        """
        Process complete human interaction cycle.

        Args:
            sensor_data: Dictionary with sensor inputs (camera, audio, etc.)

        Returns:
            interaction_response: Complete interaction response
        """
        # Step 1: Recognize human gestures and expressions
        if 'camera' in sensor_data:
            gestures = self.gesture_recognizer.recognize_human_gestures(sensor_data['camera'])
            if gestures:
                self.process_recognized_gestures(gestures)

        # Step 2: Process speech input
        if 'audio' in sensor_data:
            speech_text = self.speech_recognizer.recognize_speech(sensor_data['audio'])
            if speech_text:
                self.process_speech_input(speech_text, sensor_data.get('speaker_id', 'unknown'))

        # Step 3: Update social interaction state
        self.social_manager.manage_multiple_interactions()

        # Step 4: Generate appropriate response
        response = self.generate_integrated_response(sensor_data)

        # Step 5: Execute response (speech, gesture, expression)
        self.execute_integrated_response(response)

        return response

    def process_recognized_gestures(self, gestures):
        """
        Process recognized human gestures.
        """
        for gesture in gestures:
            gesture_type = gesture['type']
            confidence = gesture['confidence']

            if confidence > 0.7:  # High confidence gesture
                if gesture_type == 'wave':
                    self.handle_greeting_gesture(gesture)
                elif gesture_type == 'point':
                    self.handle_pointing_gesture(gesture)
                elif gesture_type == 'stop':
                    self.handle_stop_gesture(gesture)
                elif gesture_type == 'come_here':
                    self.handle_come_here_gesture(gesture)

    def handle_greeting_gesture(self, gesture):
        """
        Handle greeting gesture (wave).
        """
        # Start interaction if appropriate
        user_id = gesture.get('user_id', 'unknown')
        if self.social_manager.start_interaction(user_id, 'greeting'):
            # Respond with greeting
            self.speech_controller.speak(f"Hello! I see you're waving at me.")
            self.gesture_generator.execute_gesture('wave', duration=2.0)
            self.emotional_controller.express_emotion('happy', intensity=0.8)

    def handle_pointing_gesture(self, gesture):
        """
        Handle pointing gesture.
        """
        # Update gaze to look at pointed location
        target_pos = gesture.get('location')
        if target_pos:
            self.gaze_controller.update_gaze_target(target_pos, 'location')

        # Acknowledge the gesture
        self.speech_controller.speak("I see you're pointing at something.")

    def handle_stop_gesture(self, gesture):
        """
        Handle stop gesture.
        """
        # Stop current motion
        self.stop_current_motion()

        # Acknowledge gesture
        self.speech_controller.speak("I see the stop gesture. I'm stopping.")
        self.emotional_controller.express_emotion('neutral', intensity=0.5)

    def handle_come_here_gesture(self, gesture):
        """
        Handle "come here" gesture.
        """
        user_id = gesture.get('user_id', 'unknown')

        # Approach the user
        self.start_approach_behavior(user_id)

        # Respond verbally
        self.speech_controller.speak("I'm coming over to you.")
        self.emotional_controller.express_emotion('engaged', intensity=0.7)

    def generate_integrated_response(self, sensor_data):
        """
        Generate integrated response combining multiple modalities.
        """
        response = {
            'speech': '',
            'gesture': '',
            'facial_expression': '',
            'gaze_target': None,
            'emotional_state': 'neutral'
        }

        # Analyze context from all sensor data
        context = self.analyze_interaction_context(sensor_data)

        # Determine appropriate response based on context
        if context['human_attention'] > 0.8:
            response['emotional_state'] = 'engaged'
            response['gaze_target'] = context['attention_location']
        elif context['greeting_detected']:
            response['speech'] = "Hello! It's nice to meet you."
            response['gesture'] = 'wave'
            response['emotional_state'] = 'happy'
        elif context['help_requested']:
            response['speech'] = "I can help with that. What specifically do you need?"
            response['gesture'] = 'beckon'
            response['emotional_state'] = 'helpful'

        return response

    def execute_integrated_response(self, response):
        """
        Execute complete integrated response.
        """
        # Execute speech
        if response['speech']:
            self.speech_controller.speak(response['speech'])

        # Execute gesture
        if response['gesture']:
            self.gesture_generator.execute_gesture(response['gesture'])

        # Execute facial expression
        if response['facial_expression']:
            self.emotional_controller.apply_facial_expression(
                response['facial_expression'], intensity=0.8
            )

        # Execute gaze behavior
        if response['gaze_target']:
            self.gaze_controller.update_gaze_target(response['gaze_target'])

        # Execute emotional expression
        if response['emotional_state']:
            self.emotional_controller.express_emotion(response['emotional_state'])

    def analyze_interaction_context(self, sensor_data):
        """
        Analyze interaction context from all sensor data.
        """
        context = {
            'human_attention': 0.0,
            'attention_location': None,
            'greeting_detected': False,
            'help_requested': False,
            'current_user_familiarity': 0.0,
            'social_distance': 1.0,
            'emotional_state': 'neutral'
        }

        # Analyze from camera data
        if 'camera' in sensor_data:
            # Check for eye contact
            eye_contact_detected = self.detect_eye_contact(sensor_data['camera'])
            if eye_contact_detected:
                context['human_attention'] = 0.9
                context['attention_location'] = eye_contact_detected['location']

            # Check for greeting gestures
            gestures = self.gesture_recognizer.recognize_human_gestures(sensor_data['camera'])
            for gesture in gestures:
                if gesture['type'] == 'wave' and gesture['confidence'] > 0.7:
                    context['greeting_detected'] = True

        # Analyze from audio data
        if 'audio' in sensor_data:
            speech_text = sensor_data['audio'].get('text', '')
            if any(word in speech_text.lower() for word in ['help', 'please', 'can you']):
                context['help_requested'] = True

        # Analyze from proximity sensors
        if 'proximity' in sensor_data:
            distances = sensor_data['proximity'].get('distances', [])
            if distances:
                context['social_distance'] = min(distances)

        # Analyze from user tracking
        if 'user_id' in sensor_data:
            user_id = sensor_data['user_id']
            context['current_user_familiarity'] = self.hri_controller.get_user_familiarity(user_id)

        return context

    def detect_eye_contact(self, camera_data):
        """
        Detect if human is making eye contact with robot.
        """
        # This would analyze face orientation and gaze direction
        # For this example, return a simplified result
        return {
            'detected': True,
            'location': [1.0, 0.0, 1.5],  # [x, y, z] in robot frame
            'confidence': 0.8
        }

    def start_approach_behavior(self, user_id):
        """
        Start approach behavior toward user.
        """
        # Calculate approach trajectory
        user_position = self.get_user_position(user_id)
        approach_distance = self.hri_controller.calculate_appropriate_distance(
            InteractionStyle.CASUAL, user_id
        )[0]  # Get minimum distance

        # Move toward user maintaining appropriate distance
        self.navigation_controller.move_to_position(
            user_position, approach_distance
        )

    def stop_current_motion(self):
        """
        Stop current robot motion.
        """
        # Send zero velocity commands
        zero_cmd = Twist()
        self.cmd_vel_pub.publish(zero_cmd)

        # Apply zero torques to joints
        n_joints = self.robot_model.get_num_joints() if self.robot_model else 28
        zero_torques = [0.0] * n_joints
        self.apply_joint_torques(zero_torques)

    def get_user_position(self, user_id):
        """
        Get position of tracked user.
        """
        # This would interface with person tracking system
        # For this example, return a default position
        return [2.0, 0.0, 0.0]

    def apply_joint_torques(self, torques):
        """
        Apply joint torques to robot.
        """
        # Create and publish joint trajectory message
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.stamp = self.get_clock().now().to_msg()
        trajectory_msg.header.frame_id = 'base_link'

        # Set joint names based on robot model
        if self.robot_model:
            trajectory_msg.joint_names = self.robot_model.get_joint_names()
        else:
            trajectory_msg.joint_names = [f'joint_{i}' for i in range(len(torques))]

        point = JointTrajectoryPoint()
        point.positions = [0.0] * len(torques)  # Position control with PD
        point.velocities = [0.0] * len(torques)
        point.accelerations = [0.0] * len(torques)
        point.effort = torques
        point.time_from_start = Duration(sec=0, nanosec=int(10000000))  # 10ms

        trajectory_msg.points = [point]
        self.joint_trajectory_pub.publish(trajectory_msg)
```

## Summary

Human-Robot Interaction for humanoid robots involves sophisticated integration of multiple modalities including speech, gesture, gaze, and emotional expression. The key components include:

1. **Social Interaction Principles**: Following human social norms and conventions
2. **Trust and Acceptance**: Building and maintaining user trust
3. **Gesture Recognition and Generation**: Understanding and producing human-like gestures
4. **Emotional Expression**: Showing appropriate emotional responses
5. **Context Awareness**: Adapting behavior based on environmental and social context
6. **Turn-Taking**: Managing conversation flow naturally
7. **Situational Adaptation**: Adjusting interaction style based on context

These systems enable humanoid robots to interact naturally with humans in various social contexts, making them more effective and acceptable in human environments. Proper integration of these components is essential for creating robots that can work alongside humans seamlessly.