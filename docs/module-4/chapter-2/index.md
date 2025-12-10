---
sidebar_position: 2
title: 'Chapter 2: LLM → ROS 2 Action Planner'
---

# Chapter 2: LLM → ROS 2 Action Planner

This chapter covers creating AI action planners that translate high-level commands from Large Language Models to ROS 2 actions.

## Introduction to LLM-Based Action Planning

Large Language Models (LLMs) can serve as high-level cognitive planners for robotics systems, translating natural language commands into executable robotic actions. This approach enables:

- **Natural human-robot interaction**: Communicate with robots using everyday language
- **Adaptive planning**: Handle ambiguous or complex commands flexibly
- **Knowledge integration**: Leverage the LLM's world knowledge for planning
- **Task generalization**: Apply learned patterns to new scenarios

## Architecture of LLM-ROS Integration

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Human User    │ -> │  LLM Action      │ -> │  ROS 2 Action   │
│                 │    │  Planner         │    │  Executor       │
│ "Go to kitchen" │    │ • Parse command  │    │ • Execute plan  │
│                 │    │ • Generate plan  │    │ • Monitor exec  │
└─────────────────┘    │ • Validate plan  │    │ • Provide feedback │
                       └──────────────────┘    └─────────────────┘
                                │
                                v
                       ┌──────────────────┐
                       │  Robot State     │
                       │  Knowledge       │
                       │ • Environment    │
                       │ • Capabilities   │
                       │ • Constraints    │
                       └──────────────────┘
```

## Setting Up LLM Integration

### Required Libraries

```bash
# Install required packages
pip install openai  # For OpenAI models
# OR
pip install transformers torch  # For local models like Llama
pip install langchain langchain-community  # For LLM orchestration
pip install rclpy  # ROS 2 Python client library
```

### Basic LLM Node Implementation

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class LLMActionPlannerNode(Node):
    def __init__(self):
        super().__init__('llm_action_planner')

        # Initialize LLM (using OpenAI as example)
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=256
        )

        # Create subscriber for natural language commands
        self.command_sub = self.create_subscription(
            String,
            'natural_language_command',
            self.command_callback,
            10
        )

        # Create publisher for parsed commands
        self.parsed_command_pub = self.create_publisher(
            String,
            'parsed_command',
            10
        )

        # Navigation action client
        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        # Task execution map
        self.task_map = {
            'navigation': self.execute_navigation,
            'manipulation': self.execute_manipulation,
            'inspection': self.execute_inspection
        }

        self.get_logger().info('LLM Action Planner initialized')

    def command_callback(self, msg):
        """Process natural language command"""
        command = msg.data
        self.get_logger().info(f'Received command: {command}')

        # Parse command using LLM
        parsed_command = self.parse_with_llm(command)
        self.get_logger().info(f'Parsed command: {parsed_command}')

        # Execute the parsed command
        self.execute_parsed_command(parsed_command)

    def parse_with_llm(self, command):
        """Use LLM to parse natural language into structured command"""
        prompt = f"""
        Parse the following natural language command for a robot:
        Command: "{command}"

        Respond in JSON format with:
        {{
            "action_type": "navigation|manipulation|inspection",
            "target_location": "kitchen|bedroom|living_room|etc",
            "target_object": "object_name|None",
            "action": "go_to|pick_up|inspect|grasp|etc",
            "parameters": {{"distance": "value", "speed": "value", etc}}
        }}

        Only respond with the JSON, no other text.
        """

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self.get_logger().error(f'LLM parsing failed: {e}')
            return '{"action_type": "unknown", "action": "unknown"}'

    def execute_parsed_command(self, parsed_json_str):
        """Execute the parsed command"""
        import json
        try:
            parsed_command = json.loads(parsed_json_str)
            action_type = parsed_command.get('action_type', 'unknown')

            if action_type in self.task_map:
                self.task_map[action_type](parsed_command)
            else:
                self.get_logger().error(f'Unknown action type: {action_type}')
        except json.JSONDecodeError as e:
            self.get_logger().error(f'Failed to parse JSON: {e}')

    def execute_navigation(self, command_data):
        """Execute navigation commands"""
        target_location = command_data.get('target_location', 'unknown')

        # Map location to coordinates (in a real system, you'd have a map)
        location_map = {
            'kitchen': [1.0, 2.0, 0.0],
            'bedroom': [-1.0, 3.0, 0.0],
            'living_room': [0.0, 0.0, 0.0]
        }

        if target_location in location_map:
            x, y, theta = location_map[target_location]
            self.navigate_to_pose(x, y, theta)
        else:
            self.get_logger().error(f'Unknown location: {target_location}')

    def navigate_to_pose(self, x, y, theta):
        """Send navigation goal to Nav2"""
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation server not available')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert theta to quaternion
        import math
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2.0)

        self.nav_client.send_goal_async(goal_msg)

    def execute_manipulation(self, command_data):
        """Execute manipulation commands"""
        # Implementation for manipulation tasks
        target_object = command_data.get('target_object', 'unknown')
        self.get_logger().info(f'Planning manipulation for: {target_object}')

    def execute_inspection(self, command_data):
        """Execute inspection commands"""
        # Implementation for inspection tasks
        target_location = command_data.get('target_location', 'unknown')
        self.get_logger().info(f'Planning inspection of: {target_location}')


def main(args=None):
    rclpy.init(args=args)
    node = LLMActionPlannerNode()

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

## Creating Custom Prompts for Robotics

Effective LLM-based action planning requires well-designed prompts that account for robotics constraints:

```python
class RobotActionPrompt:
    def __init__(self):
        self.base_prompt = """
        You are a robot action planner. Your job is to translate high-level human commands
        into specific, executable actions for a mobile manipulator robot.

        The robot has the following capabilities:
        - Navigate to locations (kitchen, bedroom, living room, etc.)
        - Pick up objects (cups, books, toys, etc.)
        - Place objects at locations
        - Inspect areas for specific objects
        - Return to charging station

        The robot operates in a home environment with these constraints:
        - Must avoid obstacles
        - Cannot pick up objects that are too heavy
        - Needs to maintain battery level above 20%
        - Should confirm before executing dangerous actions

        For each command, return a JSON object with the action plan.
        """

    def create_task_prompt(self, command, robot_state, environment_map):
        """Create a specific prompt for the current task"""
        return f"""
        {self.base_prompt}

        Current robot state: {robot_state}
        Environment map: {environment_map}

        Human command: "{command}"

        Return a detailed JSON plan with:
        {{
            "success": true|false,
            "actions": [
                {{
                    "type": "navigate|pick_up|place|inspect|wait",
                    "target": "location|object_name",
                    "confidence": 0.0-1.0,
                    "reasoning": "why this action is needed"
                }}
            ],
            "estimated_time": "in seconds",
            "potential_issues": ["list", "of", "potential", "issues"]
        }}

        Only return the JSON, no other text.
        """
```

## Local LLM Options

For privacy or offline applications, you can use local LLMs:

```python
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class LocalLLMPlanner:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_plan(self, command):
        """Generate action plan using local LLM"""
        input_text = f"Robot command: {command}. Robot action plan:"
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 100,
                num_return_sequences=1,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(input_text):]  # Return only the generated part
```

## Safety and Validation

Implement safety checks for LLM-generated plans:

```python
class SafetyValidator:
    def __init__(self):
        self.forbidden_actions = [
            "jump", "fly", "break", "harm", "dangerous"
        ]
        self.physical_constraints = {
            "max_weight": 2.0,  # kg
            "max_distance": 10.0,  # meters
            "max_time": 300  # seconds
        }

    def validate_plan(self, plan_json):
        """Validate LLM-generated plan for safety"""
        try:
            plan = json.loads(plan_json)
        except json.JSONDecodeError:
            return False, "Invalid JSON format"

        # Check for forbidden actions
        for action in plan.get("actions", []):
            action_text = f"{action.get('type', '')} {action.get('target', '')}".lower()
            for forbidden in self.forbidden_actions:
                if forbidden in action_text:
                    return False, f"Forbidden action detected: {forbidden}"

        # Check physical constraints
        estimated_time = plan.get("estimated_time", 0)
        if estimated_time > self.physical_constraints["max_time"]:
            return False, f"Plan exceeds time limit: {estimated_time}s"

        return True, "Plan is safe to execute"
```

## Integration with Behavior Trees

Combine LLM planning with traditional robotics planning:

```python
import py_trees

class LLMAction(py_trees.behaviour.Behaviour):
    def __init__(self, name, llm_client, command):
        super().__init__(name)
        self.llm_client = llm_client
        self.command = command
        self.response = None

    def initialise(self):
        self.response = self.llm_client.parse_with_llm(self.command)

    def update(self):
        if self.response:
            # Parse and execute the LLM response
            result = self.execute_llm_plan(self.response)
            if result == "success":
                return py_trees.common.Status.SUCCESS
            elif result == "running":
                return py_trees.common.Status.RUNNING
            else:
                return py_trees.common.Status.FAILURE
        return py_trees.common.Status.FAILURE

    def execute_llm_plan(self, plan):
        # Execute the plan and return status
        pass
```

## Best Practices for LLM-ROS Integration

- **Provide context**: Include robot capabilities, constraints, and environment state
- **Use structured output**: Require JSON or other structured formats from LLM
- **Implement validation**: Always validate LLM output before execution
- **Handle uncertainty**: Plan for when the LLM is uncertain or wrong
- **Maintain privacy**: Be careful with sensitive data in prompts
- **Plan for failures**: Have fallback behaviors when LLM plans fail
- **Monitor performance**: Track success rates and refine prompts accordingly