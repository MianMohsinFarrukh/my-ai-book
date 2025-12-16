# Module 1 Code Examples

This directory contains ROS 2 Python code examples for Module 1: Physical AI Foundations.

## Contents:
- Basic ROS 2 node examples
- Publisher/subscriber examples
- Service/client examples
- URDF examples
- Other relevant code for the module

## Code Syntax Highlighting Guide

All code examples in this textbook use standard Markdown syntax highlighting. Below are the supported language identifiers:

### Python Code Blocks
```python
# This is a Python code example
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
```

### Bash/Shell Code Blocks
```bash
# This is a bash/shell command example
source /opt/ros/humble/setup.bash
ros2 run my_package my_node
```

### XML/URDF Code Blocks
```xml
<!-- This is an XML/URDF example -->
<robot name="simple_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </visual>
  </link>
</robot>
```

### YAML Code Blocks
```yaml
# This is a YAML configuration example
robot:
  model: "H1"
  height: 1.35  # meters
  weight: 40.0   # kg
```

## Execution Notes for Code Examples

### Prerequisites
- ROS 2 Humble Hawksbill installed
- Python 3.8+ environment
- Appropriate workspace setup (`colcon build` completed)

### Running Python Nodes
1. Source ROS 2 environment: `source /opt/ros/humble/setup.bash`
2. Navigate to workspace: `cd ~/ros2_ws`
3. Source workspace: `source install/setup.bash`
4. Run node: `python3 path/to/example.py`

### Common Execution Issues and Solutions
- **ModuleNotFoundError**: Ensure proper sourcing of ROS 2 and workspace
- **Permission denied**: Check file permissions with `chmod +x script.py`
- **Port conflicts**: Verify no other nodes are using the same topics/services
- **Import errors**: Confirm all required packages are installed via `apt install`