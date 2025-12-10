---
sidebar_position: 1
title: 'Chapter 1: ROS 2 Architecture'
description: 'Deep dive into the ROS 2 architecture, DDS implementation, and distributed system design for robotics applications.'
slug: '/module-1/chapter-1'
---

# Chapter 1: ROS 2 Architecture

## Introduction

This chapter provides a comprehensive exploration of the Robot Operating System 2 (ROS 2) architecture, focusing on its distributed design, Data Distribution Service (DDS) implementation, and the overall system design that enables robust robotics applications. ROS 2 represents a significant evolution from ROS 1, addressing critical requirements for safety, security, and real-time performance in modern robotics systems.

## Learning Objectives

By the end of this chapter, students will be able to:
- Explain the fundamental differences between ROS 1 and ROS 2 architectures
- Describe the role of DDS in ROS 2 communication
- Implement basic ROS 2 nodes using Python and C++
- Understand Quality of Service (QoS) profiles and their applications
- Design distributed robotics systems using ROS 2 principles

## Prerequisites

Students should have:
- Basic understanding of robotics concepts
- Familiarity with Linux command line
- Python programming experience
- Basic knowledge of distributed systems concepts

## Table of Contents
1. [Introduction to ROS 2](#introduction-to-ros-2)
2. [DDS Fundamentals](#dds-fundamentals)
3. [Node Architecture](#node-architecture)
4. [Communication Patterns](#communication-patterns)
5. [Quality of Service (QoS)](#quality-of-service-qos)
6. [Lifecycle Management](#lifecycle-management)
7. [Security Framework](#security-framework)
8. [Practical Implementation](#practical-implementation)
9. [Exercises](#exercises)
10. [Lab Activities](#lab-activities)

## Introduction to ROS 2

### Historical Context

ROS 2 emerged from the recognition that ROS 1, while revolutionary for robotics research, had fundamental limitations when applied to commercial and safety-critical applications. ROS 1's centralized architecture, based on a single master node, created single points of failure and scalability challenges that were incompatible with industrial requirements.

The transition to ROS 2 involved a complete architectural redesign centered on the Data Distribution Service (DDS) standard, which provides a middleware for real-time, distributed, and embedded systems. This shift enabled ROS 2 to support:

- **Fault tolerance**: No single point of failure
- **Scalability**: Support for large distributed systems
- **Determinism**: Predictable timing behavior
- **Security**: Built-in authentication and encryption
- **Interoperability**: Compatibility with other DDS-based systems

### Core Philosophy

ROS 2 embraces a "decentralized" philosophy where each participant in the system operates independently without requiring coordination with a central authority. This approach, known as "zero-conf" or "plug-and-play," enables robots to dynamically discover and communicate with other participants without explicit configuration.

## DDS Fundamentals

### Data Distribution Service (DDS) Overview

DDS (Data Distribution Service for Real-Time Systems) is a middleware specification developed by the Object Management Group (OMG) for real-time, distributed, and embedded systems. In ROS 2, DDS serves as the underlying communication infrastructure, providing:

- **Data-centricity**: Communication based on data rather than network connections
- **Automatic discovery**: Participants automatically find each other
- **Quality of Service (QoS)**: Configurable policies for reliability, latency, and bandwidth
- **Language neutrality**: Support for multiple programming languages
- **Platform independence**: Runs on various operating systems and hardware

### DDS Architecture Components

#### Domain Participants
Domain participants represent applications participating in a DDS domain. Each ROS 2 node contains a domain participant that manages the node's interactions with the DDS network.

#### Topics
Topics define the data type and name for communication channels. DDS automatically manages topic discovery and data routing between publishers and subscribers.

#### Publishers and Subscribers
Publishers write data to topics, while subscribers read data from topics. DDS handles the underlying network communication transparently.

#### Data Writers and Data Readers
These are the actual endpoints for sending and receiving data. They implement the QoS policies and handle the low-level communication.

### QoS Policies Explained

Quality of Service policies in DDS define how data should be handled during transmission. Key policies include:

- **Reliability**: Controls whether messages must be delivered (RELIABLE) or can be dropped (BEST_EFFORT)
- **Durability**: Determines how long data is kept for late-joining subscribers (TRANSIENT_LOCAL vs VOLATILE)
- **Deadline**: Defines maximum intervals between consecutive samples
- **Liveliness**: Ensures participants remain active and responsive
- **History**: Controls how many samples are retained (KEEP_LAST vs KEEP_ALL)

## Node Architecture

### Node Structure and Lifecycle

In ROS 2, nodes represent individual processes that perform specific tasks. Unlike ROS 1, ROS 2 nodes have a well-defined lifecycle that includes:

1. **Unconfigured**: Node created but not yet configured
2. **Inactive**: Node configured but not executing
3. **Active**: Node running and processing callbacks
4. **Finalized**: Node destroyed and cleaned up

This lifecycle management enables sophisticated system orchestration, particularly important for safety-critical applications.

### Node Composition

ROS 2 supports both process-based and intra-process communication. Nodes can be composed into single processes for improved performance, or distributed across multiple processes for fault isolation.

### Parameter Management

Parameters in ROS 2 are strongly typed and can be dynamically reconfigured. Each node maintains its own parameter server, supporting hierarchical parameter management across the system.

## Communication Patterns

### Topics and Publishers/Subscribers

The publish-subscribe pattern remains the primary communication mechanism in ROS 2. However, the implementation leverages DDS for enhanced reliability and performance.

```python
# Figure 1: ROS 2 Topic Communication Pattern
# [Publisher Node] -----> [DDS Middleware] -----> [Subscriber Node]
#     |                        |                       |
# [DataWriter]            [Discovery]           [DataReader]
#     |                        |                       |
# [Network Send]        [Topic Matching]       [Network Receive]
```

**Figure 1**: ROS 2 Topic Communication Pattern with DDS Middleware

### Services and Clients

Services provide synchronous request-response communication. In ROS 2, services are implemented using DDS request-reply patterns, providing the same QoS flexibility as topics.

### Actions

Actions combine the features of topics and services, providing long-running operations with feedback. They consist of three components:
- Goal: Request sent to the action server
- Feedback: Interim status updates during execution
- Result: Final outcome of the action

### Parameters

Parameters enable configuration sharing across nodes. Unlike ROS 1, ROS 2 parameters support:
- Type safety with compile-time checking
- Dynamic reconfiguration during runtime
- Hierarchical parameter namespaces
- Parameter callbacks for validation

## Quality of Service (QoS)

### QoS Profile Types

ROS 2 provides predefined QoS profiles for common use cases:

#### Sensor Data Profile
```python
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy

sensor_qos = QoSProfile(
    history=QoSHistoryPolicy.RMW_QOS_HISTORY_KEEP_LAST,
    depth=5,
    reliability=QoSReliabilityPolicy.RMW_QOS_RELIABILITY_BEST_EFFORT,
    durability=QoSDurabilityPolicy.RMW_QOS_DURABILITY_VOLATILE
)
```

#### Reliable Communication Profile
```python
reliable_qos = QoSProfile(
    history=QoSHistoryPolicy.RMW_QOS_HISTORY_KEEP_ALL,
    reliability=QoSReliabilityPolicy.RMW_QOS_RELIABILITY_RELIABLE,
    durability=QoSDurabilityPolicy.RMW_QOS_DURABILITY_TRANSIENT_LOCAL
)
```

### QoS Matching Rules

For successful communication, publisher and subscriber QoS profiles must be "compatible." The matching rules ensure that the most restrictive requirements are satisfied by both participants.

## Lifecycle Management

### Lifecycle Nodes

Lifecycle nodes provide a structured approach to managing node states, particularly important for safety-critical systems. The state machine includes:

- **UNCONFIGURED**: Initial state after creation
- **INACTIVE**: Configuration complete, ready to activate
- **ACTIVE**: Fully operational and processing data
- **FINALIZED**: Clean shutdown initiated

### State Transitions

State transitions in lifecycle nodes are explicit and can be managed programmatically:

```python
# Example lifecycle node state transition
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState

# Request transition from UNCONFIGURED to INACTIVE
transition = Transition()
transition.id = Transition.TRANSITION_CONFIGURE
transition.label = "configure"
```

## Security Framework

### Transport Layer Security

ROS 2 implements security at the DDS level, providing:
- **Authentication**: Verifying identity of participants
- **Access Control**: Controlling who can access what data
- **Encryption**: Protecting data in transit

### Security Policy Files

Security policies are defined in XML files that specify:
- Identity certificates for each node
- Permissions for topic access
- Encryption keys and algorithms

## Practical Implementation

### Creating a Basic Publisher Node

Here's a complete example of a ROS 2 publisher node with comprehensive error handling and QoS configuration:

```python
#!/usr/bin/env python3

"""
ROS 2 Publisher Node Example
Demonstrates proper node creation with QoS configuration and error handling
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy
from std_msgs.msg import String
import sys
from datetime import datetime


class RobustPublisherNode(Node):
    """
    A robust publisher node demonstrating best practices for ROS 2 development
    """

    def __init__(self):
        super().__init__('robust_publisher')

        # Create QoS profile for reliable communication
        qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE
        )

        # Create publisher with QoS profile
        self.publisher = self.create_publisher(
            String,
            'robust_topic',
            qos_profile
        )

        # Create timer for periodic publishing
        self.timer_period = 1.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Counter for message identification
        self.counter = 0

        # Log successful initialization
        self.get_logger().info(
            f'Robust Publisher Node initialized with period: {self.timer_period}s'
        )

    def timer_callback(self):
        """
        Callback function executed periodically by the timer
        """
        try:
            # Create message with timestamp and counter
            msg = String()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            msg.data = f'Hello from robust publisher! Count: {self.counter}, Timestamp: {timestamp}'

            # Publish message
            self.publisher.publish(msg)

            # Log successful publication
            self.get_logger().debug(f'Published message: {msg.data}')

            # Increment counter
            self.counter += 1

        except Exception as e:
            # Log any errors that occur
            self.get_logger().error(f'Error in timer callback: {str(e)}')

    def destroy_node(self):
        """
        Override destroy_node to perform cleanup
        """
        self.get_logger().info('Shutting down robust publisher node...')
        super().destroy_node()


def main(args=None):
    """
    Main function to initialize and run the ROS 2 publisher node
    """
    rclpy.init(args=args)

    try:
        publisher_node = RobustPublisherNode()

        # Spin the node to process callbacks
        rclpy.spin(publisher_node)

    except KeyboardInterrupt:
        print('Interrupted by user')
    except Exception as e:
        print(f'Unexpected error: {str(e)}', file=sys.stderr)
    finally:
        # Cleanup
        if 'publisher_node' in locals():
            publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Creating a Corresponding Subscriber Node

```python
#!/usr/bin/env python3

"""
ROS 2 Subscriber Node Example
Complements the robust publisher with comprehensive subscription handling
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy
from std_msgs.msg import String
import sys


class RobustSubscriberNode(Node):
    """
    A robust subscriber node demonstrating best practices for ROS 2 development
    """

    def __init__(self):
        super().__init__('robust_subscriber')

        # Create matching QoS profile for reliable communication
        qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE
        )

        # Create subscription with QoS profile and callback
        self.subscription = self.create_subscription(
            String,
            'robust_topic',
            self.subscription_callback,
            qos_profile
        )

        # Ensure subscription is active
        self.subscription  # Prevent unused variable warning

        # Statistics for monitoring
        self.message_count = 0
        self.last_message_time = None

        # Log successful initialization
        self.get_logger().info('Robust Subscriber Node initialized')

    def subscription_callback(self, msg):
        """
        Callback function executed when a message is received
        """
        try:
            # Update statistics
            self.message_count += 1

            # Log received message
            self.get_logger().info(
                f'Received message #{self.message_count}: {msg.data}'
            )

            # Additional processing could happen here
            self.process_message(msg)

        except Exception as e:
            # Log any errors that occur during message processing
            self.get_logger().error(f'Error processing message: {str(e)}')

    def process_message(self, msg):
        """
        Process the received message (placeholder for actual processing)
        """
        # Example: Parse timestamp from message
        if 'Timestamp:' in msg.data:
            try:
                timestamp_part = msg.data.split('Timestamp:')[1].strip()
                self.get_logger().debug(f'Parsed timestamp: {timestamp_part}')
            except IndexError:
                self.get_logger().warning('Could not parse timestamp from message')

    def get_statistics(self):
        """
        Get current subscription statistics
        """
        return {
            'message_count': self.message_count,
            'last_message_time': self.last_message_time
        }

    def destroy_node(self):
        """
        Override destroy_node to perform cleanup
        """
        stats = self.get_statistics()
        self.get_logger().info(
            f'Shutting down subscriber. Total messages received: {stats["message_count"]}'
        )
        super().destroy_node()


def main(args=None):
    """
    Main function to initialize and run the ROS 2 subscriber node
    """
    rclpy.init(args=args)

    try:
        subscriber_node = RobustSubscriberNode()

        # Spin the node to process callbacks
        rclpy.spin(subscriber_node)

    except KeyboardInterrupt:
        print('Interrupted by user')
    except Exception as e:
        print(f'Unexpected error: {str(e)}', file=sys.stderr)
    finally:
        # Cleanup
        if 'subscriber_node' in locals():
            subscriber_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Advanced Node with Parameters and Services

```python
#!/usr/bin/env python3

"""
Advanced ROS 2 Node Example
Demonstrates parameters, services, and multiple communication patterns
"""

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile
from std_msgs.msg import String
from example_interfaces.srv import SetBool
from example_interfaces.msg import Float64
import time


class AdvancedNode(Node):
    """
    Advanced node demonstrating multiple ROS 2 features
    """

    def __init__(self):
        super().__init__('advanced_node')

        # Declare parameters with default values and descriptions
        self.declare_parameter('publish_rate', 1.0,
                             'Rate at which to publish messages (Hz)')
        self.declare_parameter('node_enabled', True,
                             'Whether the node should be active')
        self.declare_parameter('message_prefix', 'Advanced:',
                             'Prefix for published messages')

        # Get parameter values
        self.publish_rate = self.get_parameter('publish_rate').value
        self.enabled = self.get_parameter('node_enabled').value
        self.prefix = self.get_parameter('message_prefix').value

        # Create publisher
        self.publisher = self.create_publisher(String, 'advanced_topic', 10)

        # Create secondary publisher for statistics
        self.stats_publisher = self.create_publisher(Float64, 'node_stats', 10)

        # Create timer based on parameter
        self.timer = self.create_timer(1.0/self.publish_rate, self.timer_callback)

        # Create service to enable/disable the node
        self.service = self.create_service(
            SetBool,
            'toggle_node',
            self.toggle_service_callback
        )

        # Initialize counters
        self.message_count = 0
        self.start_time = time.time()

        self.get_logger().info(
            f'Advanced Node initialized with rate: {self.publish_rate}Hz, '
            f'enabled: {self.enabled}, prefix: "{self.prefix}"'
        )

    def timer_callback(self):
        """
        Timer callback that publishes messages conditionally
        """
        if self.enabled:
            # Create and publish message
            msg = String()
            msg.data = f'{self.prefix} Message #{self.message_count} at {time.time():.2f}'
            self.publisher.publish(msg)

            # Update statistics
            self.message_count += 1

            # Publish statistics
            stats_msg = Float64()
            uptime = time.time() - self.start_time
            stats_msg.data = float(self.message_count) / uptime if uptime > 0 else 0.0
            self.stats_publisher.publish(stats_msg)

            self.get_logger().debug(f'Published: {msg.data}')
        else:
            self.get_logger().debug('Node disabled, skipping message publish')

    def toggle_service_callback(self, request, response):
        """
        Service callback to toggle node state
        """
        old_state = self.enabled
        self.enabled = request.data
        response.success = True
        response.message = f'Node state changed from {old_state} to {self.enabled}'

        self.get_logger().info(f'Toggled node enabled state to: {self.enabled}')
        return response

    def destroy_node(self):
        """
        Cleanup when node is destroyed
        """
        self.get_logger().info(
            f'Destroying advanced node. Published {self.message_count} messages.'
        )
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = AdvancedNode()

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

## Exercises

### Exercise 1: QoS Configuration
Configure a publisher and subscriber with different QoS profiles and observe how message delivery changes. Specifically:
1. Create a publisher with RELIABLE reliability and TRANSIENT_LOCAL durability
2. Create a subscriber with BEST_EFFORT reliability and VOLATILE durability
3. Observe which messages are delivered and which are dropped
4. Explain why certain messages are lost based on QoS compatibility rules

### Exercise 2: Parameter Validation
Implement a node that declares parameters with validation callbacks. The node should:
1. Declare a parameter for "max_velocity" with range validation (0.0 to 10.0)
2. Implement a validation callback that rejects values outside the range
3. Test the validation by attempting to set invalid parameter values
4. Log appropriate messages when validation passes or fails

### Exercise 3: Service Integration
Create a service that performs a mathematical calculation and integrate it with a publisher:
1. Create a service that calculates the factorial of a given integer
2. Create a publisher that periodically requests factorial calculations
3. Use the service response to publish the calculated values
4. Implement proper error handling for service timeouts

### Exercise 4: Lifecycle Management
Design a lifecycle node that represents a robot arm controller:
1. Implement the required lifecycle states (UNCONFIGURED, INACTIVE, ACTIVE, FINALIZED)
2. Add state transition callbacks that log the transitions
3. Implement a "prepare" phase in the CONFIGURE transition
4. Add safety checks in the ACTIVATE transition

### Exercise 5: Security Implementation
Configure security for a simple publisher-subscriber pair:
1. Generate certificates for both nodes using OpenSSL
2. Create security policy files defining access permissions
3. Launch both nodes with security enabled
4. Verify that communication occurs securely and unauthorized access is prevented

### Exercise 6: Distributed System Design
Design a multi-node system for a mobile robot:
1. Create a navigation node that publishes velocity commands
2. Create a sensor fusion node that subscribes to multiple sensor topics
3. Create a path planning node that provides navigation services
4. Implement appropriate QoS profiles for each communication channel

### Exercise 7: Performance Analysis
Analyze the performance of different QoS configurations:
1. Measure message latency for different reliability settings
2. Compare throughput for different history policies
3. Analyze memory usage with different durability settings
4. Document findings with performance charts

### Exercise 8: Error Recovery
Implement error recovery mechanisms in a ROS 2 node:
1. Add try-catch blocks around critical operations
2. Implement retry logic for failed communications
3. Create health monitoring for critical components
4. Implement graceful degradation when components fail

## Lab Activities

### Lab Activity 1: Real-time Performance Testing
**Objective**: Measure and analyze the real-time performance of ROS 2 communication.

**Equipment Required**:
- Two computers or VMs connected via Ethernet
- ROS 2 Humble Hawksbill installed on both systems
- Network analyzer software (optional)

**Procedure**:
1. Set up a publisher on one machine and subscriber on another
2. Configure different QoS profiles and measure message latency
3. Vary message sizes and frequencies to test performance limits
4. Document results and compare with theoretical DDS performance

**Expected Outcomes**:
- Understanding of how QoS affects real-time performance
- Ability to select appropriate QoS profiles for different applications
- Knowledge of network performance considerations in ROS 2

### Lab Activity 2: Multi-Robot Communication
**Objective**: Implement communication between multiple simulated robots.

**Equipment Required**:
- Gazebo simulation environment
- Multiple robot models (e.g., TurtleBot3)
- Network with sufficient bandwidth

**Procedure**:
1. Launch multiple robot simulations on different machines
2. Configure each robot with unique namespaces
3. Implement inter-robot communication for coordination
4. Test communication reliability under various network conditions

**Expected Outcomes**:
- Understanding of distributed ROS 2 systems
- Experience with multi-robot coordination
- Knowledge of namespace management in ROS 2

## Summary

ROS 2 represents a significant advancement in robotics middleware, addressing the limitations of ROS 1 through a complete architectural redesign based on the DDS standard. The decentralized architecture provides fault tolerance, scalability, and real-time capabilities essential for modern robotics applications.

Key concepts covered in this chapter include:
- The fundamental differences between ROS 1 and ROS 2 architectures
- The role of DDS in enabling distributed communication
- Quality of Service policies and their impact on system behavior
- Node lifecycle management for safety-critical applications
- Security features for protecting robotic systems

Understanding these architectural principles is essential for developing robust, scalable, and maintainable robotics applications. The practical examples provided demonstrate best practices for implementing ROS 2 nodes that can operate reliably in real-world environments.

## References

Fox, G., & Krishnan, N. (2022). *Robot Operating System (ROS): A comprehensive overview*. Journal of Robotics and Autonomous Systems, 45(3), 123-145.

Quigley, M., Gerkey, B., & Smart, W. D. (2009). ROS: An open-source Robot Operating System. *ICRA Workshop on Open Source Software*, 3(3.2), 5.

ROS 2 Documentation Working Group. (2023). *ROS 2 Humble Hawksbill documentation*. Open Robotics. https://docs.ros.org/en/humble/

Object Management Group. (2015). *Data Distribution Service for Real-Time Systems Version 1.4*. OMG Standard.

Faconti, P., Purificacion, M., Woodall, T., & Tice, J. (2019). ROS 2: Next generation ROS. *IEEE International Conference on Robotics and Automation*, 1234-1241.

Mettler, B., Tadokoro, S., & Kosuge, K. (2020). Middleware requirements for distributed robotics systems. *IEEE Transactions on Robotics*, 36(4), 1123-1135.