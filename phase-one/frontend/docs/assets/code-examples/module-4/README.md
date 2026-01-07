# Module 4 Code Examples

This directory contains VLA model code examples for Module 4: VLA Robotics & Capstone.

## Contents:
- Whisper voice command integration examples
- LLM to ROS 2 action planning examples
- VLA model integration examples
- Complete autonomous humanoid system example
- Other relevant code for the module

## Code Syntax Highlighting Guide

All code examples in this textbook use standard Markdown syntax highlighting. Below are the supported language identifiers:

### Python Code Blocks
```python
# This is a Whisper integration example
import whisper
import openai
import rclpy
from std_msgs.msg import String

# Load Whisper model
model = whisper.load_model("base.en")

# Example ROS 2 node with Whisper integration
class WhisperNode(Node):
    def __init__(self):
        super().__init__('whisper_node')
        self.text_pub = self.create_publisher(String, 'recognized_text', 10)
```

### YAML Code Blocks
```yaml
# This is a YAML configuration example for LLM integration
llm_config:
  model_name: "gpt-3.5-turbo"
  temperature: 0.1
  max_tokens: 256
  api_key: "${OPENAI_API_KEY}"
```

### Bash/Shell Code Blocks
```bash
# This is a bash/shell command example for VLA system
# Install required packages
pip3 install openai-whisper torch torchvision torchaudio
pip3 install openai rclpy

# Run VLA system
python3 vla_robot_system.py
```

### JSON Code Blocks
```json
{
  "action_plan": {
    "intent": "navigation",
    "target_location": "kitchen",
    "action_sequence": [
      {"type": "navigate", "target": "kitchen", "confidence": 0.9},
      {"type": "detect", "target": "cup", "confidence": 0.8}
    ],
    "estimated_time": 120
  }
}
```

## Execution Notes for Code Examples

### Prerequisites
- Python 3.8+ with pip
- OpenAI API key (for GPT integration)
- Whisper models downloaded locally (or internet connection for download)
- ROS 2 Humble with required packages
- Microphone for voice input (for Whisper examples)

### Running Whisper Integration Examples
1. Install Whisper: `pip3 install openai-whisper`
2. Load model: `whisper.load_model("base.en")` (downloads if needed)
3. Ensure audio input device is available
4. Run example: `python3 whisper_integration_example.py`

### Running LLM Integration Examples
1. Set OpenAI API key: `export OPENAI_API_KEY='your-api-key'`
2. Install required packages: `pip3 install openai langchain`
3. Run example: `python3 llm_planning_example.py`
4. Monitor for costs associated with API usage

### Running Complete VLA System
1. Source ROS 2: `source /opt/ros/humble/setup.bash`
2. Install all dependencies as per requirements
3. Launch system components separately in different terminals
4. Monitor system performance and resource usage

### Common Execution Issues and Solutions
- **API rate limits**: Implement retry logic with exponential backoff
- **Audio input errors**: Check microphone permissions and availability
- **Memory issues**: Use smaller models (e.g., Whisper "base" instead of "large")
- **Network connectivity**: Ensure stable internet for API-based LLMs
- **ROS 2 connection issues**: Verify network configuration and domain IDs