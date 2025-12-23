---
sidebar_label: 'Natural Language Processing for Humanoid Robots'
title: 'Natural Language Processing for Humanoid Robots'
---

# Natural Language Processing for Humanoid Robots

## Introduction to NLP in Robotics

Natural Language Processing (NLP) in humanoid robotics enables robots to understand and generate human language for natural interaction. Unlike traditional chatbots, robotic NLP must handle real-world contexts, multimodal inputs, and dynamic environments where language is grounded in physical reality.

## NLP Pipeline for Humanoid Robots

### Overview of the NLP Pipeline

The NLP pipeline for humanoid robots typically includes:

```
Speech Input
├── Automatic Speech Recognition (ASR)
├── Natural Language Understanding (NLU)
├── Context Integration
├── Intent Classification
├── Entity Extraction
├── Dialogue Management
├── Natural Language Generation (NLG)
└── Text-to-Speech (TTS)
```

Each component must operate efficiently in real-time while handling the uncertainties of real-world environments.

## Automatic Speech Recognition (ASR)

### ASR for Robotics Applications

```python
import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import librosa
import numpy as np

class RoboticsASR:
    def __init__(self, model_name="openai/whisper-large-v3"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load pre-trained ASR model
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Initialize audio preprocessing
        self.sample_rate = 16000
        self.chunk_size = 1024  # samples per chunk

        # Voice activity detection parameters
        self.energy_threshold = 50
        self.silence_duration = 0.5  # seconds of silence to end recognition

    def preprocess_audio(self, audio_data, sample_rate):
        """
        Preprocess audio for ASR system.

        Args:
            audio_data: Raw audio signal
            sample_rate: Original sample rate of audio

        Returns:
            processed_audio: Preprocessed audio tensor
        """
        # Resample to required rate
        if sample_rate != self.sample_rate:
            audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=self.sample_rate)

        # Normalize audio
        audio_data = audio_data.astype(np.float32)
        audio_data = audio_data / np.max(np.abs(audio_data))  # Normalize to [-1, 1]

        # Apply noise reduction (simplified)
        # In practice, use more sophisticated noise reduction
        noise_floor = np.percentile(np.abs(audio_data), 10)
        audio_data = np.where(np.abs(audio_data) < noise_floor, 0, audio_data)

        return audio_data

    def recognize_speech(self, audio_data, return_timestamps=False):
        """
        Recognize speech from audio data.

        Args:
            audio_data: Audio signal as numpy array
            return_timestamps: Whether to return word timestamps

        Returns:
            recognition_result: Dictionary with text and confidence
        """
        # Preprocess audio
        processed_audio = self.preprocess_audio(audio_data, self.sample_rate)

        # Process with Whisper model
        inputs = self.processor(
            processed_audio,
            sampling_rate=self.sample_rate,
            return_tensors="pt"
        ).to(self.device)

        # Generate transcription
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs["input_features"],
                language="en",
                return_timestamps=return_timestamps
            )

        # Decode transcription
        transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Calculate confidence (simplified - based on model outputs)
        confidence = self.estimate_confidence(generated_ids)

        return {
            'text': transcription,
            'confidence': confidence,
            'timestamp': time.time()
        }

    def estimate_confidence(self, generated_ids):
        """
        Estimate confidence of ASR result.
        This is a simplified approach - real implementation would use model probabilities.
        """
        # In practice, use the model's probability outputs
        # For this example, return a placeholder confidence score
        return 0.85  # High confidence for demonstration

    def streaming_recognition(self, audio_stream_callback, chunk_duration=0.5):
        """
        Perform streaming speech recognition.

        Args:
            audio_stream_callback: Function to provide audio chunks
            chunk_duration: Duration of each audio chunk in seconds
        """
        chunk_size = int(self.sample_rate * chunk_duration)
        audio_buffer = np.array([])
        speech_detected = False
        silence_count = 0

        while True:
            # Get audio chunk
            chunk = audio_stream_callback(chunk_size)

            if chunk is None:
                break

            # Check for speech activity
            energy = np.mean(np.abs(chunk))

            if energy > self.energy_threshold:
                # Speech detected, add to buffer
                audio_buffer = np.concatenate([audio_buffer, chunk])
                speech_detected = True
                silence_count = 0
            elif speech_detected:
                # Silence detected after speech
                silence_count += 1

                if silence_count * chunk_duration > self.silence_duration:
                    # End of speech detected
                    if len(audio_buffer) > 0:
                        result = self.recognize_speech(audio_buffer)
                        yield result

                        # Reset for next utterance
                        audio_buffer = np.array([])
                        speech_detected = False
                        silence_count = 0
```

### Robust ASR for Noisy Environments

```python
import webrtcvad
import collections

class RobustASR:
    def __init__(self):
        # Initialize Voice Activity Detection
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(2)  # Aggressive VAD mode

        # Audio parameters
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

        # Buffer for audio chunks
        self.audio_buffer = collections.deque(maxlen=30)  # 30 chunks = 0.9 seconds

        # Noise suppression parameters
        self.noise_suppression_level = 2  # 0-3, higher = more suppression
        self.echo_cancellation = True

    def voice_activity_detection(self, audio_frame):
        """
        Detect voice activity in audio frame.
        """
        # Convert to bytes for WebRTC VAD
        audio_bytes = (audio_frame * 32767).astype(np.int16).tobytes()

        # Check for voice activity
        is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)

        return is_speech

    def noise_reduction(self, audio_data):
        """
        Apply noise reduction to audio data.
        This is a simplified implementation - real systems use advanced algorithms.
        """
        # Spectral subtraction approach
        # Convert to frequency domain
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data)
        phase = np.angle(fft_data)

        # Estimate noise spectrum (simplified - assumes first part is noise)
        noise_length = min(len(audio_data) // 4, 1000)  # First 25% or 1000 samples
        noise_spectrum = np.abs(np.fft.fft(audio_data[:noise_length]))

        # Apply spectral subtraction
        enhanced_magnitude = np.maximum(magnitude - noise_spectrum * 0.5, 0)

        # Reconstruct signal
        enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = np.real(np.fft.ifft(enhanced_fft))

        return enhanced_audio.astype(np.float32)

    def multi_channel_asr(self, audio_channels):
        """
        Process multi-channel audio for improved ASR performance.

        Args:
            audio_channels: List of audio signals from different microphones

        Returns:
            best_transcription: Most confident transcription
        """
        transcriptions = []

        for channel_idx, audio_data in enumerate(audio_channels):
            # Apply beamforming to enhance speech from robot's direction
            enhanced_audio = self.apply_beamforming(audio_data, channel_idx)

            # Perform ASR on enhanced audio
            result = self.recognize_speech(enhanced_audio)
            result['channel'] = channel_idx
            transcriptions.append(result)

        # Select best transcription based on confidence
        best_result = max(transcriptions, key=lambda x: x['confidence'])
        return best_result

    def apply_beamforming(self, audio_data, channel_idx):
        """
        Apply simple beamforming to enhance speech from desired direction.
        """
        # This would implement actual beamforming algorithms
        # For this example, return the original audio with slight enhancements
        return audio_data
```

## Natural Language Understanding (NLU)

### Intent Classification

```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import numpy as np
import json

class IntentClassifier:
    def __init__(self, model_path=None):
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = AutoModel.from_pretrained("bert-base-uncased")

        # Intent classification head
        self.classifier = nn.Sequential(
            nn.Linear(768, 256),  # BERT hidden size to intermediate
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, self.num_intents)  # num_intents to be defined
        )

        # Define intent categories for robotics
        self.intents = {
            0: 'greeting',
            1: 'navigation',
            2: 'manipulation',
            3: 'information_request',
            4: 'confirmation',
            5: 'correction',
            6: 'goodbye',
            7: 'help_request',
            8: 'status_inquiry',
            9: 'emergency_stop'
        }
        self.num_intents = len(self.intents)

        # Load trained model if available
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def encode_text(self, text):
        """
        Encode text using BERT model.
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            # Use [CLS] token representation
            encoded = outputs.last_hidden_state[:, 0, :]

        return encoded

    def classify_intent(self, text, context=None):
        """
        Classify intent of input text.

        Args:
            text: Input text to classify
            context: Additional context information

        Returns:
            intent: Predicted intent
            confidence: Confidence score
        """
        # Encode text
        encoded_text = self.encode_text(text)

        # Pass through classifier
        logits = self.classifier(encoded_text)
        probabilities = torch.softmax(logits, dim=-1)

        # Get predicted intent and confidence
        predicted_idx = torch.argmax(probabilities, dim=-1).item()
        confidence = torch.max(probabilities, dim=-1).values.item()

        intent = self.intents[predicted_idx]

        return intent, confidence

    def train_classifier(self, training_data):
        """
        Train the intent classifier.

        Args:
            training_data: List of (text, intent_label) tuples
        """
        # Prepare training data
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]

        # Vectorize texts
        vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X = vectorizer.fit_transform(texts)

        # Train SVM classifier
        self.svm_classifier = SVC(kernel='linear', probability=True)
        self.svm_classifier.fit(X, labels)

        # Store vectorizer
        self.vectorizer = vectorizer

    def predict_intent_svm(self, text):
        """
        Predict intent using trained SVM model.
        """
        X = self.vectorizer.transform([text])
        intent = self.svm_classifier.predict(X)[0]
        confidence = np.max(self.svm_classifier.predict_proba(X))

        return intent, confidence

    def get_robot_specific_intents(self):
        """
        Get intent patterns specific to robotics applications.
        """
        return {
            'greeting': [
                'hello', 'hi', 'hey', 'greetings', 'good morning',
                'good afternoon', 'good evening', 'nice to meet you'
            ],
            'navigation': [
                'go to', 'move to', 'walk to', 'navigate to', 'go forward',
                'go backward', 'turn left', 'turn right', 'rotate',
                'drive to', 'reach', 'arrive at'
            ],
            'manipulation': [
                'pick up', 'grasp', 'grab', 'take', 'hold', 'release',
                'drop', 'place', 'put', 'move', 'manipulate', 'lift'
            ],
            'information_request': [
                'what', 'how', 'when', 'where', 'who', 'why',
                'tell me', 'explain', 'describe', 'what is',
                'can you tell me', 'what can you do'
            ],
            'confirmation': [
                'yes', 'no', 'correct', 'wrong', 'right', 'ok',
                'okay', 'sure', 'that is correct', 'not correct'
            ],
            'correction': [
                'no not', 'wrong', 'incorrect', 'cancel', 'stop',
                'never mind', 'that is not', 'i meant'
            ],
            'goodbye': [
                'goodbye', 'bye', 'see you', 'farewell', 'thanks',
                'thank you', 'good night', 'have a good day'
            ],
            'help_request': [
                'help', 'assist', 'can you help', 'need help',
                'what can i do', 'how do i', 'help me'
            ],
            'status_inquiry': [
                'how are you', 'are you working', 'what is your status',
                'what are you doing', 'are you ready', 'system status'
            ],
            'emergency_stop': [
                'emergency', 'stop', 'emergency stop', 'halt',
                'emergency halt', 'safety stop'
            ]
        }

class EntityExtractor:
    def __init__(self):
        # Load spaCy model for named entity recognition
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
            print("spaCy model not available. Using rule-based extraction.")

        # Define entity patterns for robotics
        self.entity_patterns = {
            'location': [
                r'\b(room|area|zone|space|hall|kitchen|living room|bedroom|office|lab)\b',
                r'\b(north|south|east|west)\b',
                r'\b(front|back|left|right)\b'
            ],
            'object': [
                r'\b(ball|cup|book|bottle|pen|box|table|chair|door|window)\b',
                r'\b(red|blue|green|yellow|white|black|large|small|heavy|light)\b'
            ],
            'person': [
                r'\b(person|someone|me|you|him|her|them)\b'
            ],
            'time': [
                r'\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b',
                r'\b(today|tomorrow|yesterday|now|later|morning|afternoon|evening|night)\b'
            ],
            'number': [
                r'\b(\d+(?:\.\d+)?)\b'
            ]
        }

        # Compiled regex patterns
        self.compiled_patterns = {}
        for entity_type, patterns in self.entity_patterns.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
            self.compiled_patterns[entity_type] = compiled

    def extract_entities(self, text):
        """
        Extract entities from text using multiple approaches.

        Args:
            text: Input text to extract entities from

        Returns:
            entities: List of extracted entities with type and confidence
        """
        entities = []

        if self.nlp:
            # Use spaCy for entity extraction
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'type': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.8  # Default confidence for spaCy
                })

        # Use rule-based extraction for robotics-specific entities
        rule_entities = self.extract_rule_based_entities(text)
        entities.extend(rule_entities)

        # Remove duplicates and merge overlapping entities
        entities = self.merge_entities(entities)

        return entities

    def extract_rule_based_entities(self, text):
        """
        Extract entities using rule-based patterns.
        """
        entities = []
        text_lower = text.lower()

        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text_lower)
                for match in matches:
                    entities.append({
                        'text': text[match.start():match.end()],
                        'type': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.7  # Rule-based confidence
                    })

        return entities

    def merge_entities(self, entities):
        """
        Merge overlapping entities and remove duplicates.
        """
        if not entities:
            return []

        # Sort by start position
        entities.sort(key=lambda x: x['start'])

        merged = [entities[0]]

        for current in entities[1:]:
            previous = merged[-1]

            # Check if entities overlap or are adjacent
            if current['start'] <= previous['end']:
                # Merge overlapping entities
                if current['type'] == previous['type']:
                    # Same type - extend the previous entity
                    previous['end'] = max(previous['end'], current['end'])
                    previous['text'] = previous['text'] + ' ' + current['text']
                    previous['confidence'] = max(previous['confidence'], current['confidence'])
                else:
                    # Different types - keep both
                    merged.append(current)
            else:
                # No overlap - add as new entity
                merged.append(current)

        return merged

    def extract_quantities(self, text):
        """
        Extract quantitative information from text.
        """
        import re

        quantity_entities = []

        # Distance units
        distance_pattern = r'(\d+(?:\.\d+)?)\s*(meters?|m|cm|mm|feet|ft|inches?|in)'
        distances = re.findall(distance_pattern, text, re.IGNORECASE)
        for distance, unit in distances:
            quantity_entities.append({
                'type': 'distance',
                'value': float(distance),
                'unit': unit,
                'text': f"{distance} {unit}"
            })

        # Time units
        time_pattern = r'(\d+(?:\.\d+)?)\s*(seconds?|second|secs?|minutes?|mins?|hours?|hrs?)'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        for time_val, unit in times:
            quantity_entities.append({
                'type': 'time',
                'value': float(time_val),
                'unit': unit,
                'text': f"{time_val} {unit}"
            })

        return quantity_entities

class ContextualNLU:
    """
    NLU system that incorporates context for better understanding.
    """
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.context_history = []
        self.max_context_length = 10

    def process_with_context(self, text, conversation_context=None):
        """
        Process text with conversation context.

        Args:
            text: Input text to process
            conversation_context: Previous conversation history

        Returns:
            nlu_result: Complete NLU result with context
        """
        # Extract intent
        intent, intent_confidence = self.intent_classifier.classify_intent(text)

        # Extract entities
        entities = self.entity_extractor.extract_entities(text)

        # Incorporate context for disambiguation
        if conversation_context:
            entities = self.disambiguate_entities(entities, conversation_context)

        # Calculate overall confidence based on intent and entity confidence
        overall_confidence = self.calculate_overall_confidence(
            intent_confidence, entities
        )

        # Update context history
        self.context_history.append({
            'text': text,
            'intent': intent,
            'entities': entities,
            'confidence': overall_confidence,
            'timestamp': time.time()
        })

        # Maintain context history size
        if len(self.context_history) > self.max_context_length:
            self.context_history.pop(0)

        return {
            'text': text,
            'intent': intent,
            'entities': entities,
            'confidence': overall_confidence,
            'context': self.context_history[-3:]  # Last 3 exchanges
        }

    def disambiguate_entities(self, entities, conversation_context):
        """
        Disambiguate entities using conversation context.
        """
        # Example: Resolve pronouns using context
        for entity in entities:
            if entity['type'] == 'pronoun':
                # Resolve pronoun to actual entity from context
                resolved_entity = self.resolve_pronoun(entity, conversation_context)
                if resolved_entity:
                    entity.update(resolved_entity)

        # Example: Resolve spatial references
        for entity in entities:
            if entity['type'] in ['location', 'object'] and entity['text'] in ['it', 'there', 'here']:
                # Resolve to actual location/object from context
                resolved = self.resolve_spatial_reference(entity, conversation_context)
                if resolved:
                    entity.update(resolved)

        return entities

    def resolve_pronoun(self, pronoun_entity, context):
        """
        Resolve pronoun to antecedent in context.
        """
        # Look for potential antecedents in recent context
        for ctx_item in reversed(context[-5:]):  # Look back 5 exchanges
            for entity in ctx_item.get('entities', []):
                if entity['type'] in ['person', 'object', 'location']:
                    # Simple resolution based on proximity and relevance
                    return {
                        'resolved_to': entity['text'],
                        'type': entity['type']
                    }

        return None

    def resolve_spatial_reference(self, spatial_entity, context):
        """
        Resolve spatial references like 'there', 'here' to actual locations.
        """
        # Look for spatial context in recent exchanges
        for ctx_item in reversed(context[-3:]):  # Look back 3 exchanges
            if 'spatial_context' in ctx_item:
                return {
                    'resolved_to': ctx_item['spatial_context'],
                    'type': 'location'
                }

        return None

    def calculate_overall_confidence(self, intent_confidence, entities):
        """
        Calculate overall confidence considering intent and entities.
        """
        if not entities:
            return intent_confidence

        # Calculate entity confidence (average of entity confidences)
        entity_confidences = [e.get('confidence', 0.5) for e in entities]
        avg_entity_confidence = sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0.5

        # Weighted combination
        intent_weight = 0.7
        entity_weight = 0.3

        overall_confidence = (intent_weight * intent_confidence +
                             entity_weight * avg_entity_confidence)

        return overall_confidence
```

## Dialogue Management

### State-Based Dialogue Manager

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import time

class DialogState(Enum):
    IDLE = "idle"
    GREETING = "greeting"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    CONFIRMING = "confirming"
    CORRECTING = "correcting"
    NAVIGATING = "navigating"
    MANIPULATING = "manipulating"
    HELPING = "helping"
    EMERGENCY = "emergency"

@dataclass
class DialogContext:
    state: DialogState
    user_id: str
    conversation_id: str
    intent: str
    entities: List[Dict]
    confidence: float
    context_variables: Dict[str, Any]
    conversation_history: List[Dict]
    last_interaction_time: float
    user_profile: Dict[str, Any]

class StateBasedDialogManager:
    def __init__(self):
        self.current_context = None
        self.dialog_states = self.define_dialog_states()
        self.state_transitions = self.define_state_transitions()
        self.response_templates = self.define_response_templates()

    def define_dialog_states(self):
        """
        Define properties and behaviors for each dialog state.
        """
        return {
            DialogState.IDLE: {
                'entry_actions': [self.enter_idle_state],
                'exit_actions': [self.exit_idle_state],
                'handlers': {
                    'speech_input': self.handle_idle_speech,
                    'motion_input': self.handle_idle_motion
                },
                'timeout': 30.0,  # Go to idle after 30 seconds of inactivity
                'priority': 1
            },
            DialogState.GREETING: {
                'entry_actions': [self.enter_greeting_state],
                'exit_actions': [self.exit_greeting_state],
                'handlers': {
                    'user_response': self.handle_greeting_response
                },
                'timeout': 10.0,  # Move to listening after greeting
                'priority': 2
            },
            DialogState.LISTENING: {
                'entry_actions': [self.enter_listening_state],
                'exit_actions': [self.exit_listening_state],
                'handlers': {
                    'speech_input': self.handle_speech_input,
                    'gesture_input': self.handle_gesture_input
                },
                'timeout': 5.0,  # Timeout if no input
                'priority': 3
            },
            DialogState.PROCESSING: {
                'entry_actions': [self.enter_processing_state],
                'exit_actions': [self.exit_processing_state],
                'handlers': {
                    'processing_complete': self.handle_processing_complete
                },
                'timeout': 15.0,  # Processing shouldn't take too long
                'priority': 4
            },
            DialogState.RESPONDING: {
                'entry_actions': [self.enter_responding_state],
                'exit_actions': [self.exit_responding_state],
                'handlers': {
                    'response_delivered': self.handle_response_delivered
                },
                'timeout': 10.0,  # Response should be delivered quickly
                'priority': 5
            },
            DialogState.CONFIRMING: {
                'entry_actions': [self.enter_confirming_state],
                'exit_actions': [self.exit_confirming_state],
                'handlers': {
                    'user_confirmation': self.handle_user_confirmation,
                    'user_denial': self.handle_user_denial
                },
                'timeout': 10.0,  # Wait for user response
                'priority': 6
            },
            DialogState.NAVIGATING: {
                'entry_actions': [self.enter_navigating_state],
                'exit_actions': [self.exit_navigating_state],
                'handlers': {
                    'navigation_complete': self.handle_navigation_complete,
                    'obstacle_detected': self.handle_obstacle_detected
                },
                'timeout': 120.0,  # Navigation timeout
                'priority': 7
            },
            DialogState.MANIPULATING: {
                'entry_actions': [self.enter_manipulating_state],
                'exit_actions': [self.exit_manipulating_state],
                'handlers': {
                    'manipulation_complete': self.handle_manipulation_complete,
                    'manipulation_failed': self.handle_manipulation_failed
                },
                'timeout': 60.0,  # Manipulation timeout
                'priority': 8
            }
        }

    def define_state_transitions(self):
        """
        Define legal transitions between states.
        """
        return {
            DialogState.IDLE: [DialogState.GREETING, DialogState.LISTENING],
            DialogState.GREETING: [DialogState.LISTENING, DialogState.EMERGENCY],
            DialogState.LISTENING: [DialogState.PROCESSING, DialogState.EMERGENCY],
            DialogState.PROCESSING: [DialogState.RESPONDING, DialogState.CONFIRMING,
                                   DialogState.NAVIGATING, DialogState.MANIPULATING,
                                   DialogState.EMERGENCY],
            DialogState.RESPONDING: [DialogState.LISTENING, DialogState.EMERGENCY],
            DialogState.CONFIRMING: [DialogState.PROCESSING, DialogState.LISTENING,
                                   DialogState.EMERGENCY],
            DialogState.NAVIGATING: [DialogState.LISTENING, DialogState.EMERGENCY],
            DialogState.MANIPULATING: [DialogState.LISTENING, DialogState.EMERGENCY],
            DialogState.EMERGENCY: [DialogState.IDLE]
        }

    def define_response_templates(self):
        """
        Define response templates for different intents and contexts.
        """
        return {
            'greeting': [
                "Hello! I'm your humanoid assistant. How can I help you today?",
                "Hi there! It's nice to meet you. What would you like to do?",
                "Greetings! I'm ready to assist you. How can I be of service?"
            ],
            'navigation': [
                "I'll navigate to {location}. Please follow me.",
                "Heading to {location}. I'll lead the way.",
                "Going to {location}. Please keep a safe distance."
            ],
            'manipulation': [
                "I'll pick up the {object}. Please make sure the area is clear.",
                "Attempting to grasp the {object}. Is this correct?",
                "Reaching for the {object}. Please stand back."
            ],
            'information': [
                "Regarding {topic}: {response}",
                "I can tell you about {topic}: {response}",
                "About {topic}, here's what I know: {response}"
            ],
            'confirmation': [
                "Got it. I'll proceed with that.",
                "Understood. I'll do as requested.",
                "Confirmed. Executing now."
            ],
            'error': [
                "I'm sorry, I didn't understand that. Could you repeat it?",
                "I'm having trouble with that request. Could you rephrase?",
                "I didn't catch that clearly. Could you speak more distinctly?"
            ]
        }

    def process_input(self, input_text, input_type='speech', user_id='unknown'):
        """
        Process input and update dialog state.

        Args:
            input_text: Text input to process
            input_type: Type of input ('speech', 'gesture', 'command')
            user_id: Identifier for the user

        Returns:
            response: Generated response text
        """
        # Initialize context if needed
        if self.current_context is None or self.current_context.user_id != user_id:
            self.initialize_context(user_id)

        # Update last interaction time
        self.current_context.last_interaction_time = time.time()

        # Process input based on current state
        current_state = self.current_context.state
        state_handlers = self.dialog_states[current_state]['handlers']

        if input_type in state_handlers:
            handler = state_handlers[input_type]
            result = handler(input_text)
        else:
            # Default handler for unhandled input types
            result = self.default_handler(input_text, input_type)

        # Update context with new information
        self.current_context.conversation_history.append({
            'timestamp': time.time(),
            'speaker': 'user',
            'text': input_text,
            'intent': result.get('intent', 'unknown'),
            'entities': result.get('entities', []),
            'input_type': input_type
        })

        return result.get('response', 'I received your input.')

    def initialize_context(self, user_id):
        """
        Initialize conversation context for a new user.
        """
        self.current_context = DialogContext(
            state=DialogState.IDLE,
            user_id=user_id,
            conversation_id=f"conv_{int(time.time())}_{user_id}",
            intent='unknown',
            entities=[],
            confidence=0.0,
            context_variables={},
            conversation_history=[],
            last_interaction_time=time.time(),
            user_profile=self.get_user_profile(user_id)
        )

    def get_user_profile(self, user_id):
        """
        Get user profile information (simplified - would use database in practice).
        """
        # This would typically load from a user database
        # For this example, return default profile
        return {
            'name': 'User',
            'preferences': {},
            'interaction_history': [],
            'familiarity': 0.5  # 0.0 = new user, 1.0 = very familiar
        }

    def handle_idle_speech(self, input_text):
        """
        Handle speech input when in IDLE state.
        """
        # Transition to greeting if greeting detected
        if self.contains_greeting(input_text):
            self.transition_to_state(DialogState.GREETING)
            return self.generate_greeting_response()
        else:
            # Direct transition to listening
            self.transition_to_state(DialogState.LISTENING)
            return self.process_input_in_listening_state(input_text)

    def handle_speech_input(self, input_text):
        """
        Handle speech input in LISTENING state.
        """
        # Update state to processing
        self.transition_to_state(DialogState.PROCESSING)

        # Process through NLU
        nlu_result = self.process_nlu(input_text)

        # Store NLU results in context
        self.current_context.intent = nlu_result['intent']
        self.current_context.entities = nlu_result['entities']
        self.current_context.confidence = nlu_result['confidence']

        # Determine next action based on intent
        if nlu_result['confidence'] > 0.7:
            return self.execute_intent_based_action(nlu_result)
        else:
            # Low confidence - ask for clarification
            self.transition_to_state(DialogState.LISTENING)
            return {
                'response': "I'm not sure I understood correctly. Could you please clarify?",
                'intent': 'clarification_request',
                'confidence': 0.0
            }

    def process_nlu(self, text):
        """
        Process text through NLU system.
        """
        # This would call the NLU system created earlier
        # For this example, we'll use a simplified approach
        intent_classifier = IntentClassifier()
        entity_extractor = EntityExtractor()

        intent, confidence = intent_classifier.predict_intent_svm(text)
        entities = entity_extractor.extract_entities(text)

        return {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'text': text
        }

    def execute_intent_based_action(self, nlu_result):
        """
        Execute action based on intent.
        """
        intent = nlu_result['intent']

        if intent == 'greeting':
            return self.handle_greeting_intent(nlu_result)
        elif intent == 'navigation':
            return self.handle_navigation_intent(nlu_result)
        elif intent == 'manipulation':
            return self.handle_manipulation_intent(nlu_result)
        elif intent == 'information_request':
            return self.handle_information_intent(nlu_result)
        elif intent == 'confirmation':
            return self.handle_confirmation_intent(nlu_result)
        elif intent == 'goodbye':
            return self.handle_goodbye_intent(nlu_result)
        elif intent == 'help_request':
            return self.handle_help_intent(nlu_result)
        elif intent == 'emergency_stop':
            return self.handle_emergency_intent(nlu_result)
        else:
            # Unknown intent - transition back to listening
            self.transition_to_state(DialogState.LISTENING)
            return {
                'response': "I'm not sure how to handle that request. Could you be more specific?",
                'intent': 'unknown',
                'confidence': 0.0
            }

    def handle_greeting_intent(self, nlu_result):
        """
        Handle greeting intent.
        """
        self.transition_to_state(DialogState.GREETING)
        response = self.select_template('greeting')
        return {
            'response': response,
            'intent': 'greeting',
            'confidence': nlu_result['confidence']
        }

    def handle_navigation_intent(self, nlu_result):
        """
        Handle navigation intent.
        """
        # Extract location from entities
        location = self.extract_entity_by_type(nlu_result['entities'], 'location')

        if location:
            self.transition_to_state(DialogState.NAVIGATING)
            template = self.select_template('navigation')
            response = template.format(location=location)
        else:
            # Ask for location if not provided
            self.transition_to_state(DialogState.LISTENING)
            response = "Where would you like me to navigate to?"

        return {
            'response': response,
            'intent': 'navigation',
            'confidence': nlu_result['confidence']
        }

    def handle_manipulation_intent(self, nlu_result):
        """
        Handle manipulation intent.
        """
        # Extract object from entities
        obj = self.extract_entity_by_type(nlu_result['entities'], 'object')

        if obj:
            # Confirm action with user
            self.transition_to_state(DialogState.CONFIRMING)
            self.current_context.context_variables['pending_action'] = {
                'type': 'manipulation',
                'object': obj
            }
            template = self.select_template('manipulation')
            response = template.format(object=obj)
        else:
            # Ask for object if not provided
            self.transition_to_state(DialogState.LISTENING)
            response = "What object would you like me to interact with?"

        return {
            'response': response,
            'intent': 'manipulation',
            'confidence': nlu_result['confidence']
        }

    def handle_information_intent(self, nlu_result):
        """
        Handle information request intent.
        """
        # Extract topic from entities or use full text
        entities = nlu_result['entities']
        topic = self.extract_entity_by_type(entities, 'object') or nlu_result['text']

        # Generate information response
        info_response = self.generate_information_response(topic)

        self.transition_to_state(DialogState.RESPONDING)
        template = self.select_template('information')
        response = template.format(topic=topic, response=info_response)

        return {
            'response': response,
            'intent': 'information_request',
            'confidence': nlu_result['confidence']
        }

    def handle_confirmation_intent(self, nlu_result):
        """
        Handle confirmation intent.
        """
        if self.current_context.state == DialogState.CONFIRMING:
            # User confirmed pending action
            pending_action = self.current_context.context_variables.get('pending_action', {})

            if pending_action.get('type') == 'manipulation':
                self.transition_to_state(DialogState.MANIPULATING)
                response = f"Proceeding with manipulation of {pending_action.get('object', 'the object')}."
            elif pending_action.get('type') == 'navigation':
                self.transition_to_state(DialogState.NAVIGATING)
                response = f"Proceeding with navigation to {pending_action.get('location', 'the destination')}."
            else:
                self.transition_to_state(DialogState.RESPONDING)
                response = "Got it. I'll proceed as requested."
        else:
            # General confirmation
            self.transition_to_state(DialogState.RESPONDING)
            response = self.select_template('confirmation')

        return {
            'response': response,
            'intent': 'confirmation',
            'confidence': nlu_result['confidence']
        }

    def handle_goodbye_intent(self, nlu_result):
        """
        Handle goodbye intent.
        """
        self.transition_to_state(DialogState.IDLE)
        response = "Goodbye! It was nice interacting with you."

        return {
            'response': response,
            'intent': 'goodbye',
            'confidence': nlu_result['confidence']
        }

    def handle_help_intent(self, nlu_result):
        """
        Handle help request intent.
        """
        self.transition_to_state(DialogState.RESPONDING)
        response = ("I can help with navigation, object manipulation, "
                   "answering questions, and general assistance. "
                   "What would you like me to do?")

        return {
            'response': response,
            'intent': 'help_request',
            'confidence': nlu_result['confidence']
        }

    def handle_emergency_intent(self, nlu_result):
        """
        Handle emergency stop intent.
        """
        self.transition_to_state(DialogState.EMERGENCY)
        response = "EMERGENCY STOP ACTIVATED. All motion halted for safety."

        # In real implementation, this would trigger safety procedures
        self.trigger_emergency_procedures()

        return {
            'response': response,
            'intent': 'emergency_stop',
            'confidence': nlu_result['confidence']
        }

    def transition_to_state(self, new_state):
        """
        Transition to a new dialog state.
        """
        old_state = self.current_context.state

        # Check if transition is legal
        legal_transitions = self.state_transitions.get(old_state, [])
        if new_state not in legal_transitions:
            print(f"Warning: Illegal state transition from {old_state} to {new_state}")
            return False

        # Execute exit actions for old state
        if old_state in self.dialog_states:
            for action in self.dialog_states[old_state]['exit_actions']:
                action()

        # Update state
        self.current_context.state = new_state

        # Execute entry actions for new state
        if new_state in self.dialog_states:
            for action in self.dialog_states[new_state]['entry_actions']:
                action()

        return True

    def select_template(self, template_type):
        """
        Select an appropriate template for the response.
        """
        import random
        templates = self.response_templates.get(template_type, ["I understand."])
        return random.choice(templates)

    def extract_entity_by_type(self, entities, entity_type):
        """
        Extract entity of specific type from entity list.
        """
        for entity in entities:
            if entity.get('type') == entity_type:
                return entity['text']
        return None

    def generate_information_response(self, topic):
        """
        Generate information response for a given topic.
        """
        # This would typically query a knowledge base
        # For this example, we'll return canned responses
        topic_lower = topic.lower()

        if 'robot' in topic_lower or 'robotics' in topic_lower:
            return ("I am a humanoid robot designed for human-robot interaction. "
                   "I can navigate environments, manipulate objects, and engage "
                   "in natural conversations.")
        elif 'name' in topic_lower:
            return "I am a humanoid robot developed for research and assistance applications."
        elif 'capability' in topic_lower or 'can you' in topic_lower:
            return ("I can navigate to locations, pick up and manipulate objects, "
                   "answer questions, provide assistance, and interact naturally with humans.")
        elif 'humanoid' in topic_lower:
            return ("Humanoid robots are designed with human-like form and capabilities. "
                   "They can operate in human environments and interact using human-like "
                   "modalities such as speech and gestures.")
        else:
            return ("I can provide information about robotics, AI, and related topics. "
                   "For more specific information, please ask detailed questions.")

    def trigger_emergency_procedures(self):
        """
        Trigger emergency safety procedures.
        """
        # This would stop all robot motion and enter safe state
        print("Emergency procedures activated - all systems safe mode")

    def enter_idle_state(self):
        """Actions when entering IDLE state."""
        print("Entering IDLE state - awaiting activation")

    def exit_idle_state(self):
        """Actions when exiting IDLE state."""
        print("Exiting IDLE state - activating interaction")

    def enter_greeting_state(self):
        """Actions when entering GREETING state."""
        print("Entering GREETING state - preparing welcome message")

    def exit_greeting_state(self):
        """Actions when exiting GREETING state."""
        print("Exiting GREETING state - greeting complete")

    def enter_listening_state(self):
        """Actions when entering LISTENING state."""
        print("Entering LISTENING state - ready to receive input")

    def exit_listening_state(self):
        """Actions when exiting LISTENING state."""
        print("Exiting LISTENING state - input received")

    def enter_processing_state(self):
        """Actions when entering PROCESSING state."""
        print("Entering PROCESSING state - analyzing input")

    def exit_processing_state(self):
        """Actions when exiting PROCESSING state."""
        print("Exiting PROCESSING state - processing complete")

    def enter_responding_state(self):
        """Actions when entering RESPONDING state."""
        print("Entering RESPONDING state - generating response")

    def exit_responding_state(self):
        """Actions when exiting RESPONDING state."""
        print("Exiting RESPONDING state - response delivered")

    def enter_navigating_state(self):
        """Actions when entering NAVIGATING state."""
        print("Entering NAVIGATING state - executing navigation")

    def exit_navigating_state(self):
        """Actions when exiting NAVIGATING state."""
        print("Exiting NAVIGATING state - navigation complete")

    def enter_manipulating_state(self):
        """Actions when entering MANIPULATING state."""
        print("Entering MANIPULATING state - executing manipulation")

    def exit_manipulating_state(self):
        """Actions when exiting MANIPULATING state."""
        print("Exiting MANIPULATING state - manipulation complete")

    def enter_emergency_state(self):
        """Actions when entering EMERGENCY state."""
        print("Entering EMERGENCY state - activating safety protocols")

    def exit_emergency_state(self):
        """Actions when exiting EMERGENCY state."""
        print("Exiting EMERGENCY state - safety protocols complete")
```

## Natural Language Generation (NLG)

### Context-Aware Response Generation

```python
import random
import re
from typing import Dict, List

class NaturalLanguageGenerator:
    def __init__(self):
        # Response templates categorized by context and intent
        self.response_templates = self.load_response_templates()

        # Personality parameters
        self.personality_traits = {
            'formality': 0.5,      # 0.0 = very casual, 1.0 = very formal
            'expressiveness': 0.7, # 0.0 = monotone, 1.0 = expressive
            'helpfulness': 0.9,    # 0.0 = unhelpful, 1.0 = very helpful
            'patience': 0.8        # 0.0 = impatient, 1.0 = very patient
        }

        # Context-specific generators
        self.context_generators = {
            'greeting': self.generate_greeting_response,
            'navigation': self.generate_navigation_response,
            'manipulation': self.generate_manipulation_response,
            'information': self.generate_information_response,
            'confirmation': self.generate_confirmation_response,
            'error': self.generate_error_response
        }

    def load_response_templates(self):
        """
        Load response templates from configuration.
        """
        return {
            'greeting': {
                'formal': [
                    "Good day! I am your humanoid assistant. How may I be of service?",
                    "Greetings! I am pleased to make your acquaintance. What would you like assistance with?",
                    "Welcome! I am your robotic assistant. How can I help you today?"
                ],
                'casual': [
                    "Hey there! I'm your robot buddy. What's up?",
                    "Hi! Ready to help out. What would you like me to do?",
                    "Hello! Nice to see you. How can I assist?"
                ]
            },
            'navigation': {
                'success': [
                    "I'm navigating to {destination}. Please follow at a safe distance.",
                    "Heading to {destination} now. I'll lead the way.",
                    "Moving toward {destination}. The path looks clear."
                ],
                'obstacle': [
                    "I've detected an obstacle at {destination}. I'll find an alternative route.",
                    "There's something in the way to {destination}. Let me navigate around it.",
                    "Path to {destination} is blocked. Calculating new route."
                ]
            },
            'manipulation': {
                'success': [
                    "Successfully grasped the {object}. I'll hold it securely.",
                    "Object {object} picked up. What should I do with it?",
                    "Grasped {object} successfully. Ready for next instruction."
                ],
                'failure': [
                    "I'm having difficulty grasping {object}. Could you adjust its position?",
                    "Cannot pick up {object} right now. It might be too heavy or in an awkward position.",
                    "Failed to grasp {object}. Would you like me to try again?"
                ]
            },
            'information': {
                'positive': [
                    "About {topic}: {information}",
                    "Here's what I know regarding {topic}: {information}",
                    "Regarding {topic}, I can tell you that {information}"
                ],
                'negative': [
                    "I don't have specific information about {topic}. Could you ask about something else?",
                    "I'm not sure about {topic}. I can help with other questions though.",
                    "I haven't learned about {topic} yet. Is there something else I can assist with?"
                ]
            },
            'confirmation': {
                'affirmative': [
                    "Confirmed. I'll proceed with {action}.",
                    "Understood. Executing {action} now.",
                    "Got it. Performing {action} as requested."
                ],
                'negative': [
                    "Acknowledged. I won't proceed with {action}.",
                    "Understood. Canceling {action}.",
                    "Got it. I'll skip {action}."
                ]
            },
            'error': {
                'low_confidence': [
                    "I'm not sure I understood correctly. Could you repeat that?",
                    "My confidence is low on that input. Could you rephrase?",
                    "I didn't catch that clearly. Please speak more distinctly."
                ],
                'unknown_intent': [
                    "I'm not sure what you'd like me to do. Could you be more specific?",
                    "I don't understand that request. Can you explain differently?",
                    "I'm confused about your request. Could you clarify?"
                ],
                'execution_failure': [
                    "I encountered an issue executing that command. Would you like me to try again?",
                    "Sorry, I couldn't complete that action. What else can I help with?",
                    "There was a problem with that task. How else can I assist?"
                ]
            }
        }

    def generate_response(self, intent, entities, context=None, confidence=0.8):
        """
        Generate natural language response based on intent and context.

        Args:
            intent: Classified intent
            entities: Extracted entities
            context: Additional context information
            confidence: Confidence in classification

        Returns:
            response: Generated natural language response
        """
        if context is None:
            context = {}

        # Determine response category based on intent and context
        response_category = self.categorize_response(intent, confidence, context)

        # Generate response using appropriate template
        if intent in self.context_generators:
            response = self.context_generators[intent](entities, context, confidence)
        else:
            # Use generic template-based generation
            response = self.generate_generic_response(intent, entities, context, confidence)

        # Apply personality modifications
        personalized_response = self.apply_personality_modifications(response, context)

        # Add emotional tone if applicable
        emotional_response = self.add_emotional_tone(personalized_response, context)

        return emotional_response

    def categorize_response(self, intent, confidence, context):
        """
        Categorize the response type based on intent, confidence, and context.
        """
        if confidence < 0.5:
            return 'error'
        elif intent == 'greeting':
            return 'greeting'
        elif intent == 'navigation':
            if context.get('obstacle_detected', False):
                return 'obstacle'
            else:
                return 'success'
        elif intent == 'manipulation':
            if context.get('manipulation_success', True):
                return 'success'
            else:
                return 'failure'
        elif intent == 'information_request':
            return 'information'
        elif intent == 'confirmation':
            if context.get('confirmed', True):
                return 'affirmative'
            else:
                return 'negative'
        else:
            return 'default'

    def generate_greeting_response(self, entities, context, confidence):
        """
        Generate greeting response.
        """
        formality_level = self.personality_traits['formality']
        template_category = 'formal' if formality_level > 0.6 else 'casual'

        templates = self.response_templates['greeting'][template_category]
        template = random.choice(templates)

        return template

    def generate_navigation_response(self, entities, context, confidence):
        """
        Generate navigation response.
        """
        destination = self.extract_entity_value(entities, 'location', 'the destination')

        if context.get('obstacle_detected', False):
            category = 'obstacle'
            templates = self.response_templates['navigation'][category]
            template = random.choice(templates)
            return template.format(destination=destination)
        else:
            category = 'success'
            templates = self.response_templates['navigation'][category]
            template = random.choice(templates)
            return template.format(destination=destination)

    def generate_manipulation_response(self, entities, context, confidence):
        """
        Generate manipulation response.
        """
        obj = self.extract_entity_value(entities, 'object', 'the object')

        if context.get('manipulation_success', True):
            category = 'success'
            templates = self.response_templates['manipulation'][category]
            template = random.choice(templates)
            return template.format(object=obj)
        else:
            category = 'failure'
            templates = self.response_templates['manipulation'][category]
            template = random.choice(templates)
            return template.format(object=obj)

    def generate_information_response(self, entities, context, confidence):
        """
        Generate information response.
        """
        topic = context.get('topic', self.extract_entity_value(entities, 'object', 'the topic'))
        information = context.get('information', 'some information')

        if information and information != 'some information':
            category = 'positive'
            templates = self.response_templates['information'][category]
            template = random.choice(templates)
            return template.format(topic=topic, information=information)
        else:
            category = 'negative'
            templates = self.response_templates['information'][category]
            template = random.choice(templates)
            return template.format(topic=topic)

    def generate_confirmation_response(self, entities, context, confidence):
        """
        Generate confirmation response.
        """
        action = context.get('action', 'the requested action')

        if context.get('confirmed', True):
            category = 'affirmative'
            templates = self.response_templates['confirmation'][category]
            template = random.choice(templates)
            return template.format(action=action)
        else:
            category = 'negative'
            templates = self.response_templates['confirmation'][category]
            template = random.choice(templates)
            return template.format(action=action)

    def generate_error_response(self, entities, context, confidence):
        """
        Generate error response based on error type.
        """
        error_type = context.get('error_type', 'low_confidence')

        templates = self.response_templates['error'][error_type]
        template = random.choice(templates)

        return template

    def generate_generic_response(self, intent, entities, context, confidence):
        """
        Generate generic response when specific generator is not available.
        """
        if confidence < 0.5:
            return self.generate_error_response(entities, context, confidence)
        else:
            return f"I understand you're requesting {intent}. How can I assist with that?"

    def extract_entity_value(self, entities, entity_type, default_value):
        """
        Extract value of specific entity type from entities list.
        """
        for entity in entities:
            if entity.get('type') == entity_type:
                return entity.get('text', default_value)
        return default_value

    def apply_personality_modifications(self, response, context):
        """
        Apply personality-based modifications to response.
        """
        modified_response = response

        # Adjust formality
        if self.personality_traits['formality'] < 0.3:
            # Very casual
            modified_response = modified_response.replace("I am", "I'm").replace("you are", "you're")
            modified_response += " Cool!"
        elif self.personality_traits['formality'] > 0.7:
            # Very formal
            modified_response = "Certainly, " + modified_response
            modified_response += " Please let me know if you require any additional assistance."

        # Add expressiveness
        if self.personality_traits['expressiveness'] > 0.7:
            exclamation_count = int(self.personality_traits['expressiveness'] * 2)
            modified_response += "!" * exclamation_count

        # Adjust helpfulness
        if self.personality_traits['helpfulness'] > 0.8:
            modified_response += " I'm here to assist with anything else you might need."

        return modified_response

    def add_emotional_tone(self, response, context):
        """
        Add emotional tone to response based on context.
        """
        emotional_keywords = {
            'happy': ['great', 'wonderful', 'fantastic', 'excellent', 'amazing'],
            'sad': ['sorry', 'apologies', 'unfortunately', 'regret'],
            'excited': ['wow', 'incredible', 'amazing', 'fantastic'],
            'concerned': ['concerned', 'worry', 'careful', 'mindful']
        }

        emotion = context.get('emotion', 'neutral')

        if emotion in ['happy', 'excited']:
            keyword = random.choice(emotional_keywords[emotion])
            return f"{keyword.title()}! {response}"
        elif emotion == 'sad':
            keyword = random.choice(emotional_keywords[emotion])
            return f"{keyword.title()}, {response.lower()}"
        elif emotion == 'concerned':
            keyword = random.choice(emotional_keywords[emotion])
            return f"{response} I'm {keyword} about this situation."

        return response

    def generate_dialogue_act(self, response, intent):
        """
        Generate dialogue act annotation for the response.
        """
        dialogue_acts = {
            'greeting': 'greet',
            'navigation': 'inform_direction',
            'manipulation': 'confirm_action',
            'information_request': 'answer_query',
            'confirmation': 'confirm_understanding',
            'goodbye': 'farewell',
            'help_request': 'offer_assistance'
        }

        act = dialogue_acts.get(intent, 'acknowledge')

        return {
            'response': response,
            'dialogue_act': act,
            'intent': intent
        }

    def personalize_response(self, response, user_profile):
        """
        Personalize response based on user profile.
        """
        if not user_profile:
            return response

        # Use user name if available
        if 'name' in user_profile and user_profile['name'] != 'User':
            response = f"{user_profile['name']}, {response}"

        # Adjust based on user familiarity
        familiarity = user_profile.get('familiarity', 0.5)
        if familiarity > 0.7:
            # More casual with familiar users
            response = response.replace("I am", "I'm")
        elif familiarity < 0.3:
            # More formal with new users
            response = "Dear user, " + response

        # Adjust based on user preferences
        preferences = user_profile.get('preferences', {})
        if preferences.get('preferred_formality', 'neutral') == 'formal':
            response = "Sir/Madam, " + response
        elif preferences.get('preferred_formality', 'neutral') == 'casual':
            response = response.replace("I am", "I'm").replace("you are", "you're")

        return response

class ContextAwareNLG(NaturalLanguageGenerator):
    """
    Context-aware NLG that considers conversation history and user state.
    """

    def __init__(self):
        super().__init__()
        self.conversation_context = []
        self.max_context_length = 10

    def generate_context_aware_response(self, intent, entities, user_context=None):
        """
        Generate response considering conversation context.

        Args:
            intent: Current intent
            entities: Current entities
            user_context: User-specific context information

        Returns:
            response: Context-aware response
        """
        # Analyze conversation history
        conversation_analysis = self.analyze_conversation_history()

        # Consider user state
        user_state = user_context.get('user_state', 'neutral') if user_context else 'neutral'

        # Generate base response
        base_response = self.generate_response(intent, entities, confidence=0.9)

        # Enhance with context
        enhanced_response = self.enhance_with_context(
            base_response, intent, conversation_analysis, user_state
        )

        # Store in context history
        self.conversation_context.append({
            'intent': intent,
            'entities': entities,
            'response': enhanced_response,
            'timestamp': time.time()
        })

        # Maintain context size
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context.pop(0)

        return enhanced_response

    def analyze_conversation_history(self):
        """
        Analyze recent conversation history for patterns.
        """
        if not self.conversation_context:
            return {'repetition_count': 0, 'topic_coherence': 0.5, 'user_patience': 0.8}

        # Count recent repetitions
        recent_intents = [ctx['intent'] for ctx in self.conversation_context[-5:]]
        repetition_count = len(recent_intents) - len(set(recent_intents))

        # Calculate topic coherence
        unique_topics = len(set(recent_intents))
        coherence = unique_topics / min(5, len(recent_intents))

        # Estimate user patience based on repetition
        user_patience = max(0.1, 0.9 - (repetition_count * 0.2))

        return {
            'repetition_count': repetition_count,
            'topic_coherence': coherence,
            'user_patience': user_patience
        }

    def enhance_with_context(self, base_response, intent, conversation_analysis, user_state):
        """
        Enhance response with conversation and user context.
        """
        enhanced_response = base_response

        # Adjust for repetition
        if conversation_analysis['repetition_count'] > 1:
            enhanced_response = f"I notice we're discussing this topic again. {enhanced_response}"

        # Adjust for user state
        if user_state == 'frustrated':
            enhanced_response = f"I understand you might be frustrated. {enhanced_response} Please let me know if I can help differently."
        elif user_state == 'excited':
            enhanced_response = f"{enhanced_response} I'm excited to help with that!"
        elif user_state == 'tired':
            enhanced_response = f"{enhanced_response} I'll be brief and efficient."

        # Add transition phrases based on previous intent
        if self.conversation_context:
            previous_intent = self.conversation_context[-1]['intent']
            if previous_intent != intent:
                transition_phrases = {
                    'navigation': 'Regarding navigation to',
                    'manipulation': 'For manipulation of',
                    'information_request': 'About your question on',
                    'greeting': 'To continue our conversation about'
                }

                transition_phrase = transition_phrases.get(intent, '')
                if transition_phrase:
                    enhanced_response = f"{transition_phrase}, {enhanced_response.lower()}"

        return enhanced_response

# Example usage
def demo_nlg():
    nlg = ContextAwareNLG()

    # Simulate conversation
    sample_inputs = [
        {'intent': 'greeting', 'entities': [], 'user_context': {'name': 'John', 'familiarity': 0.8}},
        {'intent': 'navigation', 'entities': [{'type': 'location', 'text': 'kitchen'}], 'user_context': {}},
        {'intent': 'manipulation', 'entities': [{'type': 'object', 'text': 'red cup'}], 'user_context': {}},
        {'intent': 'information_request', 'entities': [{'type': 'object', 'text': 'robotics'}], 'user_context': {}},
        {'intent': 'goodbye', 'entities': [], 'user_context': {'user_state': 'happy'}}
    ]

    for input_data in sample_inputs:
        response = nlg.generate_context_aware_response(
            input_data['intent'],
            input_data['entities'],
            input_data['user_context']
        )
        print(f"Intent: {input_data['intent']}")
        print(f"Response: {response}\n")

if __name__ == "__main__":
    demo_nlg()
```

## Integration with Isaac Platform

### Isaac NLP Components

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image, LaserScan
from dialog_msgs.msg import DialogState as DialogStateMsg
from builtin_interfaces.msg import Duration

class IsaacNLPNode(Node):
    def __init__(self):
        super().__init__('isaac_nlp_node')

        # Initialize NLP components
        self.asr_system = RoboticsASR()
        self.nlu_system = ContextualNLU()
        self.dialog_manager = StateBasedDialogManager()
        self.nlg_system = ContextAwareNLG()

        # Publishers
        self.speech_pub = self.create_publisher(String, '/robot/speech_output', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.dialog_state_pub = self.create_publisher(DialogStateMsg, '/dialog/state', 10)

        # Subscribers
        self.speech_input_sub = self.create_subscription(
            String,
            '/robot/speech_input',
            self.speech_input_callback,
            10
        )

        self.audio_sub = self.create_subscription(
            AudioData,
            '/microphone/audio',
            self.audio_callback,
            10
        )

        # Timer for periodic processing
        self.nlp_timer = self.create_timer(0.1, self.nlp_processing_step)

        # Robot state
        self.robot_state = {
            'position': [0.0, 0.0, 0.0],
            'orientation': [0.0, 0.0, 0.0, 1.0],
            'battery_level': 1.0,
            'current_task': 'idle'
        }

        self.get_logger().info('Isaac NLP node initialized')

    def speech_input_callback(self, msg):
        """
        Handle speech input from other nodes or manual input.
        """
        text_input = msg.data
        self.get_logger().info(f'Received speech input: {text_input}')

        # Process through NLP pipeline
        try:
            # Natural Language Understanding
            nlu_result = self.nlu_system.process_with_context(
                text_input,
                self.dialog_manager.current_context.conversation_history if self.dialog_manager.current_context else []
            )

            # Dialogue Management
            response = self.dialog_manager.process_input(
                text_input,
                input_type='speech',
                user_id='default_user'
            )

            # Natural Language Generation
            final_response = self.nlg_system.generate_context_aware_response(
                nlu_result['intent'],
                nlu_result['entities'],
                user_context={'user_state': 'neutral', 'name': 'User'}
            )

            # Publish response
            response_msg = String()
            response_msg.data = final_response
            self.speech_pub.publish(response_msg)

            # Log the exchange
            self.get_logger().info(f'Generated response: {final_response}')

        except Exception as e:
            self.get_logger().error(f'Error in NLP processing: {e}')
            error_response = "I'm sorry, I encountered an error processing your request."
            error_msg = String()
            error_msg.data = error_response
            self.speech_pub.publish(error_msg)

    def audio_callback(self, msg):
        """
        Handle raw audio data for speech recognition.
        """
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

            # Perform speech recognition
            recognition_result = self.asr_system.recognize_speech(audio_data, msg.sample_rate)

            if recognition_result['confidence'] > 0.6:  # Confidence threshold
                # Process the recognized text
                text_msg = String()
                text_msg.data = recognition_result['text']
                self.speech_input_callback(text_msg)
            else:
                self.get_logger().info(f'Low confidence recognition: {recognition_result["confidence"]:.2f}')

        except Exception as e:
            self.get_logger().error(f'Error in audio processing: {e}')

    def nlp_processing_step(self):
        """
        Periodic NLP processing step.
        """
        # Update dialog state publication
        if self.dialog_manager.current_context:
            state_msg = DialogStateMsg()
            state_msg.state = self.dialog_manager.current_context.state.value
            state_msg.user_id = self.dialog_manager.current_context.user_id
            state_msg.confidence = self.dialog_manager.current_context.confidence
            state_msg.timestamp = self.get_clock().now().to_msg()

            self.dialog_state_pub.publish(state_msg)

        # Check for conversation timeouts
        if self.dialog_manager.current_context:
            time_since_interaction = (
                time.time() - self.dialog_manager.current_context.last_interaction_time
            )

            if time_since_interaction > 30:  # 30 seconds timeout
                self.get_logger().info('Conversation timeout - transitioning to idle')
                self.dialog_manager.transition_to_state(DialogState.IDLE)

    def update_robot_state(self, new_state):
        """
        Update robot state from other system components.
        """
        self.robot_state.update(new_state)

    def execute_robot_action(self, action_type, parameters):
        """
        Execute robot action based on NLP interpretation.
        """
        if action_type == 'navigation':
            self.execute_navigation(parameters)
        elif action_type == 'manipulation':
            self.execute_manipulation(parameters)
        elif action_type == 'greeting':
            self.execute_greeting(parameters)
        else:
            self.get_logger().info(f'Action type {action_type} not implemented')

    def execute_navigation(self, params):
        """
        Execute navigation command.
        """
        destination = params.get('location', 'unknown')
        self.get_logger().info(f'Navigating to: {destination}')

        # Create simple movement command (in reality, this would use navigation stack)
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.3  # Move forward at 0.3 m/s
        cmd_vel.angular.z = 0.0  # No rotation

        # Publish command
        self.cmd_vel_pub.publish(cmd_vel)

    def execute_manipulation(self, params):
        """
        Execute manipulation command.
        """
        object_name = params.get('object', 'unknown')
        self.get_logger().info(f'Manipulating object: {object_name}')

        # In real implementation, this would call manipulation stack
        # For this example, we'll just log the action
        pass

    def execute_greeting(self, params):
        """
        Execute greeting action.
        """
        self.get_logger().info('Executing greeting behavior')

        # This would trigger appropriate greeting behaviors
        # For this example, we'll just log
        pass

def main(args=None):
    rclpy.init(args=args)
    nlp_node = IsaacNLPNode()

    try:
        rclpy.spin(nlp_node)
    except KeyboardInterrupt:
        nlp_node.get_logger().info('Shutting down Isaac NLP node...')
    finally:
        nlp_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

Natural Language Processing for humanoid robots involves sophisticated integration of multiple AI components to enable natural human-robot interaction. The key elements include:

1. **Automatic Speech Recognition**: Converting human speech to text with robustness to environmental conditions
2. **Natural Language Understanding**: Extracting intent and entities from text input
3. **Dialogue Management**: Maintaining conversation state and context
4. **Natural Language Generation**: Creating appropriate, context-aware responses
5. **Context Awareness**: Incorporating environmental and user-specific information
6. **Integration with Robot Systems**: Connecting NLP with robot control and perception

These components work together to enable humanoid robots to engage in natural, meaningful conversations while performing complex robotic tasks, making them more accessible and useful in human environments.