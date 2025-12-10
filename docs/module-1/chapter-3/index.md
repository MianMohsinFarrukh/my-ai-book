---
sidebar_position: 3
title: 'Chapter 3: Humanoid URDF Basics'
---

# Chapter 3: Humanoid URDF Basics

This chapter introduces the Universal Robot Description Format (URDF) and how to create humanoid robot models for simulation and control.

## What is URDF?

URDF (Unified Robot Description Format) is an XML format used to describe robot models in ROS. It contains information about:

- **Links**: Rigid parts of the robot (e.g., base, arms, legs)
- **Joints**: Connections between links (e.g., revolute, prismatic, fixed)
- **Visual**: How the robot appears in simulation
- **Collision**: Collision properties for physics simulation
- **Inertial**: Mass, center of mass, and inertia properties

## URDF Structure

A basic URDF robot description consists of:

- A robot tag with a name
- Multiple link elements describing rigid bodies
- Multiple joint elements describing connections between links
- Optional material, gazebo, and transmission elements

## Basic URDF Example

Here's a simple robot with a base and an arm:

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Arm link -->
  <joint name="arm_joint" type="revolute">
    <parent link="base_link"/>
    <child link="arm_link"/>
    <origin xyz="0.0 0.0 0.2" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10.0" velocity="1.0"/>
  </joint>

  <link name="arm_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>
</robot>
```

You can find this example in the code examples directory as `simple_robot.urdf`.

## Humanoid Robot Considerations

When creating humanoid robot models, consider:

- **Kinematic chains**: Legs, arms, and spine as connected joints
- **Degrees of freedom**: Ensuring sufficient joints for desired movements
- **Balance**: Proper center of mass for stable locomotion
- **Actuator limits**: Realistic joint limits and effort constraints

## URDF Tools

Useful tools for working with URDF:

- **RViz**: Visualize URDF models in ROS
- **Gazebo**: Simulate URDF robots in physics environment
- **xacro**: Macro language to simplify complex URDFs

## Best Practices

- Use consistent naming conventions
- Include proper inertial properties for simulation
- Test your URDF in RViz before simulation
- Use xacro for complex humanoid models to avoid repetition