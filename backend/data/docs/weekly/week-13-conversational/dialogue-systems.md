---
sidebar_label: 'Dialogue Systems for Humanoid Robots'
title: 'Dialogue Systems for Humanoid Robots'
---

# Dialogue Systems for Humanoid Robots

## Introduction to Robot Dialogue Systems

Dialogue systems for humanoid robots are specialized conversational AI systems designed to enable natural, context-aware interactions between humans and robots. Unlike traditional chatbots, robot dialogue systems must handle multimodal inputs, real-world grounding, and dynamic environmental contexts while maintaining natural conversation flow.

## Architecture of Robot Dialogue Systems

### Three-Layer Architecture

```
Dialogue Management Layer
├── Context Tracking
├── State Management
├── Policy Selection
└── Response Planning

Natural Language Understanding Layer
├── Intent Classification
├── Entity Extraction
├── Coreference Resolution
└── Sentiment Analysis

Natural Language Generation Layer
├── Response Selection
├── Template Instantiation
├── Surface Realization
└── Personality Adaptation
```

### Component Integration

```python
import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import uuid

class DialogueState(Enum):
    IDLE = "idle"
    GREETING = "greeting"
    LISTENING = "listening"
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    RESPONDING = "responding"
    CONFIRMING = "confirming"
    ERROR = "error"
    GOODBYE = "goodbye"

@dataclass
class ConversationContext:
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "unknown"
    current_state: DialogueState = DialogueState.IDLE
    previous_state: DialogueState = DialogueState.IDLE
    user_profile: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict] = field(default_factory=list)
    current_intent: str = "unknown"
    previous_intent: str = "unknown"
    entities: Dict[str, Any] = field(default_factory=dict)
    context_variables: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    last_interaction_time: float = field(default_factory=time.time)
    engagement_level: float = 0.5

class DialogueManager:
    def __init__(self):
        self.current_context = None
        self.conversation_history = []
        self.dialogue_policies = self.initialize_dialogue_policies()
        self.response_templates = self.load_response_templates()
        self.context_tracker = ContextTracker()
        self.state_transitions = self.define_state_transitions()

    def initialize_dialogue_policies(self):
        """
        Initialize dialogue management policies.
        """
        return {
            DialogueState.GREETING: {
                'entry_conditions': lambda ctx: self.is_first_interaction(ctx),
                'exit_conditions': lambda ctx: self.has_user_responded(ctx),
                'policy_function': self.greeting_policy
            },
            DialogueState.LISTENING: {
                'entry_conditions': lambda ctx: True,
                'exit_conditions': lambda ctx: self.has_input(ctx),
                'policy_function': self.listening_policy
            },
            DialogueState.UNDERSTANDING: {
                'entry_conditions': lambda ctx: self.has_input(ctx),
                'exit_conditions': lambda ctx: self.has_processed_input(ctx),
                'policy_function': self.understanding_policy
            },
            DialogueState.PLANNING: {
                'entry_conditions': lambda ctx: self.has_intent(ctx),
                'exit_conditions': lambda ctx: self.has_planned_response(ctx),
                'policy_function': self.planning_policy
            },
            DialogueState.RESPONDING: {
                'entry_conditions': lambda ctx: self.has_response(ctx),
                'exit_conditions': lambda ctx: self.has_delivered_response(ctx),
                'policy_function': self.responding_policy
            },
            DialogueState.CONFIRMING: {
                'entry_conditions': lambda ctx: self.needs_confirmation(ctx),
                'exit_conditions': lambda ctx: self.has_user_confirmed(ctx),
                'policy_function': self.confirmation_policy
            }
        }

    def define_state_transitions(self):
        """
        Define legal state transitions.
        """
        return {
            DialogueState.IDLE: [DialogueState.GREETING, DialogueState.LISTENING],
            DialogueState.GREETING: [DialogueState.LISTENING, DialogueState.ERROR],
            DialogueState.LISTENING: [DialogueState.UNDERSTANDING, DialogueState.ERROR],
            DialogueState.UNDERSTANDING: [DialogueState.PLANNING, DialogueState.ERROR],
            DialogueState.PLANNING: [DialogueState.RESPONDING, DialogueState.CONFIRMING, DialogueState.ERROR],
            DialogueState.RESPONDING: [DialogueState.LISTENING, DialogueState.GOODBYE, DialogueState.ERROR],
            DialogueState.CONFIRMING: [DialogueState.PLANNING, DialogueState.LISTENING, DialogueState.ERROR],
            DialogueState.ERROR: [DialogueState.LISTENING, DialogueState.IDLE],
            DialogueState.GOODBYE: [DialogueState.IDLE]
        }

    def load_response_templates(self):
        """
        Load response templates for different contexts.
        """
        return {
            'greeting': [
                "Hello! I'm {robot_name}, your humanoid assistant. How can I help you today?",
                "Greetings! I'm {robot_name}. It's nice to meet you. What would you like to do?",
                "Hi there! I'm {robot_name}, ready to assist. What brings you here?"
            ],
            'navigation': [
                "I'll navigate to {location}. Please follow me at a safe distance.",
                "Heading to {location} now. I'll lead the way.",
                "Going to {location}. The path looks clear ahead."
            ],
            'manipulation': [
                "I'll pick up the {object}. Please ensure the area is clear.",
                "Attempting to grasp the {object}. Is this the correct one?",
                "Reaching for the {object}. Please stand back for safety."
            ],
            'information': [
                "Regarding {topic}: {information}",
                "I can tell you about {topic}: {information}",
                "About {topic}, here's what I know: {information}"
            ],
            'confirmation': [
                "Got it! I'll proceed with {action}.",
                "Understood. Executing {action} now.",
                "Confirmed. Working on {action}."
            ],
            'error': [
                "I'm sorry, I didn't quite understand that. Could you repeat it?",
                "I'm having trouble processing your request. Could you rephrase?",
                "I didn't catch that clearly. Please speak more distinctly."
            ],
            'goodbye': [
                "Goodbye! It was nice interacting with you.",
                "See you later! Have a great day.",
                "Farewell! Feel free to come back anytime."
            ]
        }

    def process_user_input(self, user_input: str, user_id: str = "unknown") -> str:
        """
        Process user input through the dialogue system.

        Args:
            user_input: Text input from user
            user_id: Unique identifier for the user

        Returns:
            response: Generated response text
        """
        # Initialize context if needed
        if self.current_context is None or self.current_context.user_id != user_id:
            self.initialize_conversation_context(user_id)

        # Update context with current input
        self.update_context_with_input(user_input)

        # Determine next state based on current state and input
        next_state = self.determine_next_state()

        # Execute policy for the next state
        response = self.execute_policy(next_state)

        # Update context state
        self.current_context.previous_state = self.current_context.current_state
        self.current_context.current_state = next_state
        self.current_context.last_interaction_time = time.time()

        # Store in conversation history
        self.current_context.conversation_history.append({
            'timestamp': time.time(),
            'speaker': 'user',
            'text': user_input,
            'intent': self.current_context.current_intent,
            'entities': self.current_context.entities,
            'response': response
        })

        return response

    def initialize_conversation_context(self, user_id: str):
        """
        Initialize conversation context for a new user interaction.
        """
        self.current_context = ConversationContext(
            user_id=user_id,
            current_state=DialogueState.IDLE,
            user_profile=self.get_user_profile(user_id),
            confidence_threshold=0.6,
            engagement_level=0.5
        )

    def update_context_with_input(self, user_input: str):
        """
        Update conversation context with new user input.
        """
        # This would typically call NLU system to extract intent and entities
        # For this example, we'll use simple keyword-based classification
        nlu_result = self.simple_nlu_classification(user_input)

        self.current_context.current_intent = nlu_result['intent']
        self.current_context.entities = nlu_result['entities']
        self.current_context.confidence_threshold = nlu_result['confidence']

    def simple_nlu_classification(self, text: str):
        """
        Simple NLU classification using keyword matching.
        In practice, this would use machine learning models.
        """
        text_lower = text.lower()

        # Intent classification
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            intent = 'greeting'
        elif any(word in text_lower for word in ['go to', 'move to', 'navigate to', 'walk to']):
            intent = 'navigation'
        elif any(word in text_lower for word in ['pick up', 'grasp', 'take', 'grab']):
            intent = 'manipulation'
        elif any(word in text_lower for word in ['what', 'how', 'when', 'where', 'who', 'why']):
            intent = 'information_request'
        elif any(word in text_lower for word in ['yes', 'yeah', 'sure', 'ok', 'okay']):
            intent = 'confirmation'
        elif any(word in text_lower for word in ['no', 'nope', 'cancel', 'stop']):
            intent = 'negation'
        elif any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            intent = 'goodbye'
        else:
            intent = 'unknown'

        # Entity extraction (simplified)
        entities = {}
        if intent == 'navigation':
            # Extract location entity
            for word in text.split():
                if word in ['kitchen', 'office', 'bedroom', 'living room', 'bathroom', 'hallway']:
                    entities['location'] = word
                    break
        elif intent == 'manipulation':
            # Extract object entity
            for word in text.split():
                if word in ['cup', 'bottle', 'book', 'ball', 'box', 'pen']:
                    entities['object'] = word
                    break

        return {
            'intent': intent,
            'entities': entities,
            'confidence': 0.8 if intent != 'unknown' else 0.3
        }

    def determine_next_state(self) -> DialogueState:
        """
        Determine the next dialogue state based on current context.
        """
        current_state = self.current_context.current_state
        current_intent = self.current_context.current_intent
        confidence = self.current_context.confidence_threshold

        # Check if confidence is too low
        if confidence < self.current_context.confidence_threshold:
            return DialogueState.ERROR

        # State transition logic
        if current_state == DialogueState.IDLE:
            if current_intent == 'greeting':
                return DialogueState.GREETING
            else:
                return DialogueState.LISTENING

        elif current_state == DialogueState.GREETING:
            return DialogueState.LISTENING

        elif current_state == DialogueState.LISTENING:
            if current_intent != 'unknown':
                return DialogueState.UNDERSTANDING
            else:
                return DialogueState.ERROR

        elif current_state == DialogueState.UNDERSTANDING:
            if current_intent in ['navigation', 'manipulation']:
                # These intents may need confirmation
                return DialogueState.CONFIRMING
            else:
                return DialogueState.PLANNING

        elif current_state == DialogueState.CONFIRMING:
            # Wait for user confirmation
            # This would typically check for confirmation in next input
            return DialogueState.PLANNING  # Simplified for this example

        elif current_state == DialogueState.PLANNING:
            return DialogueState.RESPONDING

        elif current_state == DialogueState.RESPONDING:
            if current_intent == 'goodbye':
                return DialogueState.GOODBYE
            else:
                return DialogueState.LISTENING

        elif current_state == DialogueState.ERROR:
            return DialogueState.LISTENING

        else:
            return DialogueState.LISTENING

    def execute_policy(self, state: DialogueState) -> str:
        """
        Execute the policy for the given state.
        """
        policy_function = self.dialogue_policies[state]['policy_function']
        return policy_function()

    def greeting_policy(self) -> str:
        """
        Policy for greeting state.
        """
        robot_name = self.current_context.context_variables.get('robot_name', 'Robot')
        template = self.select_template('greeting')
        return template.format(robot_name=robot_name)

    def listening_policy(self) -> str:
        """
        Policy for listening state.
        """
        return "I'm listening. What would you like to say?"

    def understanding_policy(self) -> str:
        """
        Policy for understanding state.
        """
        intent = self.current_context.current_intent
        entities = self.current_context.entities

        if intent == 'navigation':
            location = entities.get('location', 'the destination')
            template = self.select_template('navigation')
            return template.format(location=location)

        elif intent == 'manipulation':
            obj = entities.get('object', 'the object')
            template = self.select_template('manipulation')
            return template.format(object=obj)

        elif intent == 'information_request':
            topic = ' '.join(entities.get('object', ['that']))
            # In a real system, this would query a knowledge base
            info = self.query_knowledge_base(topic)
            template = self.select_template('information')
            return template.format(topic=topic, information=info)

        elif intent == 'greeting':
            return self.select_template('greeting').format(robot_name='Robot')

        elif intent == 'goodbye':
            return self.select_template('goodbye')

        else:
            return self.select_template('error')

    def planning_policy(self) -> str:
        """
        Policy for planning state.
        """
        intent = self.current_context.current_intent
        entities = self.current_context.entities

        if intent == 'navigation':
            location = entities.get('location', 'the destination')
            return f"Planning route to {location}. Please wait a moment."

        elif intent == 'manipulation':
            obj = entities.get('object', 'the object')
            return f"Planning manipulation of {obj}. Calculating optimal grasp."

        elif intent == 'information_request':
            topic = ' '.join(entities.get('object', ['that']))
            return f"Looking up information about {topic}."

        else:
            return "Processing your request."

    def responding_policy(self) -> str:
        """
        Policy for responding state.
        """
        # This would execute the planned actions and generate responses
        return "I've processed your request and executed the appropriate actions."

    def confirmation_policy(self) -> str:
        """
        Policy for confirmation state.
        """
        intent = self.current_context.current_intent
        entities = self.current_context.entities

        if intent == 'navigation':
            location = entities.get('location', 'the destination')
            return f"Should I navigate to {location}? Please confirm with yes or no."

        elif intent == 'manipulation':
            obj = entities.get('object', 'the object')
            return f"Should I pick up the {obj}? Please confirm with yes or no."

        return "I need your confirmation before proceeding. Please respond yes or no."

    def error_policy(self) -> str:
        """
        Policy for error state.
        """
        return self.select_template('error')

    def goodbye_policy(self) -> str:
        """
        Policy for goodbye state.
        """
        return self.select_template('goodbye')

    def select_template(self, template_type: str) -> str:
        """
        Select an appropriate template based on type and context.
        """
        import random
        templates = self.response_templates.get(template_type, ["I understand."])
        return random.choice(templates)

    def query_knowledge_base(self, topic: str) -> str:
        """
        Query knowledge base for information.
        This is a simplified implementation.
        """
        # In a real system, this would query a comprehensive knowledge base
        knowledge_base = {
            'robot': "I am a humanoid robot designed to assist humans through natural interaction.",
            'ai': "Artificial Intelligence is the simulation of human intelligence processes by machines.",
            'navigation': "Navigation involves planning and executing movement from one location to another.",
            'manipulation': "Manipulation refers to the robot's ability to interact with objects in the environment.",
            'greeting': "A greeting is a polite acknowledgment of someone's presence.",
            'conversation': "Conversation is a talk between two or more people."
        }

        return knowledge_base.get(topic.lower(), "I don't have specific information about that topic.")
```

## Context Tracking and Management

### Multi-Modal Context Integration

```python
class ContextTracker:
    def __init__(self):
        self.context_memory = {}
        self.long_term_memory = {}
        self.episodic_memory = []
        self.working_memory = {}

        # Context dimensions
        self.spatial_context = SpatialContext()
        self.temporal_context = TemporalContext()
        self.social_context = SocialContext()
        self.task_context = TaskContext()

    def update_context(self, input_data, sensor_data, environment_state):
        """
        Update all context dimensions with new information.

        Args:
            input_data: User input and NLU results
            sensor_data: Robot sensor readings
            environment_state: Current environment information
        """
        # Update spatial context
        self.spatial_context.update(
            robot_pose=environment_state.get('robot_pose'),
            object_positions=environment_state.get('object_positions'),
            user_position=input_data.get('user_position')
        )

        # Update temporal context
        self.temporal_context.update(
            current_time=time.time(),
            conversation_duration=self.get_conversation_duration(),
            task_deadline=input_data.get('deadline')
        )

        # Update social context
        self.social_context.update(
            user_profile=input_data.get('user_profile'),
            interaction_history=input_data.get('conversation_history', []),
            social_cues=sensor_data.get('social_cues', {})
        )

        # Update task context
        self.task_context.update(
            current_task=input_data.get('current_task'),
            task_progress=input_data.get('task_progress', 0.0),
            task_dependencies=input_data.get('task_dependencies', [])
        )

        # Consolidate all context information
        self.working_memory = {
            'spatial': self.spatial_context.get_current_state(),
            'temporal': self.temporal_context.get_current_state(),
            'social': self.social_context.get_current_state(),
            'task': self.task_context.get_current_state(),
            'combined': self.combine_contexts()
        }

    def combine_contexts(self):
        """
        Combine different context dimensions into unified representation.
        """
        combined_context = {}

        # Spatial-temporal integration
        combined_context['spatio_temporal'] = {
            'location_at_time': self.spatial_context.get_location_at_time(
                self.temporal_context.current_time
            ),
            'movement_patterns': self.spatial_context.get_movement_patterns(
                self.temporal_context.get_recent_time_window()
            )
        }

        # Social-task integration
        combined_context['social_task'] = {
            'task_preferences': self.social_context.get_task_preferences(),
            'collaboration_style': self.social_context.get_collaboration_style(),
            'helpfulness_level': self.social_context.get_helpfulness_level()
        }

        # Task-spatial integration
        combined_context['task_spatial'] = {
            'relevant_objects': self.task_context.get_relevant_objects(
                self.spatial_context.get_visible_objects()
            ),
            'required_positions': self.task_context.get_required_positions(
                self.spatial_context.get_available_positions()
            )
        }

        return combined_context

    def get_context_relevance(self, intent, entities):
        """
        Determine which context dimensions are relevant for the current intent.
        """
        relevance_scores = {
            'spatial': 0.0,
            'temporal': 0.0,
            'social': 0.0,
            'task': 0.0
        }

        # Spatial relevance
        spatial_intents = ['navigation', 'manipulation', 'location_query', 'object_identification']
        if intent in spatial_intents:
            relevance_scores['spatial'] = 0.9

        # Temporal relevance
        temporal_intents = ['schedule_query', 'time_request', 'duration_query', 'timing']
        if intent in temporal_intents:
            relevance_scores['temporal'] = 0.8

        # Social relevance
        social_intents = ['greeting', 'farewell', 'social_interaction', 'politeness']
        if intent in social_intents:
            relevance_scores['social'] = 0.9

        # Task relevance
        task_intents = ['task_request', 'command', 'action', 'procedure']
        if intent in task_intents:
            relevance_scores['task'] = 0.8

        return relevance_scores

    def resolve_coreferences(self, entities, context):
        """
        Resolve pronouns and spatial references using context.
        """
        resolved_entities = []

        for entity in entities:
            if entity['type'] == 'pronoun':
                # Resolve pronoun to entity from context
                resolved = self.resolve_pronoun(entity, context)
                if resolved:
                    resolved_entities.append(resolved)
                else:
                    resolved_entities.append(entity)
            elif entity['type'] == 'spatial_reference':
                # Resolve spatial reference (there, here, that) using spatial context
                resolved = self.resolve_spatial_reference(entity, context)
                if resolved:
                    resolved_entities.append(resolved)
                else:
                    resolved_entities.append(entity)
            else:
                resolved_entities.append(entity)

        return resolved_entities

    def resolve_pronoun(self, pronoun_entity, context):
        """
        Resolve pronoun to specific entity from context.
        """
        # Look for potential antecedents in recent conversation
        recent_entities = self.get_recent_entities(context)

        # Simple resolution rules
        if pronoun_entity['text'] in ['it', 'this', 'that']:
            # Likely refers to most recently mentioned object
            for entity in reversed(recent_entities):
                if entity['type'] in ['object', 'location', 'person']:
                    return {
                        'text': entity['text'],
                        'type': entity['type'],
                        'resolved_from': pronoun_entity['text'],
                        'confidence': 0.8
                    }

        elif pronoun_entity['text'] in ['they', 'them']:
            # Likely refers to multiple entities
            people_entities = [e for e in recent_entities if e['type'] == 'person']
            if people_entities:
                return {
                    'text': ', '.join([e['text'] for e in people_entities]),
                    'type': 'person_group',
                    'resolved_from': pronoun_entity['text'],
                    'confidence': 0.7
                }

        return None

    def resolve_spatial_reference(self, spatial_entity, context):
        """
        Resolve spatial reference like 'there' or 'here' to specific location.
        """
        if spatial_entity['text'] == 'here':
            # 'Here' typically refers to robot's current location
            robot_pos = context.get('spatial', {}).get('robot_position', [0, 0, 0])
            return {
                'text': f"at position ({robot_pos[0]:.2f}, {robot_pos[1]:.2f})",
                'type': 'location',
                'resolved_from': spatial_entity['text'],
                'confidence': 0.9
            }

        elif spatial_entity['text'] == 'there':
            # 'There' typically refers to user's indicated location or recent reference
            user_gaze = context.get('spatial', {}).get('user_gaze_direction')
            if user_gaze:
                # Calculate location based on gaze direction
                distance = 1.0  # Default distance
                target_pos = [robot_pos[i] + user_gaze[i] * distance for i in range(3)]
                return {
                    'text': f"at position ({target_pos[0]:.2f}, {target_pos[1]:.2f})",
                    'type': 'location',
                    'resolved_from': spatial_entity['text'],
                    'confidence': 0.6
                }

        return None

    def get_recent_entities(self, context, lookback=5):
        """
        Get entities from recent conversation history.
        """
        recent_entities = []
        conversation_history = context.get('conversation_history', [])

        for exchange in reversed(conversation_history[-lookback:]):
            if 'entities' in exchange:
                recent_entities.extend(exchange['entities'])

        return recent_entities

    def update_long_term_memory(self, conversation_summary):
        """
        Update long-term memory with conversation insights.
        """
        user_id = conversation_summary.get('user_id', 'unknown')

        if user_id not in self.long_term_memory:
            self.long_term_memory[user_id] = {
                'preferences': {},
                'interaction_patterns': [],
                'familiarity_level': 0.0,
                'last_interaction': time.time()
            }

        # Update user profile based on conversation
        profile = self.long_term_memory[user_id]

        # Update preferences
        for pref_type, pref_value in conversation_summary.get('preferences', {}).items():
            if pref_type not in profile['preferences']:
                profile['preferences'][pref_type] = []
            profile['preferences'][pref_type].append(pref_value)

        # Update interaction patterns
        profile['interaction_patterns'].append({
            'timestamp': time.time(),
            'intent_frequency': conversation_summary.get('intent_frequency', {}),
            'response_success': conversation_summary.get('response_success', True)
        })

        # Update familiarity level
        profile['familiarity_level'] = min(1.0, profile['familiarity_level'] + 0.1)

        # Keep only recent patterns (last 100 interactions)
        if len(profile['interaction_patterns']) > 100:
            profile['interaction_patterns'] = profile['interaction_patterns'][-100:]

        profile['last_interaction'] = time.time()

    def get_user_context(self, user_id):
        """
        Get user-specific context information.
        """
        if user_id in self.long_term_memory:
            return self.long_term_memory[user_id]
        else:
            return {
                'preferences': {},
                'interaction_patterns': [],
                'familiarity_level': 0.0,
                'last_interaction': 0
            }

class SpatialContext:
    def __init__(self):
        self.robot_position = [0, 0, 0]
        self.robot_orientation = [0, 0, 0, 1]  # quaternion
        self.object_positions = {}
        self.visible_objects = []
        self.navigation_map = None
        self.spatial_relations = {}

    def update(self, robot_pose=None, object_positions=None, user_position=None):
        """Update spatial context with new information."""
        if robot_pose:
            self.robot_position = robot_pose[:3]
            self.robot_orientation = robot_pose[3:]

        if object_positions:
            self.object_positions.update(object_positions)

        if user_position:
            self.user_position = user_position

    def get_distance_to_object(self, object_name):
        """Get distance from robot to object."""
        if object_name in self.object_positions:
            obj_pos = self.object_positions[object_name]
            dist = np.linalg.norm(np.array(self.robot_position) - np.array(obj_pos))
            return dist
        return float('inf')

    def get_objects_in_range(self, center, radius):
        """Get objects within a certain range of a center point."""
        objects_in_range = []
        center_pos = np.array(center)

        for obj_name, obj_pos in self.object_positions.items():
            dist = np.linalg.norm(center_pos - np.array(obj_pos))
            if dist <= radius:
                objects_in_range.append((obj_name, dist))

        return objects_in_range

    def calculate_path_to_object(self, object_name):
        """Calculate navigation path to object."""
        if object_name not in self.object_positions:
            return None

        target_pos = self.object_positions[object_name]
        # This would use a path planning algorithm
        # For this example, return direct path
        return [self.robot_position, target_pos]

class TemporalContext:
    def __init__(self):
        self.start_time = time.time()
        self.current_time = time.time()
        self.conversation_timer = 0.0
        self.event_timeline = []
        self.temporal_patterns = {}

    def update(self, current_time, conversation_duration=None, task_deadline=None):
        """Update temporal context."""
        self.current_time = current_time
        self.conversation_timer = current_time - self.start_time

        if task_deadline:
            self.task_deadline = task_deadline

    def get_recent_time_window(self, duration=30):
        """Get events from recent time window."""
        recent_events = []
        for event in self.event_timeline:
            if self.current_time - event['timestamp'] <= duration:
                recent_events.append(event)
        return recent_events

    def get_time_of_day_context(self):
        """Get time-of-day specific context."""
        hour = datetime.fromtimestamp(self.current_time).hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

class SocialContext:
    def __init__(self):
        self.user_profile = {}
        self.social_cues = {}
        self.interaction_history = []
        self.social_preferences = {}

    def update(self, user_profile=None, interaction_history=None, social_cues=None):
        """Update social context."""
        if user_profile:
            self.user_profile.update(user_profile)

        if interaction_history:
            self.interaction_history.extend(interaction_history)

        if social_cues:
            self.social_cues.update(social_cues)

    def get_task_preferences(self):
        """Get user's task preferences."""
        return self.user_profile.get('task_preferences', {})

    def get_collaboration_style(self):
        """Get user's preferred collaboration style."""
        return self.user_profile.get('collaboration_style', 'collaborative')

    def get_helpfulness_level(self):
        """Get user's preferred helpfulness level."""
        return self.user_profile.get('helpfulness_preference', 'moderate')
```

## Dialogue State Tracking

### Belief State Management

```python
class BeliefStateTracker:
    def __init__(self):
        self.belief_states = {}
        self.confidence_thresholds = {
            'intent': 0.7,
            'entity': 0.6,
            'slot': 0.65,
            'action': 0.8
        }

    def update_belief_state(self, observation, action_taken=None):
        """
        Update belief state based on observation and action taken.

        Args:
            observation: New observation (user input, sensor data, etc.)
            action_taken: Action taken by the system (for updating action beliefs)
        """
        # Initialize belief state if needed
        if 'current' not in self.belief_states:
            self.belief_states['current'] = self.initialize_belief_state()

        # Get previous belief state
        previous_state = self.belief_states['current'].copy()

        # Update beliefs based on observation
        updated_state = self.belief_states['current'].copy()

        # Update intent belief
        if 'intent' in observation:
            intent_prob = observation['intent']['probability']
            intent_name = observation['intent']['name']

            if intent_prob > self.confidence_thresholds['intent']:
                updated_state['current_intent'] = intent_name
                updated_state['intent_confidence'] = intent_prob

        # Update entity beliefs
        if 'entities' in observation:
            for entity in observation['entities']:
                entity_type = entity['type']
                entity_value = entity['value']
                entity_confidence = entity.get('confidence', 0.5)

                if entity_confidence > self.confidence_thresholds['entity']:
                    if entity_type not in updated_state['entities']:
                        updated_state['entities'][entity_type] = []

                    # Add entity if not already present or if higher confidence
                    existing_entity = next((e for e in updated_state['entities'][entity_type]
                                          if e['value'] == entity_value), None)

                    if existing_entity is None or existing_entity['confidence'] < entity_confidence:
                        updated_state['entities'][entity_type].append({
                            'value': entity_value,
                            'confidence': entity_confidence,
                            'timestamp': time.time()
                        })

        # Update slot filling beliefs
        if 'slots' in observation:
            for slot_name, slot_value in observation['slots'].items():
                if slot_name not in updated_state['slots_filled']:
                    updated_state['slots_filled'][slot_name] = {
                        'value': slot_value,
                        'confidence': 0.8,
                        'timestamp': time.time()
                    }

        # Update action beliefs
        if action_taken:
            updated_state['last_action'] = action_taken
            updated_state['action_outcome_expected'] = observation.get('expected_outcome', None)

        # Store in belief states
        self.belief_states['previous'] = previous_state
        self.belief_states['current'] = updated_state

        return updated_state

    def initialize_belief_state(self):
        """Initialize the belief state."""
        return {
            'current_intent': 'unknown',
            'intent_confidence': 0.0,
            'entities': {},
            'slots_filled': {},
            'task_progress': {},
            'user_state': 'neutral',
            'conversation_purpose': 'exploration',
            'last_action': None,
            'action_outcome_expected': None,
            'belief_confidence': 0.5
        }

    def get_belief_probability(self, variable, value):
        """
        Get the probability of a specific belief value.

        Args:
            variable: The variable name (e.g., 'intent', 'location', 'action')
            value: The value to check probability for

        Returns:
            probability: Probability of the value being correct
        """
        if variable == 'intent':
            current_intent = self.belief_states['current'].get('current_intent', 'unknown')
            confidence = self.belief_states['current'].get('intent_confidence', 0.0)
            return confidence if current_intent == value else (1 - confidence) / 10  # Small prob for others

        elif variable in self.belief_states['current']['entities']:
            entities = self.belief_states['current']['entities'][variable]
            entity = next((e for e in entities if e['value'] == value), None)
            return entity['confidence'] if entity else 0.0

        return 0.0

    def is_slot_filled(self, slot_name):
        """Check if a slot is filled with sufficient confidence."""
        if slot_name in self.belief_states['current']['slots_filled']:
            slot_info = self.belief_states['current']['slots_filled'][slot_name]
            return slot_info['confidence'] > self.confidence_thresholds['slot']
        return False

    def get_missing_slots(self, required_slots):
        """Get slots that are still missing from the belief state."""
        missing = []
        for slot in required_slots:
            if not self.is_slot_filled(slot):
                missing.append(slot)
        return missing

    def predict_user_intention(self):
        """
        Predict user's intention based on current belief state.
        """
        current_intent = self.belief_states['current']['current_intent']
        entities = self.belief_states['current']['entities']
        conversation_purpose = self.belief_states['current']['conversation_purpose']

        # Complex intention prediction based on multiple factors
        intention = {
            'primary': current_intent,
            'confidence': self.belief_states['current']['intent_confidence'],
            'contextual': [],
            'predicted_outcome': None
        }

        # Add contextual intentions based on entities
        if 'location' in entities and current_intent == 'navigation':
            intention['contextual'].append('navigation_to_specific_location')

        if 'object' in entities and current_intent == 'manipulation':
            intention['contextual'].append('manipulation_of_specific_object')

        # Predict outcome based on current state
        if current_intent == 'information_request':
            intention['predicted_outcome'] = 'information_acquired'
        elif current_intent == 'navigation':
            intention['predicted_outcome'] = 'destination_reached'
        elif current_intent == 'manipulation':
            intention['predicted_outcome'] = 'object_manipulated'

        return intention

    def calculate_dialogue_act_probability(self, dialogue_act, context):
        """
        Calculate probability of a specific dialogue act given current context.
        """
        # This would use a more sophisticated model in practice
        # For this example, we'll use simple heuristics

        act_probabilities = {
            'greeting': 0.1,
            'question': 0.2,
            'command': 0.3,
            'statement': 0.4,
            'confirmation': 0.1,
            'acknowledgment': 0.2,
            'explanation': 0.15,
            'request_for_clarification': 0.25
        }

        # Adjust based on context
        if context.get('first_interaction', False):
            act_probabilities['greeting'] = 0.8

        if context.get('low_confidence', False):
            act_probabilities['request_for_clarification'] = 0.7

        return act_probabilities.get(dialogue_act, 0.1)

class DialoguePolicyManager:
    def __init__(self):
        self.policies = {}
        self.policy_weights = {}
        self.current_policy = 'default'
        self.learning_enabled = True
        self.policy_performance = {}

    def add_policy(self, policy_name, policy_function, conditions=None):
        """
        Add a dialogue policy with optional conditions.

        Args:
            policy_name: Name of the policy
            policy_function: Function implementing the policy
            conditions: Conditions under which to use this policy
        """
        self.policies[policy_name] = {
            'function': policy_function,
            'conditions': conditions or [],
            'performance': {'success': 0, 'attempts': 0, 'avg_response_time': 0.0}
        }
        self.policy_weights[policy_name] = 1.0  # Equal initial weight

    def select_policy(self, context):
        """
        Select the most appropriate policy based on current context.
        """
        applicable_policies = []

        for policy_name, policy_info in self.policies.items():
            meets_conditions = True

            for condition in policy_info['conditions']:
                if not condition(context):
                    meets_conditions = False
                    break

            if meets_conditions:
                applicable_policies.append(policy_name)

        if not applicable_policies:
            return 'default'

        # Select policy based on weighted probability
        if len(applicable_policies) == 1:
            return applicable_policies[0]

        # Calculate weighted selection
        total_weight = sum(self.policy_weights[pol] for pol in applicable_policies)
        if total_weight == 0:
            return applicable_policies[0]

        # Use weighted random selection
        import random
        weights = [self.policy_weights[pol] for pol in applicable_policies]
        selected_policy = random.choices(applicable_policies, weights=weights)[0]

        return selected_policy

    def execute_policy(self, policy_name, context):
        """
        Execute the specified dialogue policy.
        """
        if policy_name in self.policies:
            start_time = time.time()

            try:
                response = self.policies[policy_name]['function'](context)

                # Update performance metrics
                execution_time = time.time() - start_time
                self.update_policy_performance(policy_name, True, execution_time)

                return response
            except Exception as e:
                self.get_logger().error(f'Policy {policy_name} execution failed: {e}')
                self.update_policy_performance(policy_name, False, time.time() - start_time)
                # Fall back to default policy
                return self.policies.get('default', {'response': 'I encountered an error processing your request.'})
        else:
            return {'response': 'No policy available for this situation.'}

    def update_policy_performance(self, policy_name, success, execution_time):
        """
        Update performance metrics for a policy.
        """
        if policy_name in self.policies:
            perf = self.policies[policy_name]['performance']

            perf['attempts'] += 1
            if success:
                perf['success'] += 1

            # Update average response time
            old_avg = perf['avg_response_time']
            new_attempts = perf['attempts']
            perf['avg_response_time'] = (old_avg * (new_attempts - 1) + execution_time) / new_attempts

    def adapt_policy_weights(self):
        """
        Adapt policy weights based on performance.
        """
        if not self.learning_enabled:
            return

        for policy_name, policy_info in self.policies.items():
            perf = policy_info['performance']

            if perf['attempts'] > 0:
                success_rate = perf['success'] / perf['attempts']
                time_efficiency = 1.0 / (perf['avg_response_time'] + 0.1)  # Avoid division by zero

                # Combine success rate and efficiency
                new_weight = success_rate * 0.7 + time_efficiency * 0.3
                self.policy_weights[policy_name] = max(0.1, new_weight)  # Minimum weight of 0.1

    def get_policy_recommendation(self, user_input, context):
        """
        Get policy recommendation for handling user input.
        """
        # Analyze input characteristics
        input_length = len(user_input.split())
        input_complexity = self.estimate_input_complexity(user_input)
        user_familiarity = context.get('user_familiarity', 0.5)

        # Select policy based on input characteristics
        if input_length < 3 and input_complexity < 0.3:
            # Short, simple input - use direct response policy
            return 'direct_response'
        elif user_familiarity > 0.7:
            # Familiar user - use more autonomous policy
            return 'autonomous_response'
        elif input_complexity > 0.7:
            # Complex input - use detailed analysis policy
            return 'detailed_analysis'
        else:
            # Default policy for normal inputs
            return 'standard_response'

    def estimate_input_complexity(self, text):
        """
        Estimate complexity of input text.
        """
        import re

        # Count different types of linguistic elements
        words = text.split()
        word_count = len(words)

        # Count complex elements
        question_words = len(re.findall(r'\b(what|how|when|where|why|who|which|whose)\b', text.lower()))
        punctuation_complexity = text.count('?') + text.count('!') + text.count(':') + text.count(';')
        number_count = len(re.findall(r'\b\d+\b', text))

        # Calculate complexity score (0-1)
        complexity_score = (question_words + punctuation_complexity + number_count) / max(word_count, 1)

        return min(1.0, complexity_score)
```

## Natural Language Generation for Robotics

### Context-Aware Response Generation

```python
class ContextAwareNLG:
    def __init__(self):
        self.response_templates = self.load_response_templates()
        self.personality_module = PersonalityModule()
        self.context_sensitive_rules = self.define_context_rules()

    def load_response_templates(self):
        """
        Load response templates with context parameters.
        """
        return {
            'navigation': {
                'success': [
                    {
                        'template': "I'm navigating to {location}. Please follow me at a safe distance.",
                        'conditions': {'user_familiarity': lambda x: x > 0.5},
                        'priority': 1
                    },
                    {
                        'template': "Heading to {location} now. I'll lead the way.",
                        'conditions': {'user_familiarity': lambda x: x <= 0.5},
                        'priority': 1
                    }
                ],
                'failure': [
                    {
                        'template': "I'm having trouble navigating to {location}. The path seems blocked.",
                        'conditions': {'obstacle_detected': lambda x: x},
                        'priority': 1
                    }
                ]
            },
            'manipulation': {
                'success': [
                    {
                        'template': "Successfully grasped the {object}. What should I do with it?",
                        'conditions': {'grasp_success': lambda x: x},
                        'priority': 1
                    }
                ],
                'failure': [
                    {
                        'template': "I'm having difficulty grasping {object}. Could you adjust its position?",
                        'conditions': {'grasp_failure': lambda x: x},
                        'priority': 1
                    }
                ]
            },
            'information_request': {
                'positive': [
                    {
                        'template': "About {topic}: {information}",
                        'conditions': {'knowledge_available': lambda x: x},
                        'priority': 1
                    }
                ],
                'negative': [
                    {
                        'template': "I don't have specific information about {topic}. Could you ask about something else?",
                        'conditions': {'knowledge_available': lambda x: not x},
                        'priority': 1
                    }
                ]
            }
        }

    def define_context_rules(self):
        """
        Define rules for context-sensitive response generation.
        """
        return [
            {
                'condition': lambda ctx: ctx.get('time_of_day') == 'morning',
                'action': lambda resp: f"Good morning! {resp}",
                'priority': 10
            },
            {
                'condition': lambda ctx: ctx.get('user_familiarity', 0) > 0.8,
                'action': lambda resp: f"{resp} You're a familiar user - I remember our previous interactions!",
                'priority': 5
            },
            {
                'condition': lambda ctx: ctx.get('user_familiarity', 0) < 0.3,
                'action': lambda resp: f"{resp} I'm still learning about you. Please let me know if I can assist further.",
                'priority': 5
            },
            {
                'condition': lambda ctx: ctx.get('conversation_length', 0) > 10,
                'action': lambda resp: f"{resp} We've been talking for a while. Is there anything specific you'd like me to do?",
                'priority': 3
            },
            {
                'condition': lambda ctx: ctx.get('low_confidence', False),
                'action': lambda resp: f"{resp} I'm not entirely confident about this response. Please let me know if I misunderstood.",
                'priority': 8
            }
        ]

    def generate_response(self, intent, entities, context, confidence=0.8):
        """
        Generate context-aware response.

        Args:
            intent: Classified intent
            entities: Extracted entities
            context: Current context information
            confidence: Confidence in classification

        Returns:
            response: Generated natural language response
        """
        # Select template based on intent and context
        template = self.select_template(intent, entities, context, confidence)

        # Fill template with entities
        filled_response = self.fill_template(template, entities)

        # Apply personality
        personalized_response = self.personality_module.apply_personality(
            filled_response, context.get('user_profile', {})
        )

        # Apply context-sensitive rules
        contextual_response = self.apply_context_rules(personalized_response, context)

        # Add emotional tone if applicable
        final_response = self.add_emotional_tone(contextual_response, context)

        return final_response

    def select_template(self, intent, entities, context, confidence):
        """
        Select appropriate template based on intent, entities, and context.
        """
        if intent not in self.response_templates:
            return "I'm not sure how to respond to that. Could you rephrase?"

        intent_templates = self.response_templates[intent]

        # Determine success/failure based on context
        outcome = 'success' if confidence > 0.7 else 'failure'

        if outcome in intent_templates:
            # Find templates that match context conditions
            applicable_templates = []

            for template in intent_templates[outcome]:
                matches_conditions = True
                for condition_name, condition_func in template['conditions'].items():
                    if condition_name in context:
                        if not condition_func(context[condition_name]):
                            matches_conditions = False
                            break
                    elif condition_name in entities:
                        if not condition_func(entities[condition_name]):
                            matches_conditions = False
                            break

                if matches_conditions:
                    applicable_templates.append(template)

            # Sort by priority and return first one
            if applicable_templates:
                applicable_templates.sort(key=lambda x: x['priority'], reverse=True)
                return applicable_templates[0]['template']

        # If no conditional templates match, return first available template
        if intent_templates.get(outcome):
            return intent_templates[outcome][0]['template']

        # Fallback to generic template
        return self.get_generic_template(intent)

    def fill_template(self, template, entities):
        """
        Fill template with entity values.
        """
        filled_template = template

        # Replace placeholders with entity values
        for entity_type, entity_value in entities.items():
            if isinstance(entity_value, dict):
                # Handle entity dictionaries
                entity_text = entity_value.get('text', str(entity_value))
            else:
                entity_text = str(entity_value)

            # Replace both {entity_type} and {entity_type.text} patterns
            filled_template = filled_template.replace(f'{{{entity_type}}}', entity_text)
            filled_template = filled_template.replace(f'{{{entity_type}.text}}', entity_text)

        return filled_template

    def apply_context_rules(self, response, context):
        """
        Apply context-sensitive rules to modify response.
        """
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.context_sensitive_rules, key=lambda x: x['priority'], reverse=True)

        modified_response = response

        for rule in sorted_rules:
            if rule['condition'](context):
                modified_response = rule['action'](modified_response)

        return modified_response

    def add_emotional_tone(self, response, context):
        """
        Add appropriate emotional tone based on context.
        """
        emotional_tone = context.get('emotional_state', 'neutral')

        if emotional_tone == 'happy':
            return f"{response} :)"  # Add positive emoji or tone
        elif emotional_tone == 'sad':
            return f"{response} I understand if you're feeling down. I'm here to help."  # Add empathy
        elif emotional_tone == 'excited':
            return f"{response} That sounds exciting! I'm enthusiastic about helping with that!"  # Add excitement
        elif emotional_tone == 'concerned':
            return f"{response} I'll be careful and mindful during this task."  # Add caution
        else:
            return response  # Neutral tone

    def get_generic_template(self, intent):
        """
        Get generic template for unknown intent.
        """
        generic_templates = {
            'greeting': "Hello! How can I assist you today?",
            'navigation': "I can help with navigation. Where would you like to go?",
            'manipulation': "I can assist with object manipulation. What would you like me to interact with?",
            'information_request': "I'd be happy to provide information. What would you like to know?",
            'confirmation': "I understand. How should I proceed?",
            'goodbye': "Goodbye! It was nice interacting with you.",
            'unknown': "I'm not sure I understand. Could you rephrase that?"
        }

        return generic_templates.get(intent, generic_templates['unknown'])

class PersonalityModule:
    def __init__(self):
        self.personality_traits = {
            'extraversion': 0.6,
            'agreeableness': 0.8,
            'conscientiousness': 0.7,
            'emotional_stability': 0.7,
            'openness': 0.6
        }

        self.personality_expressions = {
            'extraversion': {
                'high': ['!', 'Great!', 'Wonderful!', 'Fantastic!'],
                'low': ['.', 'Okay.', 'I see.', 'Understood.']
            },
            'agreeableness': {
                'high': ['Please', 'Thank you', 'You\'re welcome', 'I\'d be happy to'],
                'low': ['Sure', 'OK', 'Got it', 'Done']
            },
            'conscientiousness': {
                'high': ['I\'ll make sure to', 'I\'ll be careful to', 'I\'ll pay attention to'],
                'low': ['I\'ll', 'I will', 'I can']
            }
        }

    def apply_personality(self, response, user_profile):
        """
        Apply personality traits to response.
        """
        modified_response = response

        # Apply extraversion
        extraversion_level = user_profile.get('extraversion', self.personality_traits['extraversion'])
        if extraversion_level > 0.7:
            # Add enthusiasm
            positive_expressions = self.personality_expressions['extraversion']['high']
            if random.random() < 0.3:  # 30% chance to add enthusiasm
                modifier = random.choice(positive_expressions)
                modified_response = f"{modifier} {modified_response}"

        # Apply agreeableness
        agreeableness_level = user_profile.get('agreeableness', self.personality_traits['agreeableness'])
        if agreeableness_level > 0.7:
            # Add politeness
            polite_expressions = self.personality_expressions['agreeableness']['high']
            if 'please' not in response.lower():
                modified_response = f"I'd be happy to {modified_response.lower()}" if modified_response[0].isupper() else f"I'd be happy to {response}"

        # Apply conscientiousness
        conscientiousness_level = user_profile.get('conscientiousness', self.personality_traits['conscientiousness'])
        if conscientiousness_level > 0.7:
            # Add careful language
            careful_expressions = self.personality_expressions['conscientiousness']['high']
            if random.random() < 0.2:  # 20% chance to add careful language
                modifier = random.choice(careful_expressions)
                modified_response = modified_response.replace('I\'ll', modifier) if 'I\'ll' in modified_response else f"{modifier} {modified_response}"

        return modified_response

    def adapt_to_user(self, user_profile):
        """
        Adapt personality to match user's communication style.
        """
        # Adjust robot's personality based on user's observed traits
        for trait in ['extraversion', 'agreeableness', 'conscientiousness', 'emotional_stability', 'openness']:
            if trait in user_profile:
                user_trait_value = user_profile[trait]
                robot_trait_value = self.personality_traits[trait]

                # Move robot's trait closer to user's trait (but don't fully match)
                adjustment = (user_trait_value - robot_trait_value) * 0.2  # 20% adaptation
                self.personality_traits[trait] = max(0.1, min(0.9, robot_trait_value + adjustment))

    def get_personality_response(self, base_response, user_profile):
        """
        Generate response with appropriate personality adaptation.
        """
        # Adapt personality to user
        self.adapt_to_user(user_profile)

        # Apply personality to base response
        personalized_response = self.apply_personality(base_response, user_profile)

        return personalized_response
```

## Integration with Robot Systems

### ROS 2 Integration

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image, LaserScan, Imu
from geometry_msgs.msg import Twist
from dialog_msgs.msg import DialogState as DialogStateMsg
from std_srvs.srv import Trigger
import threading
import queue

class IsaacDialogueNode(Node):
    def __init__(self):
        super().__init__('isaac_dialogue_node')

        # Initialize dialogue system components
        self.dialogue_manager = DialogueManager()
        self.context_tracker = ContextTracker()
        self.belief_tracker = BeliefStateTracker()
        self.nlg_system = ContextAwareNLG()

        # Publishers
        self.speech_pub = self.create_publisher(String, '/robot/speech_output', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.dialog_state_pub = self.create_publisher(DialogStateMsg, '/dialog/state', 10)

        # Subscribers
        self.speech_sub = self.create_subscription(
            String,
            '/robot/speech_input',
            self.speech_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10
        )

        self.camera_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )

        # Services
        self.reset_dialogue_srv = self.create_service(
            Trigger,
            '/dialog/reset',
            self.reset_dialogue_callback
        )

        # Timer for periodic processing
        self.dialog_timer = self.create_timer(0.1, self.dialog_step)

        # Queues for thread-safe processing
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # Robot state
        self.robot_state = {
            'position': [0, 0, 0],
            'orientation': [0, 0, 0, 1],
            'battery_level': 1.0,
            'current_task': 'idle',
            'task_progress': 0.0
        }

        # Sensor data storage
        self.imu_data = None
        self.laser_data = None
        self.camera_data = None

        self.get_logger().info('Isaac Dialogue Node initialized')

    def speech_callback(self, msg):
        """Handle incoming speech input."""
        try:
            user_input = msg.data
            self.get_logger().info(f'Received speech: {user_input}')

            # Process through dialogue system
            response = self.process_dialogue_input(user_input)

            # Publish response
            response_msg = String()
            response_msg.data = response
            self.speech_pub.publish(response_msg)

            self.get_logger().info(f'Response: {response}')

        except Exception as e:
            self.get_logger().error(f'Error processing speech: {e}')
            error_response = "I encountered an error processing your input. Could you repeat that?"
            error_msg = String()
            error_msg.data = error_response
            self.speech_pub.publish(error_msg)

    def process_dialogue_input(self, user_input):
        """
        Process user input through the complete dialogue system.
        """
        # Get current context including sensor data
        current_context = self.get_current_context()

        # Update belief state with new observation
        observation = {
            'intent': 'unknown',  # This would come from NLU
            'entities': {},      # This would come from NLU
            'slots': {}          # This would come from NLU
        }

        # In a real implementation, this would call NLU system
        # For this example, we'll use simple keyword-based classification
        simple_nlu_result = self.simple_nlu_classification(user_input)
        observation.update(simple_nlu_result)

        # Update belief state
        self.belief_tracker.update_belief_state(observation)

        # Process through dialogue manager
        response = self.dialogue_manager.process_user_input(
            user_input,
            user_id='default_user'  # Would come from speaker recognition
        )

        # Generate final response using NLG
        final_response = self.nlg_system.generate_response(
            intent=self.dialogue_manager.current_context.current_intent,
            entities=self.dialogue_manager.current_context.entities,
            context=current_context,
            confidence=0.8  # Would come from NLU confidence
        )

        # Update context tracker
        self.context_tracker.update_context(
            input_data={'text': user_input, 'user_id': 'default_user'},
            sensor_data=self.get_sensor_data(),
            environment_state=self.get_environment_state()
        )

        # Publish dialogue state
        self.publish_dialog_state()

        return final_response

    def simple_nlu_classification(self, text):
        """
        Simple NLU classification for demonstration.
        """
        text_lower = text.lower()

        # Intent classification
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            intent = 'greeting'
        elif any(word in text_lower for word in ['go to', 'move to', 'navigate to', 'walk to']):
            intent = 'navigation'
        elif any(word in text_lower for word in ['pick up', 'grasp', 'take', 'grab']):
            intent = 'manipulation'
        elif any(word in text_lower for word in ['what', 'how', 'when', 'where', 'who', 'why']):
            intent = 'information_request'
        elif any(word in text_lower for word in ['yes', 'yeah', 'sure', 'ok', 'okay']):
            intent = 'confirmation'
        elif any(word in text_lower for word in ['no', 'nope', 'cancel', 'stop']):
            intent = 'negation'
        elif any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            intent = 'goodbye'
        else:
            intent = 'unknown'

        # Entity extraction (simplified)
        entities = {}
        if intent == 'navigation':
            # Extract location entity
            for word in text.split():
                if word in ['kitchen', 'office', 'bedroom', 'living room', 'bathroom', 'hallway']:
                    entities['location'] = word
                    break
        elif intent == 'manipulation':
            # Extract object entity
            for word in text.split():
                if word in ['cup', 'bottle', 'book', 'ball', 'box', 'pen']:
                    entities['object'] = word
                    break

        return {
            'intent': intent,
            'entities': entities,
            'confidence': 0.8 if intent != 'unknown' else 0.3
        }

    def imu_callback(self, msg):
        """Handle IMU data for balance and orientation."""
        self.imu_data = msg

        # Update robot state with orientation information
        self.robot_state['orientation'] = [
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ]

    def laser_callback(self, msg):
        """Handle laser scan data for obstacle detection."""
        self.laser_data = msg

        # Process for obstacle detection
        if self.detect_obstacles(msg):
            # Update context with obstacle information
            self.context_tracker.update_context(
                input_data={'obstacle_detected': True},
                sensor_data={'obstacle_distance': self.get_closest_obstacle_distance(msg)},
                environment_state={}
            )

    def camera_callback(self, msg):
        """Handle camera data for visual perception."""
        self.camera_data = msg

        # Process for face detection, gesture recognition, etc.
        # This would typically use Isaac's vision modules
        pass

    def dialog_step(self):
        """Periodic dialogue processing step."""
        try:
            # Update context with current sensor data
            current_context = self.get_current_context()
            self.context_tracker.update_context(
                input_data={},
                sensor_data=self.get_sensor_data(),
                environment_state=self.get_environment_state()
            )

            # Check for timeout conditions
            time_since_last_interaction = time.time() - self.dialogue_manager.current_context.last_interaction_time if self.dialogue_manager.current_context else float('inf')

            if time_since_last_interaction > 30.0:  # 30 second timeout
                # Trigger timeout response
                timeout_response = self.handle_timeout()
                if timeout_response:
                    timeout_msg = String()
                    timeout_msg.data = timeout_response
                    self.speech_pub.publish(timeout_msg)

            # Publish current dialogue state
            self.publish_dialog_state()

        except Exception as e:
            self.get_logger().error(f'Error in dialog step: {e}')

    def get_current_context(self):
        """
        Get current context including sensor data and environment state.
        """
        context = {
            'time_of_day': self.get_time_of_day(),
            'robot_state': self.robot_state,
            'sensor_data': self.get_sensor_data(),
            'environment_state': self.get_environment_state(),
            'dialogue_state': self.dialogue_manager.current_context.current_state.value if self.dialogue_manager.current_context else 'idle'
        }

        return context

    def get_sensor_data(self):
        """Get current sensor data."""
        sensor_data = {}

        if self.imu_data:
            sensor_data['imu'] = {
                'linear_acceleration': [self.imu_data.linear_acceleration.x,
                                      self.imu_data.linear_acceleration.y,
                                      self.imu_data.linear_acceleration.z],
                'angular_velocity': [self.imu_data.angular_velocity.x,
                                   self.imu_data.angular_velocity.y,
                                   self.imu_data.angular_velocity.z],
                'orientation': [self.imu_data.orientation.x,
                              self.imu_data.orientation.y,
                              self.imu_data.orientation.z,
                              self.imu_data.orientation.w]
            }

        if self.laser_data:
            sensor_data['laser'] = {
                'ranges': list(self.laser_data.ranges),
                'intensities': list(self.laser_data.intensities),
                'angle_min': self.laser_data.angle_min,
                'angle_max': self.laser_data.angle_max,
                'angle_increment': self.laser_data.angle_increment
            }

        return sensor_data

    def get_environment_state(self):
        """Get current environment state."""
        env_state = {
            'robot_pose': self.robot_state['position'] + self.robot_state['orientation'],
            'battery_level': self.robot_state['battery_level'],
            'current_task': self.robot_state['current_task'],
            'task_progress': self.robot_state['task_progress'],
            'obstacle_detected': self.detect_obstacles(self.laser_data) if self.laser_data else False
        }

        return env_state

    def detect_obstacles(self, laser_scan):
        """Detect obstacles in laser scan data."""
        if not laser_scan:
            return False

        # Check for obstacles within 1 meter
        min_distance = min(laser_scan.ranges) if laser_scan.ranges else float('inf')
        return min_distance < 1.0

    def get_closest_obstacle_distance(self, laser_scan):
        """Get distance to closest obstacle."""
        if not laser_scan or not laser_scan.ranges:
            return float('inf')

        return min(laser_scan.ranges)

    def handle_timeout(self):
        """Handle conversation timeout."""
        if self.dialogue_manager.current_context:
            self.dialogue_manager.current_context.current_state = DialogueState.IDLE
            return "I haven't heard from you in a while. I'll be here when you need me."
        return None

    def publish_dialog_state(self):
        """Publish current dialogue state."""
        if self.dialogue_manager.current_context:
            state_msg = DialogStateMsg()
            state_msg.state = self.dialogue_manager.current_context.current_state.value
            state_msg.user_id = self.dialogue_manager.current_context.user_id
            state_msg.confidence = self.dialogue_manager.current_context.confidence_threshold
            state_msg.timestamp = self.get_clock().now().to_msg()

            self.dialog_state_pub.publish(state_msg)

    def reset_dialogue_callback(self, request, response):
        """Reset dialogue system."""
        self.dialogue_manager.current_context = None
        self.context_tracker = ContextTracker()
        self.belief_tracker = BeliefStateTracker()

        response.success = True
        response.message = "Dialogue system reset"

        self.get_logger().info('Dialogue system reset')
        return response

def main(args=None):
    rclpy.init(args=args)
    dialogue_node = IsaacDialogueNode()

    try:
        rclpy.spin(dialogue_node)
    except KeyboardInterrupt:
        dialogue_node.get_logger().info('Shutting down dialogue node...')
    finally:
        dialogue_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

Dialogue systems for humanoid robots require sophisticated integration of multiple AI components to enable natural, context-aware interaction. The key components include:

1. **State Management**: Tracking conversation state and context
2. **Belief Tracking**: Maintaining uncertainty-aware state estimates
3. **Policy Management**: Selecting appropriate responses based on context
4. **Context Integration**: Incorporating spatial, temporal, and social context
5. **Natural Language Generation**: Creating appropriate, personalized responses
6. **Multimodal Integration**: Combining speech, vision, and sensor data

These systems enable humanoid robots to engage in natural conversations while maintaining awareness of their environment and adapting to human social cues, making them more effective and acceptable in human environments.