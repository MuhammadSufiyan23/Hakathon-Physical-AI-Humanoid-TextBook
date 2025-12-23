---
sidebar_label: 'Week 11: Humanoid Interaction and Communication'
title: 'Week 11: Humanoid Interaction and Communication'
---

# Week 11: Humanoid Interaction and Communication

## Introduction

Humanoid robots are designed to interact with humans in natural, intuitive ways. Effective interaction and communication are essential for humanoid robots to be accepted and useful in human environments. This week covers the fundamental concepts, technologies, and implementation approaches for creating engaging and effective human-robot interactions.

## Learning Objectives

By the end of this week, students will be able to:
- Understand the principles of human-robot interaction (HRI)
- Implement multimodal communication systems (speech, gesture, facial expressions)
- Design context-aware interaction systems
- Create emotion recognition and response mechanisms
- Implement safety and ethical considerations in HRI
- Evaluate the effectiveness of human-robot interactions

## Table of Contents
1. [Fundamentals of Human-Robot Interaction](#fundamentals-of-human-robot-interaction)
2. [Multimodal Communication Systems](#multimodal-communication-systems)
3. [Social Interaction Principles](#social-interaction-principles)
4. [Emotion Recognition and Response](#emotion-recognition-and-response)
5. [Context-Aware Interaction](#context-aware-interaction)
6. [Safety and Ethical Considerations](#safety-and-ethical-considerations)
7. [Implementation Examples](#implementation-examples)

## Fundamentals of Human-Robot Interaction

### What is Human-Robot Interaction?

Human-Robot Interaction (HRI) is a multidisciplinary field studying the design, development, and evaluation of robots for use by or with humans. HRI encompasses:

- **Physical interaction**: Direct physical contact between humans and robots
- **Social interaction**: Social behaviors, norms, and conventions
- **Cognitive interaction**: Mental models, expectations, and understanding
- **Emotional interaction**: Emotional responses and affective computing

### Key Principles of HRI

#### Predictability
Robots should behave in ways that humans can anticipate and understand:

```python
class PredictableRobotBehavior:
    def __init__(self):
        self.behavior_patterns = {
            'greeting': ['wave', 'smile', 'verbal_greeting'],
            'farewell': ['wave', 'thank_you', 'positive_expression'],
            'attention': ['head_turn', 'eye_contact', 'posture_change']
        }

    def execute_predictable_action(self, action_type, context):
        """
        Execute actions that follow predictable patterns.
        """
        if action_type in self.behavior_patterns:
            # Log the action for consistency tracking
            self.log_action(action_type, context)

            # Execute pattern consistently
            for behavior in self.behavior_patterns[action_type]:
                self.execute_behavior(behavior)

            return True
        return False

    def log_action(self, action_type, context):
        """Log actions for consistency analysis."""
        # Implementation would log to database or file
        pass
```

#### Legibility
Robot actions should clearly communicate the robot's intentions:

```python
class LegibleActionGenerator:
    def __init__(self):
        self.intention_signals = {
            'approaching': ['look_ahead', 'reduce_speed', 'annouce_intention'],
            'avoiding': ['change_direction_visibly', 'slow_down', 'acknowledge_obstacle'],
            'grasping': ['reach_slowly', 'align_hand', 'confirm_target']
        }

    def generate_legible_action(self, intended_action, environment):
        """
        Generate actions that clearly signal intentions.
        """
        if intended_action in self.intention_signals:
            # Add intention signals before main action
            for signal in self.intention_signals[intended_action]:
                self.execute_intention_signal(signal, environment)

            # Execute main action
            self.execute_main_action(intended_action)

            return True
        return False
```

#### Reciprocity
Interactions should involve mutual exchange and response:

```python
class ReciprocalInteractionManager:
    def __init__(self):
        self.interaction_state = 'idle'
        self.response_timeouts = {
            'greeting': 5.0,  # seconds
            'question': 10.0,
            'command': 3.0
        }

    def initiate_interaction(self, interaction_type):
        """Initiate interaction and wait for reciprocal response."""
        self.send_signal(interaction_type)
        self.interaction_state = f'waiting_for_response_{interaction_type}'

        # Start timeout timer
        self.start_response_timer(interaction_type)

    def receive_response(self, response):
        """Process received response and update interaction state."""
        if self.interaction_state.startswith('waiting_for_response'):
            # Reset timer
            self.cancel_response_timer()

            # Process response
            self.process_response(response)

            # Update state
            self.interaction_state = 'engaged'

            # Respond appropriately
            self.generate_reciprocal_response(response)

    def process_response_timeout(self, interaction_type):
        """Handle response timeout."""
        self.interaction_state = 'idle'

        # Implement timeout strategy
        if interaction_type == 'greeting':
            self.attempt_greeting_retry()
        elif interaction_type == 'question':
            self.offer_alternative_interaction()
```

### Proxemics in Human-Robot Interaction

Proxemics, the study of spatial relationships, is crucial for comfortable HRI:

```python
import math

class ProxemicManager:
    def __init__(self):
        # Hall's proxemics zones (in meters)
        self.intimate_zone = (0.0, 0.45)    # 0-1.5 feet
        self.personal_zone = (0.45, 1.2)   # 1.5-4 feet
        self.social_zone = (1.2, 3.7)      # 4-12 feet
        self.public_zone = (3.7, 10.0)     # 12+ feet

    def calculate_comfort_level(self, distance, context='neutral'):
        """
        Calculate comfort level based on distance and context.

        Args:
            distance: Distance between robot and human
            context: Interaction context ('greeting', 'intimate', 'public', etc.)

        Returns:
            comfort_level: 0.0 (uncomfortable) to 1.0 (very comfortable)
        """
        if context == 'intimate':
            optimal_range = self.personal_zone
        elif context == 'public':
            optimal_range = self.social_zone
        else:
            optimal_range = self.personal_zone

        min_dist, max_dist = optimal_range

        if distance < self.intimate_zone[0]:
            return 0.0  # Invasion of intimate space
        elif distance < min_dist:
            # Too close, discomfort increases as distance decreases
            discomfort = (min_dist - distance) / min_dist
            return max(0.0, 1.0 - discomfort)
        elif distance <= max_dist:
            # Within optimal range
            return 1.0
        elif distance <= self.public_zone[0]:
            # Beyond optimal but within social range
            comfort_decrease = (distance - max_dist) / (self.public_zone[0] - max_dist)
            return max(0.3, 1.0 - comfort_decrease)
        else:
            # Too far for interaction
            return 0.1

    def suggest_approach_strategy(self, current_distance, desired_distance):
        """
        Suggest safe approach strategy based on proxemics.
        """
        if current_distance < desired_distance:
            # Need to retreat
            if current_distance < self.intimate_zone[1]:
                return {
                    'action': 'immediate_retreat',
                    'distance': self.personal_zone[0],
                    'speed': 'slow'
                }
            elif current_distance < self.personal_zone[1]:
                return {
                    'action': 'gradual_retreat',
                    'distance': self.personal_zone[0],
                    'speed': 'cautious'
                }
            else:
                return {
                    'action': 'maintain_distance',
                    'distance': current_distance,
                    'speed': 'normal'
                }
        else:
            # Can approach
            if desired_distance < self.personal_zone[0]:
                return {
                    'action': 'cautious_approach',
                    'distance': self.personal_zone[0],
                    'speed': 'very_slow'
                }
            elif desired_distance < self.social_zone[1]:
                return {
                    'action': 'normal_approach',
                    'distance': desired_distance,
                    'speed': 'normal'
                }
            else:
                return {
                    'action': 'approach',
                    'distance': desired_distance,
                    'speed': 'confident'
                }
```

## Multimodal Communication Systems

### Speech Communication

Effective speech communication involves both speech recognition and synthesis:

```python
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time

class MultimodalSpeechSystem:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Configure recognizer
        self.recognizer.energy_threshold = 3000  # Adjust based on environment
        self.recognizer.dynamic_energy_threshold = True

        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.configure_tts()

        # Audio processing
        self.audio_queue = queue.Queue()
        self.listening_active = False
        self.speech_thread = None

        # Callbacks
        self.speech_callbacks = {
            'recognized': [],
            'error': [],
            'started_listening': [],
            'stopped_listening': []
        }

    def configure_tts(self):
        """Configure text-to-speech parameters."""
        # Get available voices
        voices = self.tts_engine.getProperty('voices')

        # Set to a natural-sounding voice
        for voice in voices:
            if 'english' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break

        # Set speech parameters
        self.tts_engine.setProperty('rate', 180)  # Words per minute
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

    def start_listening(self):
        """Start continuous listening for speech."""
        if not self.listening_active:
            self.listening_active = True

            # Notify listeners
            self._trigger_callbacks('started_listening')

            # Start listening thread
            self.speech_thread = threading.Thread(target=self._continuous_listening, daemon=True)
            self.speech_thread.start()

    def stop_listening(self):
        """Stop listening for speech."""
        self.listening_active = False

        # Notify listeners
        self._trigger_callbacks('stopped_listening')

    def _continuous_listening(self):
        """Continuously listen for speech in a separate thread."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

            while self.listening_active:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(
                        source,
                        timeout=1.0,
                        phrase_time_limit=5.0
                    )

                    # Recognize speech
                    text = self.recognizer.recognize_google(audio)

                    # Process recognized text
                    self._handle_recognized_speech(text)

                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    continue
                except sr.UnknownValueError:
                    # Speech not understood
                    self._handle_recognition_error("Could not understand audio")
                except sr.RequestError as e:
                    # Recognition service error
                    self._handle_recognition_error(f"Recognition service error: {e}")
                except Exception as e:
                    # Other error
                    self._handle_recognition_error(f"Unexpected error: {e}")

    def _handle_recognized_speech(self, text):
        """Handle recognized speech text."""
        # Clean up text
        cleaned_text = self._clean_recognized_text(text)

        # Trigger callbacks
        for callback in self.speech_callbacks['recognized']:
            try:
                callback(cleaned_text)
            except Exception as e:
                print(f"Error in speech callback: {e}")

    def _handle_recognition_error(self, error_message):
        """Handle speech recognition errors."""
        for callback in self.speech_callbacks['error']:
            try:
                callback(error_message)
            except Exception as e:
                print(f"Error in error callback: {e}")

    def _clean_recognized_text(self, text):
        """Clean and normalize recognized text."""
        # Convert to lowercase
        text = text.lower().strip()

        # Remove common filler words
        fillers = ['um', 'uh', 'like', 'you know', 'so', 'well']
        for filler in fillers:
            text = text.replace(filler, '')

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def speak_text(self, text, blocking=True):
        """
        Speak text using TTS engine.

        Args:
            text: Text to speak
            blocking: Whether to block until speech is complete
        """
        if blocking:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        else:
            # Non-blocking speech
            def speak_non_blocking():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()

            speak_thread = threading.Thread(target=speak_non_blocking, daemon=True)
            speak_thread.start()

    def add_speech_callback(self, event_type, callback):
        """
        Add callback for speech events.

        Args:
            event_type: Type of event ('recognized', 'error', etc.)
            callback: Callback function
        """
        if event_type in self.speech_callbacks:
            self.speech_callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type):
        """Trigger callbacks for specific event."""
        if event_type in self.speech_callbacks:
            for callback in self.speech_callbacks[event_type]:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in {event_type} callback: {e}")
```

### Gesture and Movement Communication

Gestures are crucial for natural interaction:

```python
import numpy as np
from enum import Enum

class GestureType(Enum):
    GREETING = "greeting"
    EMPHASIS = "emphasis"
    DIRECTION = "direction"
    ACKNOWLEDGMENT = "acknowledgment"
    EMPATHY = "empathy"
    INSTRUCTION = "instruction"

class GestureManager:
    def __init__(self):
        self.gesture_library = self._initialize_gesture_library()
        self.current_gesture = None
        self.gesture_speed = 1.0  # Normal speed

    def _initialize_gesture_library(self):
        """Initialize the library of available gestures."""
        return {
            GestureType.GREETING: {
                'name': 'Wave',
                'description': 'Friendly greeting wave',
                'sequence': [
                    {'joint': 'right_shoulder', 'angle': 0.0, 'time': 0.0},
                    {'joint': 'right_shoulder', 'angle': 0.5, 'time': 0.5},
                    {'joint': 'right_elbow', 'angle': 1.0, 'time': 0.5},
                    {'joint': 'right_wrist', 'angle': 0.5, 'time': 0.7},
                    {'joint': 'right_wrist', 'angle': -0.5, 'time': 0.9},  # Wave
                    {'joint': 'right_wrist', 'angle': 0.5, 'time': 1.1},   # Wave back
                    {'joint': 'right_wrist', 'angle': 0.0, 'time': 1.5},
                    {'joint': 'right_shoulder', 'angle': 0.0, 'time': 2.0}
                ],
                'mirrored': True  # Can be mirrored for left hand
            },
            GestureType.EMPHASIS: {
                'name': 'Emphasis Point',
                'description': 'Pointing gesture for emphasis',
                'sequence': [
                    {'joint': 'right_shoulder', 'angle': 0.3, 'time': 0.0},
                    {'joint': 'right_elbow', 'angle': 1.5, 'time': 0.3},
                    {'joint': 'right_wrist', 'angle': 0.2, 'time': 0.5},
                    {'joint': 'right_fingers', 'angle': 0.8, 'time': 0.5},  # Extend index finger
                    {'joint': 'torso', 'angle': 0.1, 'time': 0.7},  # Lean forward slightly
                    {'joint': 'right_shoulder', 'angle': 0.0, 'time': 1.2}
                ]
            },
            GestureType.DIRECTION: {
                'name': 'Direction Point',
                'description': 'Pointing in a specific direction',
                'sequence': [
                    {'joint': 'right_shoulder', 'angle': 0.5, 'time': 0.0},
                    {'joint': 'right_elbow', 'angle': 1.2, 'time': 0.2},
                    {'joint': 'right_wrist', 'angle': 0.0, 'time': 0.4},
                    {'joint': 'right_fingers', 'angle': 0.9, 'time': 0.4},  # Extend fingers
                    {'joint': 'neck', 'angle': 0.3, 'time': 0.5},  # Look in direction
                    {'joint': 'right_shoulder', 'angle': 0.0, 'time': 1.0}
                ]
            },
            GestureType.ACKNOWLEDGMENT: {
                'name': 'Nod',
                'description': 'Head nod for acknowledgment',
                'sequence': [
                    {'joint': 'neck_pitch', 'angle': -0.2, 'time': 0.0},
                    {'joint': 'neck_pitch', 'angle': 0.1, 'time': 0.2},
                    {'joint': 'neck_pitch', 'angle': -0.2, 'time': 0.4},
                    {'joint': 'neck_pitch', 'angle': 0.0, 'time': 0.6}
                ]
            },
            GestureType.EMPATHY: {
                'name': 'Concern Expression',
                'description': 'Gesture showing concern or empathy',
                'sequence': [
                    {'joint': 'eyebrows', 'angle': 0.3, 'time': 0.0},  # Raise eyebrows
                    {'joint': 'neck', 'angle': 0.1, 'time': 0.2},  # Tilt head
                    {'joint': 'shoulders', 'angle': -0.1, 'time': 0.3},  # Slight shrug
                    {'joint': 'eyebrows', 'angle': 0.0, 'time': 0.6},
                    {'joint': 'neck', 'angle': 0.0, 'time': 0.7},
                    {'joint': 'shoulders', 'angle': 0.0, 'time': 0.8}
                ]
            }
        }

    def execute_gesture(self, gesture_type, speed_factor=1.0):
        """
        Execute a gesture by name.

        Args:
            gesture_type: GestureType enum value
            speed_factor: Factor to multiply gesture duration (1.0 = normal)
        """
        if gesture_type not in self.gesture_library:
            print(f"Gesture {gesture_type} not found in library")
            return False

        gesture = self.gesture_library[gesture_type]
        self.current_gesture = gesture

        # Execute gesture sequence
        for step in gesture['sequence']:
            joint = step['joint']
            target_angle = step['angle']
            time_at_step = step['time'] / speed_factor

            # Move to position (this would interface with actual robot)
            self._execute_joint_move(joint, target_angle, time_at_step)

        self.current_gesture = None
        return True

    def _execute_joint_move(self, joint, angle, duration):
        """Execute a joint movement."""
        # This would interface with the actual robot's control system
        # For simulation, we'll just print the movement
        print(f"Moving {joint} to {angle} over {duration}s")

    def interrupt_gesture(self):
        """Interrupt current gesture execution."""
        if self.current_gesture:
            print(f"Interrupting gesture: {self.current_gesture['name']}")
            self.current_gesture = None

    def get_gesture_timing(self, gesture_type):
        """Get the total duration of a gesture."""
        if gesture_type in self.gesture_library:
            sequence = self.gesture_library[gesture_type]['sequence']
            if sequence:
                return sequence[-1]['time']  # Last time value is total duration
        return 0.0

    def execute_contextual_gesture(self, context, intensity=1.0):
        """
        Execute gesture appropriate for context.

        Args:
            context: Context for gesture (e.g., 'greeting', 'empathy', 'direction')
            intensity: Intensity level (0.0 to 1.0)
        """
        if context == 'greeting':
            gesture = GestureType.GREETING
        elif context == 'acknowledgment':
            gesture = GestureType.ACKNOWLEDGMENT
        elif context == 'direction':
            gesture = GestureType.DIRECTION
        elif context == 'empathy':
            gesture = GestureType.EMPATHY
        else:
            gesture = GestureType.EMPHASIS

        # Adjust speed based on intensity
        speed_factor = 0.5 + 0.5 * intensity  # 0.5 to 1.0

        return self.execute_gesture(gesture, speed_factor)
```

### Facial Expression System

```python
import cv2
import numpy as np
from enum import Enum

class FacialExpression(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CONFUSED = "confused"
    CONCENTRATED = "concentrated"
    CONCERNED = "concerned"

class FacialExpressionSystem:
    def __init__(self, display_width=128, display_height=128):
        self.display_width = display_width
        self.display_height = display_height
        self.current_expression = FacialExpression.NEUTRAL
        self.expression_intensity = 1.0  # 0.0 to 1.0

    def generate_expression_image(self, expression, intensity=1.0):
        """
        Generate facial expression image.

        Args:
            expression: FacialExpression enum value
            intensity: Expression intensity (0.0 to 1.0)

        Returns:
            image: Generated facial expression image
        """
        # Create blank image
        img = np.ones((self.display_height, self.display_width, 3), dtype=np.uint8) * 255

        # Draw face base
        center_x, center_y = self.display_width // 2, self.display_height // 2
        face_radius = min(self.display_width, self.display_height) // 2 - 10

        # Draw face circle
        cv2.circle(img, (center_x, center_y), face_radius, (200, 200, 200), -1)  # Skin tone
        cv2.circle(img, (center_x, center_y), face_radius, (0, 0, 0), 2)  # Face outline

        # Draw features based on expression
        if expression == FacialExpression.HAPPY:
            self._draw_happy_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.SAD:
            self._draw_sad_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.ANGRY:
            self._draw_angry_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.SURPRISED:
            self._draw_surprised_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.FEARFUL:
            self._draw_fearful_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.CONFUSED:
            self._draw_confused_expression(img, center_x, center_y, face_radius, intensity)
        elif expression == FacialExpression.CONCERNED:
            self._draw_concerned_expression(img, center_x, center_y, face_radius, intensity)
        else:  # Neutral
            self._draw_neutral_expression(img, center_x, center_y, face_radius)

        return img

    def _draw_neutral_expression(self, img, cx, cy, radius):
        """Draw neutral facial expression."""
        # Eyes
        eye_y = cy - radius // 3
        eye_radius = radius // 8

        # Left eye
        cv2.circle(img, (cx - radius//3, eye_y), eye_radius, (0, 0, 0), 2)
        cv2.circle(img, (cx - radius//3, eye_y), eye_radius//3, (0, 0, 0), -1)  # Pupil

        # Right eye
        cv2.circle(img, (cx + radius//3, eye_y), eye_radius, (0, 0, 0), 2)
        cv2.circle(img, (cx + radius//3, eye_y), eye_radius//3, (0, 0, 0), -1)  # Pupil

        # Neutral mouth
        mouth_width = radius // 2
        mouth_y = cy + radius // 4
        cv2.line(img,
                (cx - mouth_width//2, mouth_y),
                (cx + mouth_width//2, mouth_y),
                (0, 0, 0), 2)

    def _draw_happy_expression(self, img, cx, cy, radius, intensity):
        """Draw happy facial expression."""
        # Smiling eyes (closed slightly)
        eye_y = cy - radius // 3
        eye_radius = radius // 8

        # Left eye (smile shape)
        eye_points = np.array([
            [cx - radius//3 - eye_radius, eye_y],
            [cx - radius//3, eye_y - eye_radius//2],
            [cx - radius//3 + eye_radius, eye_y]
        ], np.int32)
        cv2.polylines(img, [eye_points], False, (0, 0, 0), 2)

        # Right eye (smile shape)
        eye_points = np.array([
            [cx + radius//3 - eye_radius, eye_y],
            [cx + radius//3, eye_y - eye_radius//2],
            [cx + radius//3 + eye_radius, eye_y]
        ], np.int32)
        cv2.polylines(img, [eye_points], False, (0, 0, 0), 2)

        # Happy mouth (smile)
        mouth_width = radius // 2
        mouth_y = cy + radius // 3
        smile_points = np.array([
            [cx - mouth_width//2, mouth_y],
            [cx, mouth_y + radius//4 * intensity],
            [cx + mouth_width//2, mouth_y]
        ], np.int32)
        cv2.polylines(img, [smile_points], False, (0, 0, 0), 2)

    def _draw_sad_expression(self, img, cx, cy, radius, intensity):
        """Draw sad facial expression."""
        # Sad eyes (drooping)
        eye_y = cy - radius // 3
        eye_radius = radius // 8

        # Left eye (drooping)
        eye_points = np.array([
            [cx - radius//3 - eye_radius, eye_y],
            [cx - radius//3, eye_y + eye_radius//2],
            [cx - radius//3 + eye_radius, eye_y]
        ], np.int32)
        cv2.polylines(img, [eye_points], False, (0, 0, 0), 2)

        # Right eye (drooping)
        eye_points = np.array([
            [cx + radius//3 - eye_radius, eye_y],
            [cx + radius//3, eye_y + eye_radius//2],
            [cx + radius//3 + eye_radius, eye_y]
        ], np.int32)
        cv2.polylines(img, [eye_points], False, (0, 0, 0), 2)

        # Sad mouth (frown)
        mouth_width = radius // 2
        mouth_y = cy + radius // 2
        frown_points = np.array([
            [cx - mouth_width//2, mouth_y],
            [cx, mouth_y - radius//4 * intensity],
            [cx + mouth_width//2, mouth_y]
        ], np.int32)
        cv2.polylines(img, [frown_points], False, (0, 0, 0), 2)

    def _draw_angry_expression(self, img, cx, cy, radius, intensity):
        """Draw angry facial expression."""
        # Angry eyes (narrowed)
        eye_y = cy - radius // 3
        eye_width = radius // 6

        # Left eye (narrowed)
        cv2.ellipse(img, (cx - radius//3, eye_y), (eye_width, eye_width//3),
                   0, 0, 180, (0, 0, 0), 2)

        # Right eye (narrowed)
        cv2.ellipse(img, (cx + radius//3, eye_y), (eye_width, eye_width//3),
                   0, 0, 180, (0, 0, 0), 2)

        # Angry eyebrows (furrowed)
        brow_y = cy - radius // 2
        # Left eyebrow
        cv2.line(img, (cx - radius//2, brow_y), (cx - radius//4, brow_y - radius//8 * intensity), (0, 0, 0), 2)
        # Right eyebrow
        cv2.line(img, (cx + radius//2, brow_y), (cx + radius//4, brow_y - radius//8 * intensity), (0, 0, 0), 2)

        # Angry mouth (tight line)
        mouth_width = radius // 3
        mouth_y = cy + radius // 2
        cv2.line(img,
                (cx - mouth_width//2, mouth_y),
                (cx + mouth_width//2, mouth_y),
                (0, 0, 0), 3)  # Thick line

    def _draw_surprised_expression(self, img, cx, cy, radius, intensity):
        """Draw surprised facial expression."""
        # Surprised eyes (wide open)
        eye_radius = radius // 8

        # Left eye (wide)
        cv2.circle(img, (cx - radius//3, cy - radius//3), eye_radius, (0, 0, 0), 2)
        cv2.circle(img, (cx - radius//3, cy - radius//3), eye_radius//4, (0, 0, 0), -1)  # Large pupil

        # Right eye (wide)
        cv2.circle(img, (cx + radius//3, cy - radius//3), eye_radius, (0, 0, 0), 2)
        cv2.circle(img, (cx + radius//3, cy - radius//3), eye_radius//4, (0, 0, 0), -1)  # Large pupil

        # Raised eyebrows
        brow_y = cy - radius // 2
        # Left eyebrow
        cv2.line(img, (cx - radius//2, brow_y), (cx - radius//4, brow_y + radius//10), (0, 0, 0), 2)
        # Right eyebrow
        cv2.line(img, (cx + radius//2, brow_y), (cx + radius//4, brow_y + radius//10), (0, 0, 0), 2)

        # Surprised mouth (O shape)
        mouth_radius = radius // 6 * intensity
        mouth_y = cy + radius // 3
        cv2.circle(img, (cx, mouth_y), mouth_radius, (0, 0, 0), 2)

    def set_expression(self, expression, intensity=1.0, duration=0.5):
        """
        Set facial expression with smooth transition.

        Args:
            expression: FacialExpression enum value
            intensity: Expression intensity (0.0 to 1.0)
            duration: Transition duration in seconds
        """
        self.current_expression = expression
        self.expression_intensity = intensity

        # Generate expression image
        expression_img = self.generate_expression_image(expression, intensity)

        # In a real implementation, this would update the robot's facial display
        # For this example, we'll just return the image
        return expression_img

    def blend_expressions(self, exp1, exp2, ratio):
        """
        Blend between two expressions.

        Args:
            exp1: First expression
            exp2: Second expression
            ratio: Blend ratio (0.0 = pure exp1, 1.0 = pure exp2)
        """
        # This would involve more complex image blending
        # For this example, we'll use the second expression when ratio > 0.5
        if ratio > 0.5:
            return self.generate_expression_image(exp2, ratio)
        else:
            return self.generate_expression_image(exp1, 1.0 - ratio)
```

## Social Interaction Principles

### Turn-Taking and Conversation Management

```python
import time
from enum import Enum
from collections import deque

class ConversationState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    AWAITING_RESPONSE = "awaiting_response"

class TurnTakingManager:
    def __init__(self):
        self.state = ConversationState.IDLE
        self.conversation_history = deque(maxlen=50)
        self.user_attention_detected = False
        self.robot_attention_requested = False
        self.last_speech_time = 0
        self.last_user_speech_time = 0
        self.conversation_timeout = 10.0  # seconds
        self.response_timeout = 5.0  # seconds after user speech

    def update_attention_status(self, user_attention, robot_attention_requested=False):
        """Update attention status from perception system."""
        self.user_attention_detected = user_attention
        self.robot_attention_requested = robot_attention_requested

    def process_user_speech(self, speech_text):
        """Process user speech input."""
        current_time = time.time()

        # Add to conversation history
        self.conversation_history.append({
            'speaker': 'human',
            'text': speech_text,
            'timestamp': current_time
        })

        self.last_user_speech_time = current_time

        # Update state based on current state
        if self.state in [ConversationState.IDLE, ConversationState.LISTENING]:
            self.state = ConversationState.THINKING
        elif self.state == ConversationState.AWAITING_RESPONSE:
            # User interrupted while waiting for response
            self.state = ConversationState.THINKING

    def generate_robot_response(self, user_input):
        """Generate appropriate robot response."""
        # Analyze user input
        intent = self.analyze_intent(user_input)
        sentiment = self.analyze_sentiment(user_input)

        # Generate response based on intent and context
        response = self.create_contextual_response(intent, sentiment, user_input)

        # Add to conversation history
        current_time = time.time()
        self.conversation_history.append({
            'speaker': 'robot',
            'text': response,
            'timestamp': current_time
        })

        self.last_speech_time = current_time
        self.state = ConversationState.SPEAKING

        return response

    def analyze_intent(self, text):
        """Analyze intent of user input."""
        text_lower = text.lower()

        # Simple keyword-based intent analysis
        if any(greeting in text_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        elif any(question_word in text_lower for question_word in ['what', 'how', 'when', 'where', 'why']):
            return 'question'
        elif any(command_word in text_lower for command_word in ['please', 'could you', 'can you', 'move', 'go']):
            return 'request'
        elif any(farewell in text_lower for farewell in ['bye', 'goodbye', 'see you', 'farewell']):
            return 'farewell'
        else:
            return 'statement'

    def analyze_sentiment(self, text):
        """Analyze sentiment of user input."""
        # Simple sentiment analysis using keyword matching
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic', 'love', 'like', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'annoying']

        pos_count = sum(1 for word in positive_words if word in text.lower())
        neg_count = sum(1 for word in negative_words if word in text.lower())

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'

    def create_contextual_response(self, intent, sentiment, user_input):
        """Create response based on intent, sentiment, and context."""
        import random

        responses = {
            'greeting': {
                'positive': [
                    "Hello! It's wonderful to meet you!",
                    "Hi there! I'm happy to interact with you!",
                    "Greetings! What brings you here today?"
                ],
                'neutral': [
                    "Hello! How can I assist you?",
                    "Hi! Nice to meet you!",
                    "Greetings! How are you doing?"
                ],
                'negative': [
                    "Hello. I hope I can brighten your day!",
                    "Hi there. Is there something I can help with?",
                    "Greetings. I'm here if you need assistance."
                ]
            },
            'question': {
                'positive': [
                    f"You asked: '{user_input}'. That's an interesting question!",
                    f"Regarding your question about '{user_input}', I'd be happy to help!",
                    f"Great question about '{user_input}'! Here's what I know..."
                ],
                'neutral': [
                    f"You asked: '{user_input}'. Let me think about that...",
                    f"Regarding '{user_input}', here's what I can tell you...",
                    f"I understand you're asking about '{user_input}'. Let me help."
                ],
                'negative': [
                    f"I understand you're asking about '{user_input}'. I'll do my best to assist.",
                    f"You asked: '{user_input}'. I'm here to help with your concerns.",
                    f"Regarding '{user_input}', I want to provide helpful information."
                ]
            },
            'request': {
                'positive': [
                    f"You asked me to: '{user_input}'. I'll do my best!",
                    f"I'd be happy to help with '{user_input}'!",
                    f"Sure thing! You asked for '{user_input}'. Working on it..."
                ],
                'neutral': [
                    f"I received your request: '{user_input}'. Processing...",
                    f"You asked me to '{user_input}'. I'll see what I can do.",
                    f"Understood. You'd like me to '{user_input}'."
                ],
                'negative': [
                    f"I understand you need help with '{user_input}'. I'll assist you.",
                    f"You requested '{user_input}'. I'm here to help.",
                    f"Regarding '{user_input}', I want to be helpful."
                ]
            },
            'farewell': {
                'positive': [
                    "Goodbye! It was wonderful talking with you!",
                    "Farewell! I hope to see you again soon!",
                    "Take care! Have a fantastic day!"
                ],
                'neutral': [
                    "Goodbye! Thanks for the conversation!",
                    "See you later! Have a good day!",
                    "Farewell! It was nice talking with you."
                ],
                'negative': [
                    "Goodbye. I hope things improve for you!",
                    "Take care. I'm here if you need me again.",
                    "Farewell. I hope our next interaction is better."
                ]
            },
            'statement': {
                'positive': [
                    f"That's great to hear about '{user_input}'!",
                    f"Thanks for sharing: '{user_input}'. That sounds wonderful!",
                    f"I appreciate you telling me about '{user_input}'."
                ],
                'neutral': [
                    f"Thanks for letting me know: '{user_input}'.",
                    f"I understand you said: '{user_input}'.",
                    f"Interesting! You mentioned '{user_input}'."
                ],
                'negative': [
                    f"I understand you're experiencing '{user_input}'. I'm here to listen.",
                    f"Thanks for sharing '{user_input}'. I'm ready to help if needed.",
                    f"I hear you regarding '{user_input}'. How can I assist?"
                ]
            }
        }

        response_category = responses.get(intent, responses['statement'])
        sentiment_responses = response_category.get(sentiment, response_category['neutral'])

        return random.choice(sentiment_responses)

    def manage_conversation_flow(self):
        """Manage conversation state transitions."""
        current_time = time.time()

        # Check for timeouts
        if (current_time - self.last_speech_time) > self.conversation_timeout:
            if self.state != ConversationState.IDLE:
                self.state = ConversationState.IDLE
                return "timeout_reset"

        # Check if it's time for robot to speak
        if (self.state == ConversationState.THINKING and
            (current_time - self.last_user_speech_time) > 0.5):  # Brief thinking time
            return "ready_to_respond"

        # Check if waiting for response timeout
        if (self.state == ConversationState.AWAITING_RESPONSE and
            (current_time - self.last_speech_time) > self.response_timeout):
            return "response_timeout"

        return "continue"

    def initiate_conversation(self):
        """Initiate conversation when appropriate."""
        if self.user_attention_detected and self.state == ConversationState.IDLE:
            self.state = ConversationState.LISTENING
            greeting = "Hello! I noticed you're paying attention. How can I assist you today?"

            self.conversation_history.append({
                'speaker': 'robot',
                'text': greeting,
                'timestamp': time.time()
            })

            self.last_speech_time = time.time()
            return greeting

        return None

    def get_conversation_context(self):
        """Get current conversation context."""
        return {
            'state': self.state.value,
            'user_attention': self.user_attention_detected,
            'robot_attention_requested': self.robot_attention_requested,
            'last_human_speech': time.time() - self.last_user_speech_time,
            'last_robot_speech': time.time() - self.last_speech_time,
            'conversation_active': self.state != ConversationState.IDLE
        }
```

## Context-Aware Interaction

### Environmental Context Recognition

```python
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class EnvironmentalContext:
    location: str
    time_of_day: str
    day_of_week: str
    lighting_condition: str
    noise_level: float  # 0.0 to 1.0
    occupancy: int      # Number of people present
    activity_type: str  # Meeting, casual, focused work, etc.

@dataclass
class SocialContext:
    user_familiarity: float  # 0.0 to 1.0
    interaction_history: List[str]
    cultural_preferences: Dict[str, str]
    formality_preference: str  # formal, casual, intimate

@dataclass
class TaskContext:
    current_task: str
    task_priority: int  # 1-10 scale
    task_phase: str     # planning, execution, completion
    required_attention: str  # high, medium, low
    estimated_completion: float  # seconds

class ContextManager:
    def __init__(self):
        self.environmental_context = EnvironmentalContext(
            location="unknown",
            time_of_day="unknown",
            day_of_week="unknown",
            lighting_condition="normal",
            noise_level=0.5,
            occupancy=1,
            activity_type="unknown"
        )

        self.social_context = SocialContext(
            user_familiarity=0.0,
            interaction_history=[],
            cultural_preferences={},
            formality_preference="casual"
        )

        self.task_context = TaskContext(
            current_task="idle",
            task_priority=1,
            task_phase="idle",
            required_attention="low",
            estimated_completion=0.0
        )

        self.context_change_callbacks = []

    def update_environmental_context(self, sensor_data: Dict):
        """Update environmental context from sensor data."""
        # Update location based on RFID, WiFi, or other location sensors
        if 'location' in sensor_data:
            self.environmental_context.location = sensor_data['location']

        # Update time-based context
        current_time = datetime.now()
        self.environmental_context.time_of_day = self._classify_time_of_day(current_time.hour)
        self.environmental_context.day_of_week = current_time.strftime('%A')

        # Update environmental conditions
        if 'lighting_level' in sensor_data:
            light_level = sensor_data['lighting_level']
            if light_level < 0.3:
                self.environmental_context.lighting_condition = "dim"
            elif light_level > 0.8:
                self.environmental_context.lighting_condition = "bright"
            else:
                self.environmental_context.lighting_condition = "normal"

        if 'noise_level' in sensor_data:
            self.environmental_context.noise_level = min(1.0, sensor_data['noise_level'])

        if 'occupancy_count' in sensor_data:
            self.environmental_context.occupancy = sensor_data['occupancy_count']

        if 'activity_type' in sensor_data:
            self.environmental_context.activity_type = sensor_data['activity_type']

    def _classify_time_of_day(self, hour):
        """Classify time of day based on hour."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def update_social_context(self, user_id: str, interaction_data: Dict):
        """Update social context based on user interaction."""
        # Update user familiarity based on interaction frequency
        interaction_count = len([ih for ih in self.social_context.interaction_history
                               if ih.startswith(f"user_{user_id}")])
        self.social_context.user_familiarity = min(1.0, interaction_count * 0.1)

        # Add to interaction history
        self.social_context.interaction_history.append(
            f"user_{user_id}_{datetime.now().isoformat()}"
        )

        # Update cultural preferences if provided
        if 'cultural_preferences' in interaction_data:
            self.social_context.cultural_preferences.update(
                interaction_data['cultural_preferences']
            )

        # Update formality preference based on user behavior
        if 'formality_indicators' in interaction_data:
            formal_indicators = interaction_data['formality_indicators']
            if formal_indicators.get('uses_title', False):
                self.social_context.formality_preference = "formal"
            elif formal_indicators.get('uses_first_name', False):
                self.social_context.formality_preference = "casual"

    def update_task_context(self, task_data: Dict):
        """Update task context."""
        if 'task_name' in task_data:
            self.task_context.current_task = task_data['task_name']

        if 'priority' in task_data:
            self.task_context.task_priority = task_data['priority']

        if 'phase' in task_data:
            self.task_context.task_phase = task_data['phase']

        if 'attention_required' in task_data:
            self.task_context.required_attention = task_data['attention_required']

        if 'estimated_duration' in task_data:
            self.task_context.estimated_completion = task_data['estimated_duration']

    def get_context_aware_behavior_modifiers(self) -> Dict:
        """
        Get behavior modifiers based on current context.
        """
        modifiers = {
            'speech_volume': self._calculate_speech_volume(),
            'formality_level': self._calculate_formality_level(),
            'interaction_speed': self._calculate_interaction_speed(),
            'personal_space': self._calculate_personal_space(),
            'gaze_behavior': self._calculate_gaze_behavior(),
            'gesture_intensity': self._calculate_gesture_intensity()
        }

        return modifiers

    def _calculate_speech_volume(self) -> float:
        """Calculate appropriate speech volume based on context."""
        base_volume = 0.8  # Normal volume

        # Adjust for noise level
        noise_adjustment = (1.0 - self.environmental_context.noise_level) * 0.3
        adjusted_volume = base_volume + noise_adjustment

        # Adjust for occupancy (speak softer when more people present)
        occupancy_adjustment = max(0.0, (5 - self.environmental_context.occupancy) * 0.1)
        final_volume = max(0.3, min(1.0, adjusted_volume + occupancy_adjustment))

        return final_volume

    def _calculate_formality_level(self) -> str:
        """Calculate appropriate formality level."""
        if self.social_context.user_familiarity > 0.7:
            return "casual"
        elif self.social_context.formality_preference == "formal":
            return "formal"
        elif self.environmental_context.location in ["office", "meeting_room", "conference"]:
            return "formal"
        else:
            return "casual"

    def _calculate_interaction_speed(self) -> float:
        """Calculate appropriate interaction speed (0.0 to 1.0)."""
        speed = 0.7  # Base speed

        # Slow down for formal interactions
        if self._calculate_formality_level() == "formal":
            speed *= 0.8

        # Adjust for user familiarity
        speed += self.social_context.user_familiarity * 0.2

        # Adjust for attention requirements
        if self.task_context.required_attention == "high":
            speed *= 0.9
        elif self.task_context.required_attention == "low":
            speed *= 1.1

        return max(0.3, min(1.0, speed))

    def _calculate_personal_space(self) -> float:
        """Calculate appropriate personal space distance."""
        # Base distance based on formality
        if self._calculate_formality_level() == "formal":
            base_distance = 1.0  # Meter
        else:
            base_distance = 0.6  # Meter

        # Adjust for cultural preferences
        if "latin_american" in self.social_context.cultural_preferences.get("background", ""):
            base_distance *= 0.8  # Closer interaction
        elif "east_asian" in self.social_context.cultural_preferences.get("background", ""):
            base_distance *= 1.2  # More distance

        # Adjust for activity type
        if self.environmental_context.activity_type in ["presentation", "formal_meeting"]:
            base_distance *= 1.1
        elif self.environmental_context.activity_type in ["collaboration", "brainstorming"]:
            base_distance *= 0.9

        return base_distance

    def _calculate_gaze_behavior(self) -> str:
        """Calculate appropriate gaze behavior."""
        if self._calculate_formality_level() == "formal":
            return "respectful_attention"  # Maintain appropriate eye contact
        elif self.environmental_context.noise_level > 0.7:
            return "attentive_listening"   # More visual attention needed
        elif self.environmental_context.occupancy > 3:
            return "inclusive_scanning"    # Scan between multiple people
        else:
            return "natural_conversation"  # Normal eye contact pattern

    def _calculate_gesture_intensity(self) -> float:
        """Calculate appropriate gesture intensity."""
        intensity = 0.6  # Base intensity

        # Adjust for formality
        if self._calculate_formality_level() == "formal":
            intensity *= 0.7  # More reserved gestures
        else:
            intensity *= 1.2  # More expressive gestures

        # Adjust for environment
        if self.environmental_context.occupancy > 5:
            intensity *= 0.8  # More subtle in crowds
        elif self.environmental_context.activity_type == "presentation":
            intensity *= 1.3  # More expressive for presentations

        # Adjust for user familiarity
        intensity += self.social_context.user_familiarity * 0.3

        return max(0.2, min(1.0, intensity))

    def get_adaptive_response(self, base_response: str) -> str:
        """
        Generate context-adaptive response.
        """
        modifiers = self.get_context_aware_behavior_modifiers()

        # Apply formality modifications
        if modifiers['formality_level'] == 'formal':
            # Make response more formal
            formal_prefixes = ["Dear user,", "Respectfully,", "I would like to inform you that,"]
            formal_suffixes = ["Thank you for your patience.", "I hope this information is helpful.", "Please let me know if you need further assistance."]

            import random
            formal_response = f"{random.choice(formal_prefixes)} {base_response} {random.choice(formal_suffixes)}"
        elif modifiers['formality_level'] == 'casual':
            # Make response more casual
            casual_connectors = ["So, ", "Well, ", ""]
            casual_endings = ["Cheers!", "Have a good one!", "Talk soon!"]

            import random
            casual_response = f"{random.choice(casual_connectors)}{base_response} {random.choice(casual_endings)}"
        else:
            casual_response = base_response

        return casual_response

    def add_context_change_callback(self, callback):
        """Add callback for context changes."""
        self.context_change_callbacks.append(callback)

    def notify_context_changes(self, old_context, new_context):
        """Notify about context changes."""
        for callback in self.context_change_callbacks:
            try:
                callback(old_context, new_context)
            except Exception as e:
                print(f"Error in context change callback: {e}")
```

## Safety and Ethical Considerations

### Safety Management System

```python
class SafetyManager:
    def __init__(self):
        self.safety_zones = {
            'collision_prevention': 0.5,    # 50cm minimum distance
            'emergency_stop': 0.2,         # 20cm critical distance
            'safe_operation': 1.0          # 1m safe distance
        }

        self.emergency_stop_active = False
        self.safety_violations = []
        self.safety_thresholds = {
            'velocity_limit': 0.5,         # m/s
            'acceleration_limit': 2.0,     # m/s²
            'torque_limit': 50.0,          # Nm
            'temperature_limit': 60.0      # °C
        }

    def check_safety_constraints(self, robot_state, environment_state):
        """
        Check if current robot state violates safety constraints.

        Returns:
            safety_ok: Boolean indicating if state is safe
            violations: List of safety violations
        """
        violations = []

        # Check collision constraints
        if 'obstacle_distances' in environment_state:
            min_distance = min(environment_state['obstacle_distances'])
            if min_distance < self.safety_zones['collision_prevention']:
                violations.append({
                    'type': 'collision_risk',
                    'severity': 'warning',
                    'distance': min_distance,
                    'threshold': self.safety_zones['collision_prevention']
                })

            if min_distance < self.safety_zones['emergency_stop']:
                violations.append({
                    'type': 'collision_imminent',
                    'severity': 'critical',
                    'distance': min_distance,
                    'threshold': self.safety_zones['emergency_stop']
                })

        # Check velocity constraints
        if 'joint_velocities' in robot_state:
            max_vel = max(abs(v) for v in robot_state['joint_velocities'])
            if max_vel > self.safety_thresholds['velocity_limit']:
                violations.append({
                    'type': 'velocity_exceeded',
                    'severity': 'warning',
                    'value': max_vel,
                    'threshold': self.safety_thresholds['velocity_limit']
                })

        # Check acceleration constraints
        if 'joint_accelerations' in robot_state:
            max_acc = max(abs(a) for a in robot_state['joint_accelerations'])
            if max_acc > self.safety_thresholds['acceleration_limit']:
                violations.append({
                    'type': 'acceleration_exceeded',
                    'severity': 'warning',
                    'value': max_acc,
                    'threshold': self.safety_thresholds['acceleration_limit']
                })

        # Check torque constraints
        if 'joint_torques' in robot_state:
            max_torque = max(abs(t) for t in robot_state['joint_torques'])
            if max_torque > self.safety_thresholds['torque_limit']:
                violations.append({
                    'type': 'torque_exceeded',
                    'severity': 'warning',
                    'value': max_torque,
                    'threshold': self.safety_thresholds['torque_limit']
                })

        # Check temperature constraints
        if 'motor_temperatures' in robot_state:
            max_temp = max(robot_state['motor_temperatures'])
            if max_temp > self.safety_thresholds['temperature_limit']:
                violations.append({
                    'type': 'temperature_exceeded',
                    'severity': 'warning',
                    'value': max_temp,
                    'threshold': self.safety_thresholds['temperature_limit']
                })

        # Check for critical violations that require emergency stop
        critical_violations = [v for v in violations if v['severity'] == 'critical']
        if critical_violations:
            self.activate_emergency_stop()
            return False, violations

        self.safety_violations.extend(violations)
        return len(violations) == 0, violations

    def activate_emergency_stop(self):
        """Activate emergency stop procedures."""
        self.emergency_stop_active = True
        print("EMERGENCY STOP ACTIVATED - Halting all robot motion")

        # In a real system, this would:
        # - Cut power to actuators
        # - Apply brakes
        # - Sound alarm
        # - Send notifications

    def deactivate_emergency_stop(self):
        """Deactivate emergency stop."""
        self.emergency_stop_active = False
        print("Emergency stop deactivated - Robot ready")

    def get_safety_status(self):
        """Get current safety status."""
        return {
            'emergency_stop_active': self.emergency_stop_active,
            'violation_count': len(self.safety_violations),
            'recent_violations': self.safety_violations[-10:],  # Last 10 violations
            'safety_zones': self.safety_zones,
            'safety_thresholds': self.safety_thresholds
        }

    def reset_safety_system(self):
        """Reset safety system."""
        self.safety_violations.clear()
        self.emergency_stop_active = False
        print("Safety system reset")

class EthicalDecisionMaker:
    def __init__(self):
        self.ethical_principles = {
            'beneficence': 0.9,      # Robot should do good
            'non_malfeasance': 1.0,  # Robot should do no harm
            'autonomy': 0.7,         # Respect human autonomy
            'justice': 0.8           # Fair treatment
        }

        self.ethical_decision_tree = self._build_ethical_decision_tree()

    def _build_ethical_decision_tree(self):
        """Build ethical decision tree for action evaluation."""
        return {
            'refuse_action': [
                'would_cause_harm',
                'violates_consent',
                'discriminatory',
                'invasion_of_privacy'
            ],
            'require_confirmation': [
                'significant_consequences',
                'changes_robot_behavior',
                'collects_personal_data'
            ],
            'proceed_with_caution': [
                'minor_risks',
                'beneficial_outcomes',
                'human_supervision_available'
            ]
        }

    def evaluate_action_ethically(self, action, context):
        """
        Evaluate an action based on ethical principles.

        Args:
            action: Action to evaluate
            context: Context of the action

        Returns:
            evaluation: Dictionary with ethical evaluation
        """
        evaluation = {
            'action': action,
            'ethical_score': 0.0,
            'principle_alignment': {},
            'recommendation': 'proceed',
            'reasoning': []
        }

        # Evaluate against each ethical principle
        for principle, weight in self.ethical_principles.items():
            alignment = self._evaluate_principle_alignment(action, context, principle)
            evaluation['principle_alignment'][principle] = alignment
            evaluation['ethical_score'] += alignment * weight

        # Determine recommendation based on ethical score
        if evaluation['ethical_score'] < 0.3:
            evaluation['recommendation'] = 'refuse'
        elif evaluation['ethical_score'] < 0.7:
            evaluation['recommendation'] = 'proceed_with_caution'
        elif evaluation['ethical_score'] < 0.9:
            evaluation['recommendation'] = 'require_confirmation'
        else:
            evaluation['recommendation'] = 'proceed'

        # Add reasoning
        if evaluation['ethical_score'] < 0.3:
            evaluation['reasoning'].append("Action fails ethical evaluation")
        elif 'harm' in str(action).lower():
            evaluation['reasoning'].append("Potential for harm detected")

        return evaluation

    def _evaluate_principle_alignment(self, action, context, principle):
        """Evaluate how well an action aligns with an ethical principle."""
        # This is a simplified evaluation
        # In practice, this would involve complex ethical reasoning

        if principle == 'non_malfeasance':
            # Check for potential harm
            harmful_keywords = ['hurt', 'harm', 'danger', 'injure', 'damage']
            if any(keyword in str(action).lower() for keyword in harmful_keywords):
                return 0.0
            else:
                return 1.0
        elif principle == 'autonomy':
            # Check for respect of human autonomy
            if 'override_human_decision' in action:
                return 0.2
            elif 'assist_human_choice' in action:
                return 0.9
            else:
                return 0.7
        elif principle == 'beneficence':
            # Check for beneficial outcomes
            beneficial_keywords = ['help', 'assist', 'support', 'benefit', 'aid']
            if any(keyword in str(action).lower() for keyword in beneficial_keywords):
                return 0.9
            else:
                return 0.5
        else:
            # Default evaluation
            return 0.7

    def handle_ethical_dilemma(self, dilemma_context):
        """
        Handle ethical dilemmas by applying ethical reasoning.
        """
        # Example: Conflict between beneficence and autonomy
        if dilemma_context.get('conflict_type') == 'beneficence_vs_autonomy':
            # Prioritize autonomy while seeking alternative beneficial solutions
            return {
                'primary_principle': 'autonomy',
                'secondary_consideration': 'beneficence',
                'recommended_action': 'inform_user_and_seek_consent',
                'alternatives': self._generate_alternatives(dilemma_context)
            }

        return {
            'primary_principle': 'non_malfeasance',
            'recommended_action': 'default_safe_behavior',
            'alternatives': []
        }

    def _generate_alternatives(self, context):
        """Generate ethical alternatives to problematic actions."""
        alternatives = []

        # Generate alternative approaches that better align with ethical principles
        alternatives.append({
            'action': 'request_explicit_consent',
            'ethics_score': 0.9,
            'principles_supported': ['autonomy', 'beneficence']
        })

        alternatives.append({
            'action': 'provide_information_only',
            'ethics_score': 0.8,
            'principles_supported': ['autonomy', 'beneficence']
        })

        alternatives.append({
            'action': 'suggest_human_supervision',
            'ethics_score': 0.85,
            'principles_supported': ['non_malfeasance', 'autonomy']
        })

        return alternatives
```

## Implementation Examples

### Complete Interaction System Integration

```python
class HumanoidInteractionSystem:
    def __init__(self):
        # Initialize all subsystems
        self.speech_system = MultimodalSpeechSystem()
        self.gesture_manager = GestureManager()
        self.facial_system = FacialExpressionSystem()
        self.turn_taking_manager = TurnTakingManager()
        self.context_manager = ContextManager()
        self.safety_manager = SafetyManager()
        self.ethics_manager = EthicalDecisionMaker()

        # Interaction state
        self.interaction_active = False
        self.current_user_id = "unknown"
        self.interaction_mode = "social"  # social, task_assistance, entertainment, etc.

    def start_interaction(self, user_id="unknown", mode="social"):
        """Start a new interaction session."""
        self.current_user_id = user_id
        self.interaction_mode = mode
        self.interaction_active = True

        # Initialize context for this user
        self.context_manager.update_social_context(
            user_id,
            {"session_start": True}
        )

        # Start listening
        self.speech_system.start_listening()

        # Show welcoming expression
        self.facial_system.set_expression(FacialExpression.HAPPY, intensity=0.8)

        # Perform welcoming gesture
        self.gesture_manager.execute_contextual_gesture('greeting', intensity=0.7)

        # Say hello
        greeting = f"Hello {user_id if user_id != 'unknown' else 'there'}! I'm ready to interact with you."
        self.speech_system.speak_text(greeting)

    def process_interaction_step(self, sensor_data):
        """
        Process one step of interaction.

        Args:
            sensor_data: Dictionary containing sensor measurements

        Returns:
            response: Generated response or None
        """
        if not self.interaction_active:
            return None

        # Update context managers
        self.context_manager.update_environmental_context(sensor_data)
        self.turn_taking_manager.update_attention_status(
            sensor_data.get('user_attention', False)
        )

        # Check safety constraints
        robot_state = sensor_data.get('robot_state', {})
        environment_state = sensor_data.get('environment_state', {})

        safety_ok, violations = self.safety_manager.check_safety_constraints(
            robot_state, environment_state
        )

        if not safety_ok:
            # Handle safety violations
            for violation in violations:
                if violation['severity'] == 'critical':
                    self._handle_critical_safety_violation(violation)
                    return None

        # Manage conversation flow
        conversation_action = self.turn_taking_manager.manage_conversation_flow()

        if conversation_action == "ready_to_respond":
            # Get recent user input from speech system
            # (In a real implementation, this would be more sophisticated)
            pass

        elif conversation_action == "timeout_reset":
            # Conversation timed out, reset
            self.interaction_active = False
            self._reset_interaction_state()

        # Get context-aware behavior modifiers
        modifiers = self.context_manager.get_context_aware_behavior_modifiers()

        # Adjust behavior based on context
        self._apply_context_modifiers(modifiers)

        return None

    def _handle_critical_safety_violation(self, violation):
        """Handle critical safety violations."""
        # Stop all motion
        self._emergency_stop()

        # Show concerned expression
        self.facial_system.set_expression(FacialExpression.CONCERNED, intensity=1.0)

        # Announce safety issue
        safety_msg = f"Safety issue detected: {violation['type']}. Activating safety protocols."
        self.speech_system.speak_text(safety_msg)

    def _apply_context_modifiers(self, modifiers):
        """Apply context-based behavior modifications."""
        # Adjust speech volume
        target_volume = modifiers['speech_volume']
        self.speech_system.set_volume(target_volume)

        # Adjust gesture intensity
        target_intensity = modifiers['gesture_intensity']
        self.gesture_manager.set_intensity(target_intensity)

        # Adjust personal space behavior
        target_space = modifiers['personal_space']
        self._update_personal_space(target_space)

    def _reset_interaction_state(self):
        """Reset interaction state for new session."""
        self.current_user_id = "unknown"
        self.interaction_mode = "social"
        self.turn_taking_manager.state = ConversationState.IDLE

    def stop_interaction(self):
        """Stop current interaction."""
        self.interaction_active = False
        self.speech_system.stop_listening()

        # Show farewell expression
        self.facial_system.set_expression(FacialExpression.HAPPY, intensity=0.5)

        # Perform farewell gesture
        self.gesture_manager.execute_contextual_gesture('farewell', intensity=0.6)

        # Say goodbye
        farewell = f"Goodbye {self.current_user_id if self.current_user_id != 'unknown' else 'friend'}. It was nice interacting with you."
        self.speech_system.speak_text(farewell)

    def handle_user_speech(self, text):
        """Handle user speech input."""
        # Add to conversation history
        self.turn_taking_manager.process_user_speech(text)

        # Evaluate action ethically
        ethical_eval = self.ethics_manager.evaluate_action_ethically(
            f"respond_to: {text}",
            self.context_manager.get_context_aware_behavior_modifiers()
        )

        if ethical_eval['recommendation'] == 'refuse':
            response = "I'm not sure I can respond to that appropriately."
        elif ethical_eval['recommendation'] == 'require_confirmation':
            response = f"I heard: '{text}'. Before I respond, is this something you'd like me to address?"
        else:
            # Generate context-aware response
            response = self.context_manager.get_adaptive_response(
                f"I understand you said: '{text}'. How can I help?"
            )

        # Speak response
        self.speech_system.speak_text(response)

        # Show appropriate facial expression
        if "happy" in text.lower() or "good" in text.lower():
            self.facial_system.set_expression(FacialExpression.HAPPY, intensity=0.8)
        elif "sad" in text.lower() or "bad" in text.lower():
            self.facial_system.set_expression(FacialExpression.CONCERNED, intensity=0.6)
        else:
            self.facial_system.set_expression(FacialExpression.NEUTRAL, intensity=0.5)

        # Perform appropriate gesture
        self.gesture_manager.execute_contextual_gesture('acknowledgment', intensity=0.5)

    def get_interaction_metrics(self):
        """Get metrics about current interaction."""
        return {
            'interaction_active': self.interaction_active,
            'current_user': self.current_user_id,
            'interaction_mode': self.interaction_mode,
            'conversation_state': self.turn_taking_manager.state.value,
            'safety_status': self.safety_manager.get_safety_status(),
            'context_modifiers': self.context_manager.get_context_aware_behavior_modifiers(),
            'user_attention': self.turn_taking_manager.user_attention_detected
        }
```

## Summary

Humanoid interaction and communication systems require sophisticated integration of multiple modalities including speech, gesture, facial expressions, and contextual awareness. Successful implementation involves:

1. **Multimodal Communication**: Combining speech, gestures, and expressions for natural interaction
2. **Social Intelligence**: Understanding and applying social norms and conventions
3. **Context Awareness**: Adapting behavior based on environmental and social context
4. **Safety Management**: Ensuring safe operation in human environments
5. **Ethical Considerations**: Implementing ethical decision-making in robot behavior
6. **Turn-Taking**: Managing natural conversation flow
7. **Personalization**: Adapting to individual user preferences and familiarity

These systems enable humanoid robots to interact naturally with humans in a variety of settings, from assistive applications to entertainment and education. The key to success lies in creating intuitive, predictable, and safe interactions that enhance human-robot collaboration.