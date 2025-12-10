---
sidebar_position: 1
title: 'Chapter 1: Whisper Voice Commands'
---

# Chapter 1: Whisper Voice Commands

This chapter covers integrating Whisper speech recognition with robotics systems for voice command processing.

## Introduction to Whisper for Robotics

Whisper is OpenAI's robust speech recognition model that can be adapted for robotics applications. It provides:

- **High accuracy**: State-of-the-art performance across multiple languages
- **Robustness**: Works well in various acoustic environments
- **Real-time capability**: Can be optimized for real-time processing
- **Open source**: Available under MIT license for commercial use

## Whisper Architecture

Whisper uses a Transformer-based architecture with:

- **Encoder**: Processes audio input with convolutional layers and transformer blocks
- **Decoder**: Generates text tokens conditioned on the encoded audio
- **Multilingual support**: Trained on 98 languages for global applications

## Installing Whisper for Robotics

```bash
# Install Whisper and related packages
pip install openai-whisper
pip install sounddevice  # For audio input
pip install pyaudio      # Alternative audio library
pip install vosk         # For offline speech recognition alternatives
```

## Basic Whisper Integration

Here's a simple example of integrating Whisper with a ROS 2 node:

```python
import rclpy
from rclpy.node import Node
import whisper
import sounddevice as sd
import numpy as np
from std_msgs.msg import String
import queue
import threading

class WhisperNode(Node):
    def __init__(self):
        super().__init__('whisper_node')

        # Load Whisper model
        self.model = whisper.load_model("base.en")  # or "base", "small", etc.

        # Audio parameters
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()

        # Publisher for recognized text
        self.text_pub = self.create_publisher(String, 'recognized_text', 10)

        # Start audio recording thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()

        # Timer for processing audio
        self.timer = self.create_timer(2.0, self.process_audio)  # Process every 2 seconds

        self.get_logger().info('Whisper node initialized')

    def record_audio(self):
        """Record audio from microphone"""
        def audio_callback(indata, frames, time, status):
            if status:
                self.get_logger().warning(f'Audio status: {status}')
            # Add audio data to queue
            self.audio_queue.put(indata.copy())

        # Start audio stream
        with sd.InputStream(callback=audio_callback,
                           channels=1,
                           samplerate=self.sample_rate,
                           dtype=np.float32):
            while rclpy.ok():
                sd.sleep(100)

    def process_audio(self):
        """Process accumulated audio and recognize speech"""
        if not self.audio_queue.empty():
            # Collect audio data from queue
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())

            if audio_data:
                # Concatenate audio data
                audio_array = np.concatenate(audio_data, axis=0)

                # Convert to float32 if needed
                if audio_array.dtype != np.float32:
                    audio_array = audio_array.astype(np.float32)

                # Normalize audio
                audio_array = audio_array / np.max(np.abs(audio_array))

                # Run Whisper transcription
                result = self.model.transcribe(audio_array, fp16=False)
                recognized_text = result['text'].strip()

                if recognized_text:  # Only publish if there's text
                    self.get_logger().info(f'Recognized: {recognized_text}')

                    # Publish recognized text
                    msg = String()
                    msg.data = recognized_text
                    self.text_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WhisperNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Voice Command Processing

For robotics applications, you'll typically want to process recognized text into commands:

```python
class VoiceCommandProcessor:
    def __init__(self):
        self.commands = {
            'move forward': 'linear_x 0.5',
            'move backward': 'linear_x -0.5',
            'turn left': 'angular_z 0.5',
            'turn right': 'angular_z -0.5',
            'stop': 'stop_robot',
            'go to kitchen': 'navigate_to_kitchen',
            'pick up object': 'grasp_object'
        }

    def parse_command(self, text):
        """Parse recognized text into robot commands"""
        text_lower = text.lower()

        for command_phrase, robot_command in self.commands.items():
            if command_phrase in text_lower:
                return robot_command

        # Handle numeric values
        import re
        numbers = re.findall(r'\d+', text_lower)
        if 'move' in text_lower and numbers:
            distance = int(numbers[0]) if numbers else 1
            return f'move_distance {distance}'

        return 'unknown_command'
```

## Optimizing Whisper for Real-time Performance

For real-time robotics applications, consider these optimizations:

### 1. Model Selection
```python
# Choose smaller models for faster inference
models = {
    'tiny': 'Fastest, least accurate',
    'base': 'Good balance of speed and accuracy',
    'small': 'Better accuracy, slower',
    'medium': 'High accuracy, slow',
    'large': 'Highest accuracy, slowest'
}

model = whisper.load_model("base")  # Good balance for robotics
```

### 2. GPU Acceleration
```python
# Use GPU if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base").to(device)
```

### 3. Audio Preprocessing
```python
def preprocess_audio(audio_data, target_sr=16000):
    """Preprocess audio for optimal Whisper performance"""
    # Resample if needed
    if len(audio_data) > target_sr * 30:  # Limit to 30 seconds
        audio_data = audio_data[:target_sr * 30]

    # Normalize
    audio_data = audio_data / np.max(np.abs(audio_data))

    return audio_data
```

## Alternative: Vosk for Offline Recognition

For applications requiring offline speech recognition:

```python
from vosk import Model, KaldiRecognizer
import json

class VoskNode(Node):
    def __init__(self):
        super().__init__('vosk_node')

        # Load Vosk model
        self.model = Model("model_path")  # Download model from Kaldi website
        self.rec = KaldiRecognizer(self.model, 16000)

        # Audio setup
        self.stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )

        # Start recognition loop
        self.recognition_thread = threading.Thread(target=self.recognize_loop)
        self.recognition_thread.start()

    def recognize_loop(self):
        while rclpy.ok():
            data = self.stream.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                if 'text' in result and result['text']:
                    self.publish_recognized_text(result['text'])
```

## Best Practices for Voice Commands in Robotics

- **Use clear, unambiguous phrases**: "Move forward 2 meters" rather than "Go forward a bit"
- **Implement confirmation**: Have the robot acknowledge commands before executing
- **Handle errors gracefully**: Provide feedback when commands aren't understood
- **Consider acoustic environment**: Account for noise, reverberation, and distance
- **Privacy considerations**: Be mindful of recording and processing audio
- **Fallback mechanisms**: Provide alternative control methods if voice recognition fails

## References

Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022). Robust speech recognition via large-scale weak supervision. *arXiv preprint arXiv:2212.04356*.

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems*, 33, 1877-1901.

Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. *arXiv preprint arXiv:1810.04805*.

Ko, T., Peddinti, V., Povey, D., & Khudanpur, S. (2017). A study of using speaker embeddings for language recognition. *Proc. Interspeech 2017*, 1143-1147.