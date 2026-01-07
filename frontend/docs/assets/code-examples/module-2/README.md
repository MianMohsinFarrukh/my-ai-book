# Module 2 Code Examples

This directory contains code examples for Module 2: Simulation Environments (Gazebo & Unity).

## Contents:
- Gazebo world files
- Robot model files (SDF/URDF)
- Simulation controllers and plugins
- Unity integration examples (when applicable)
- ROS 2 launch files for simulation
- Other relevant code examples for the module

## Code Syntax Highlighting Guide

All code examples in this textbook use standard Markdown syntax highlighting. Below are the supported language identifiers:

### XML/SDF Code Blocks
```xml
<!-- This is an SDF model example -->
<sdf version="1.7">
  <world name="simple_world">
    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
            </plane>
          </geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>
```

### Python Code Blocks
```python
# This is a Python code example for Gazebo integration
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class GazeboController(Node):
    def __init__(self):
        super().__init__('gazebo_controller')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
```

### Bash/Shell Code Blocks
```bash
# This is a bash/shell command example for Gazebo
# Launch Gazebo with a specific world
gz sim -r simple_obstacle_course.sdf

# Or using ROS 2 launch
ros2 launch gazebo_ros gazebo.launch.py world:=/path/to/my/world.sdf
```

### C++ Code Blocks
```cpp
// This is a C++ code example for Gazebo plugins
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>

namespace gazebo
{
  class SimpleModelPlugin : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf)
    {
      this->model = _model;
      this->physics = this->model->GetWorld()->Physics();
    }

    private: physics::ModelPtr model;
    private: physics::PhysicsPtr physics;
  };

  GZ_REGISTER_MODEL_PLUGIN(SimpleModelPlugin)
}
```

## Execution Notes for Code Examples

### Prerequisites
- Gazebo Garden or compatible version installed
- ROS 2 Humble with gazebo_ros packages
- Appropriate simulation environment setup
- Robot models and dependencies installed

### Running Gazebo Simulations
1. Source ROS 2 environment: `source /opt/ros/humble/setup.bash`
2. Launch simulation: `ros2 launch gazebo_ros gazebo.launch.py world:=path/to/world.sdf`
3. Spawn robot models: `ros2 run gazebo_ros spawn_entity.py -file path/to/model.sdf -entity robot_name`

### Common Execution Issues and Solutions
- **Physics errors**: Check model collisions and inertial properties
- **Rendering issues**: Verify GPU drivers and graphics settings
- **Connection failures**: Confirm ROS bridge is running and ports are accessible
- **Performance issues**: Reduce scene complexity or adjust physics parameters