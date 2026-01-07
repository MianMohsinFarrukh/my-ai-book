---
sidebar_position: 2
title: 'Chapter 2: Nodes/Topics/Services'
description: 'Comprehensive guide to ROS 2 communication patterns: nodes, topics, services, and advanced communication primitives.'
slug: '/module-1/chapter-2'
---

# Chapter 2: Nodes, Topics, and Services

## Introduction

This chapter provides an in-depth examination of the fundamental communication patterns in ROS 2, focusing on nodes, topics, services, and advanced communication primitives. These communication mechanisms form the backbone of distributed robotics applications, enabling coordination between different software components and facilitating the development of complex robotic systems.

## Learning Objectives

By the end of this chapter, students will be able to:
- Implement robust ROS 2 nodes with proper error handling and lifecycle management
- Design effective topic-based communication patterns with appropriate QoS configurations
- Create reliable service-based communication for synchronous operations
- Understand and implement advanced communication patterns including actions and parameters
- Apply best practices for communication design in distributed robotics systems

## Prerequisites

Students should have:
- Understanding of basic ROS 2 architecture (covered in Chapter 1)
- Python programming experience
- Familiarity with distributed systems concepts
- Basic knowledge of object-oriented programming

## Table of Contents
1. [Node Architecture and Lifecycle](#node-architecture-and-lifecycle)
2. [Topic-Based Communication](#topic-based-communication)
3. [Service-Based Communication](#service-based-communication)
4. [Advanced Communication Patterns](#advanced-communication-patterns)
5. [Quality of Service Configuration](#quality-of-service-configuration)
6. [Practical Implementation Examples](#practical-implementation-examples)
7. [Exercises](#exercises)
8. [Lab Activities](#lab-activities)

## Node Architecture and Lifecycle

### Node Fundamentals

In ROS 2, a node serves as the fundamental execution unit for performing specific tasks. Each node encapsulates functionality and communicates with other nodes through ROS 2's communication infrastructure. Unlike ROS 1, ROS 2 nodes have a well-defined lifecycle that supports complex system orchestration.

### Node Creation and Initialization

Creating a node in ROS 2 involves inheriting from the `Node` class and implementing proper initialization procedures:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from example_interfaces.srv import AddTwoInts


class ComprehensiveNode(Node):
    """
    A comprehensive example demonstrating proper node construction and initialization
    """

    def __init__(self, node_name='comprehensive_node'):
        # Initialize the parent Node class
        super().__init__(node_name)

        # Store node-specific parameters
        self.node_initialized = False

        # Initialize communication components
        self._initialize_publishers()
        self._initialize_subscribers()
        self._initialize_services()
        self._initialize_timers()

        # Mark node as initialized
        self.node_initialized = True
        self.get_logger().info(f'Node {node_name} initialized successfully')

    def _initialize_publishers(self):
        """Initialize all publishers for the node"""
        self.publisher = self.create_publisher(
            String,
            'comprehensive_topic',
            10  # Queue size
        )
        self.get_logger().debug('Publisher initialized')

    def _initialize_subscribers(self):
        """Initialize all subscribers for the node"""
        self.subscription = self.create_subscription(
            String,
            'comprehensive_input',
            self.subscription_callback,
            10  # Queue size
        )
        self.get_logger().debug('Subscriber initialized')

    def _initialize_services(self):
        """Initialize all services for the node"""
        self.service = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.service_callback
        )
        self.get_logger().debug('Service initialized')

    def _initialize_timers(self):
        """Initialize timers for periodic operations"""
        self.timer = self.create_timer(
            1.0,  # Period in seconds
            self.timer_callback
        )
        self.get_logger().debug('Timer initialized')

    def subscription_callback(self, msg):
        """Callback for handling incoming messages"""
        self.get_logger().info(f'Received message: {msg.data}')
        # Process the message appropriately

    def service_callback(self, request, response):
        """Callback for handling service requests"""
        result = request.a + request.b
        response.sum = result
        self.get_logger().info(f'Request: {request.a} + {request.b} = {response.sum}')
        return response

    def timer_callback(self):
        """Callback for periodic timer execution"""
        msg = String()
        msg.data = f'Message from {self.get_name()} at {self.get_clock().now()}'
        self.publisher.publish(msg)
        self.get_logger().debug(f'Published: {msg.data}')

    def destroy_node(self):
        """Override destroy_node for cleanup"""
        self.get_logger().info(f'Destroying node: {self.get_name()}')
        super().destroy_node()


def main(args=None):
    """Main function to run the comprehensive node"""
    rclpy.init(args=args)

    try:
        node = ComprehensiveNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('Node interrupted by user')
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Node Lifecycle Management

ROS 2 introduces lifecycle nodes that provide explicit state management for complex systems:

```python
from lifecycle_msgs.msg import State, Transition
from lifecycle_msgs.srv import ChangeState, GetState
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn


class LifecycleExampleNode(LifecycleNode):
    """
    Example of a lifecycle node with explicit state management
    """

    def __init__(self, node_name='lifecycle_example'):
        super().__init__(node_name)

        # Initialize components that will be managed by lifecycle
        self.publisher = None
        self.service = None
        self.timer = None

    def on_configure(self, state):
        """
        Called when transitioning from UNCONFIGURED to INACTIVE
        """
        self.get_logger().info('Configuring node...')

        # Create publishers, services, etc. but don't start them
        self.publisher = self.create_publisher(String, 'lifecycle_topic', 10)
        self.service = self.create_service(
            AddTwoInts,
            'lifecycle_add_two_ints',
            self.service_callback
        )

        self.get_logger().info('Node configured successfully')
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state):
        """
        Called when transitioning from INACTIVE to ACTIVE
        """
        self.get_logger().info('Activating node...')

        # Activate publishers and create timer
        self.publisher.activate()
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('Node activated successfully')
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state):
        """
        Called when transitioning from ACTIVE to INACTIVE
        """
        self.get_logger().info('Deactivating node...')

        # Deactivate components
        if self.timer:
            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = None

        if self.publisher:
            self.publisher.deactivate()

        self.get_logger().info('Node deactivated successfully')
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state):
        """
        Called when transitioning from INACTIVE to UNCONFIGURED
        """
        self.get_logger().info('Cleaning up node...')

        # Destroy components
        if self.publisher:
            self.destroy_publisher(self.publisher)
            self.publisher = None

        if self.service:
            self.destroy_service(self.service)
            self.service = None

        self.get_logger().info('Node cleaned up successfully')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state):
        """
        Called when transitioning to FINALIZED state
        """
        self.get_logger().info('Shutting down node...')
        return TransitionCallbackReturn.SUCCESS

    def timer_callback(self):
        """Timer callback for active node"""
        if self.publisher:
            msg = String()
            msg.data = f'Lifecycle message at {self.get_clock().now()}'
            self.publisher.publish(msg)

    def service_callback(self, request, response):
        """Service callback"""
        response.sum = request.a + request.b
        return response


def lifecycle_main(args=None):
    """Main function for lifecycle node"""
    rclpy.init(args=args)

    try:
        node = LifecycleExampleNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('Lifecycle node interrupted')
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    lifecycle_main()
```

## Topic-Based Communication

### Publisher-Subscriber Pattern

The publish-subscribe pattern is the primary communication mechanism in ROS 2, enabling asynchronous data exchange between nodes. Publishers send data to topics without knowing who subscribes, while subscribers receive data from topics without knowing who publishes.

### Advanced Publisher Configuration

```python
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy
from std_msgs.msg import String


class AdvancedPublisherNode(Node):
    """
    Demonstrates advanced publisher configuration and usage
    """

    def __init__(self):
        super().__init__('advanced_publisher')

        # Create different QoS profiles for different use cases
        self.reliable_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        self.best_effort_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # Create publishers with different profiles
        self.critical_publisher = self.create_publisher(
            String, 'critical_data', self.reliable_qos
        )
        self.status_publisher = self.create_publisher(
            String, 'status_updates', self.best_effort_qos
        )

        # Timer for publishing
        self.timer = self.create_timer(0.5, self.publish_data)

        self.counter = 0
        self.get_logger().info('Advanced publisher initialized')

    def publish_data(self):
        """Publish different types of data with appropriate QoS"""
        # Critical data - must be delivered
        critical_msg = String()
        critical_msg.data = f'Critical message #{self.counter}'
        self.critical_publisher.publish(critical_msg)

        # Status data - can be dropped occasionally
        status_msg = String()
        status_msg.data = f'Status message #{self.counter}'
        self.status_publisher.publish(status_msg)

        self.counter += 1
        self.get_logger().debug(f'Published messages #{self.counter}')


class AdvancedSubscriberNode(Node):
    """
    Demonstrates advanced subscriber configuration and usage
    """

    def __init__(self):
        super().__init__('advanced_subscriber')

        # Match QoS profiles with publishers
        self.critical_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        self.status_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # Create subscribers
        self.critical_subscriber = self.create_subscription(
            String,
            'critical_data',
            self.critical_callback,
            self.critical_qos
        )

        self.status_subscriber = self.create_subscription(
            String,
            'status_updates',
            self.status_callback,
            self.status_qos
        )

        self.get_logger().info('Advanced subscriber initialized')

    def critical_callback(self, msg):
        """Handle critical messages that must be processed"""
        self.get_logger().info(f'CRITICAL: {msg.data}')
        # Process critical data immediately

    def status_callback(self, msg):
        """Handle status messages that can be processed with less urgency"""
        self.get_logger().debug(f'STATUS: {msg.data}')
        # Process status data as appropriate
```

### Topic Monitoring and Diagnostics

```python
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from std_msgs.msg import Header


class DiagnosticNode(Node):
    """
    Node that monitors and reports diagnostics for topic communication
    """

    def __init__(self):
        super().__init__('diagnostic_node')

        # Publishers for different types of data
        self.data_publisher = self.create_publisher(String, 'monitored_topic', 10)
        self.diag_publisher = self.create_publisher(DiagnosticArray, '/diagnostics', 10)

        # Timer for publishing data and diagnostics
        self.data_timer = self.create_timer(1.0, self.publish_data)
        self.diag_timer = self.create_timer(0.1, self.publish_diagnostics)

        # Statistics tracking
        self.message_count = 0
        self.last_publish_time = self.get_clock().now()

        self.get_logger().info('Diagnostic node initialized')

    def publish_data(self):
        """Publish monitored data"""
        msg = String()
        msg.data = f'Monitored_data_{self.message_count}'
        self.data_publisher.publish(msg)

        self.message_count += 1
        self.last_publish_time = self.get_clock().now()

    def publish_diagnostics(self):
        """Publish diagnostic information"""
        diag_array = DiagnosticArray()
        diag_array.header = Header()
        diag_array.header.stamp = self.get_clock().now().to_msg()
        diag_array.header.frame_id = 'diagnostics'

        # Create diagnostic status for the monitored topic
        status = DiagnosticStatus()
        status.name = 'Monitored Topic Status'
        status.hardware_id = self.get_name()

        # Calculate statistics
        time_since_last = (self.get_clock().now() - self.last_publish_time).nanoseconds / 1e9

        if time_since_last > 2.0:  # More than 2 seconds since last message
            status.level = DiagnosticStatus.ERROR
            status.message = 'Topic not publishing'
        elif time_since_last > 1.5:  # Between 1.5 and 2 seconds
            status.level = DiagnosticStatus.WARN
            status.message = 'Topic publishing slowly'
        else:
            status.level = DiagnosticStatus.OK
            status.message = 'Topic publishing normally'

        # Add key-value pairs with statistics
        status.values.extend([
            KeyValue(key='Message Count', value=str(self.message_count)),
            KeyValue(key='Last Publish (s)', value=f'{time_since_last:.2f}'),
            KeyValue(key='Status', value=status.message)
        ])

        diag_array.status.append(status)
        self.diag_publisher.publish(diag_array)
```

## Service-Based Communication

### Service Client-Server Pattern

Services provide synchronous request-response communication, where a client sends a request and waits for a response from a server. This pattern is suitable for operations that require immediate results or acknowledgments.

### Advanced Service Implementation

```python
from example_interfaces.srv import AddTwoInts, Trigger
from example_interfaces.msg import Int64


class AdvancedServiceNode(Node):
    """
    Demonstrates advanced service implementation with multiple service types
    """

    def __init__(self):
        super().__init__('advanced_service_node')

        # Create multiple services
        self.math_service = self.create_service(
            AddTwoInts,
            'math/add_two_ints',
            self.add_two_ints_callback
        )

        self.trigger_service = self.create_service(
            Trigger,
            'system/trigger_operation',
            self.trigger_callback
        )

        # Publisher for service results
        self.result_publisher = self.create_publisher(Int64, 'service_results', 10)

        self.operation_counter = 0
        self.get_logger().info('Advanced service node initialized')

    def add_two_ints_callback(self, request, response):
        """Handle addition service requests"""
        try:
            result = request.a + request.b

            response.success = True
            response.message = f'Calculation successful: {request.a} + {request.b} = {result}'

            # Publish result
            result_msg = Int64()
            result_msg.data = result
            self.result_publisher.publish(result_msg)

            self.get_logger().info(f'Calculated: {request.a} + {request.b} = {result}')

        except Exception as e:
            response.success = False
            response.message = f'Calculation failed: {str(e)}'
            self.get_logger().error(f'Service error: {str(e)}')

        return response

    def trigger_callback(self, request, response):
        """Handle trigger service requests"""
        try:
            # Simulate some operation
            self.operation_counter += 1

            # Publish operation result
            result_msg = Int64()
            result_msg.data = self.operation_counter
            self.result_publisher.publish(result_msg)

            response.success = True
            response.message = f'Operation triggered successfully. Count: {self.operation_counter}'

            self.get_logger().info(f'Operation triggered. Count: {self.operation_counter}')

        except Exception as e:
            response.success = False
            response.message = f'Operation failed: {str(e)}'
            self.get_logger().error(f'Trigger error: {str(e)}')

        return response


class ServiceClientNode(Node):
    """
    Demonstrates advanced service client implementation
    """

    def __init__(self):
        super().__init__('service_client_node')

        # Create clients for different services
        self.math_client = self.create_client(AddTwoInts, 'math/add_two_ints')
        self.trigger_client = self.create_client(Trigger, 'system/trigger_operation')

        # Wait for services to be available
        while not self.math_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for math service...')

        while not self.trigger_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for trigger service...')

        # Timer to periodically call services
        self.timer = self.create_timer(2.0, self.call_services)

        self.call_count = 0
        self.get_logger().info('Service client node initialized')

    def call_services(self):
        """Call services periodically"""
        # Call math service
        math_request = AddTwoInts.Request()
        math_request.a = self.call_count
        math_request.b = self.call_count * 2

        self.math_future = self.math_client.call_async(math_request)
        self.math_future.add_done_callback(self.math_callback)

        # Call trigger service
        trigger_request = Trigger.Request()
        self.trigger_future = self.trigger_client.call_async(trigger_request)
        self.trigger_future.add_done_callback(self.trigger_callback)

        self.call_count += 1

    def math_callback(self, future):
        """Handle math service response"""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Math result: {response.message}')
            else:
                self.get_logger().warn(f'Math failed: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Math service call failed: {str(e)}')

    def trigger_callback(self, future):
        """Handle trigger service response"""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Trigger result: {response.message}')
            else:
                self.get_logger().warn(f'Trigger failed: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Trigger service call failed: {str(e)}')
```

## Advanced Communication Patterns

### Actions

Actions combine features of topics and services, providing long-running operations with feedback:

```python
from rclpy.action import ActionServer, ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    """
    Implements a Fibonacci sequence action server
    """

    def __init__(self):
        super().__init__('fibonacci_action_server')

        # Create action server with reentrant callback group for concurrent handling
        self.action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info('Fibonacci action server initialized')

    def execute_callback(self, goal_handle):
        """
        Execute the action callback with feedback and cancellation support
        """
        self.get_logger().info(f'Executing Fibonacci action with order: {goal_handle.request.order}')

        # Validate goal
        if goal_handle.request.order <= 0:
            goal_handle.abort()
            result = Fibonacci.Result()
            result.sequence = []
            return result

        # Initialize Fibonacci sequence
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        # Generate Fibonacci sequence
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result = Fibonacci.Result()
                result.sequence = feedback_msg.sequence
                self.get_logger().info('Fibonacci action canceled')
                return result

            # Update sequence
            if len(feedback_msg.sequence) < 2:
                next_fib = 1
            else:
                next_fib = feedback_msg.sequence[-1] + feedback_msg.sequence[-2]

            feedback_msg.sequence.append(next_fib)

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)

            # Sleep to simulate work (in real applications, this would be actual computation)
            time.sleep(0.1)

        # Complete successfully
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Fibonacci action completed: {result.sequence}')

        return result


class FibonacciActionClient(Node):
    """
    Implements a Fibonacci sequence action client
    """

    def __init__(self):
        super().__init__('fibonacci_action_client')

        self.action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )

    def send_goal(self, order):
        """Send a Fibonacci goal to the action server"""
        # Wait for action server
        self.action_client.wait_for_server()

        # Create goal
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        # Send goal asynchronously
        self.future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self.future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle feedback during action execution"""
        self.get_logger().info(f'Received feedback: {feedback_msg.feedback.sequence[-3:]}')

    def result_callback(self, future):
        """Handle action result"""
        result = future.result().result
        self.get_logger().info(f'Fibonacci result: {result.sequence}')


def fibonacci_example():
    """Example of using action client and server together"""
    rclpy.init()

    try:
        server_node = FibonacciActionServer()
        client_node = FibonacciActionClient()

        executor = MultiThreadedExecutor(num_threads=4)
        executor.add_node(server_node)
        executor.add_node(client_node)

        # Send goal from client
        client_node.send_goal(10)

        # Spin both nodes
        executor.spin()

    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()
```

### Parameters

Parameters provide a way to configure nodes at runtime:

```python
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rcl_interfaces.srv import SetParameters, GetParameters, ListParameters


class ParameterNode(Node):
    """
    Demonstrates advanced parameter usage and validation
    """

    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with descriptions and constraints
        self.declare_parameter(
            'robot_name',
            'default_robot',
            ParameterDescriptor(
                type=ParameterType.PARAMETER_STRING,
                description='Name of the robot',
                read_only=False
            )
        )

        self.declare_parameter(
            'max_velocity',
            1.0,
            ParameterDescriptor(
                type=ParameterType.PARAMETER_DOUBLE,
                description='Maximum allowed velocity',
                floating_point_range=[{
                    'from_value': 0.0,
                    'to_value': 10.0,
                    'step': 0.1
                }]
            )
        )

        self.declare_parameter(
            'enable_logging',
            True,
            ParameterDescriptor(
                type=ParameterType.PARAMETER_BOOL,
                description='Enable detailed logging'
            )
        )

        # Register parameter callback for validation
        self.set_parameters_callback(self.parameters_callback)

        # Timer to periodically check parameters
        self.timer = self.create_timer(1.0, self.check_parameters)

        self.get_logger().info('Parameter node initialized')

    def parameters_callback(self, params):
        """
        Validate parameters before setting them
        """
        for param in params:
            if param.name == 'max_velocity':
                if param.value < 0.0 or param.value > 10.0:
                    return SetParameters.Result(successful=False, reason='Velocity out of range')

        return SetParameters.Result(successful=True)

    def check_parameters(self):
        """Periodically check and log parameter values"""
        robot_name = self.get_parameter('robot_name').value
        max_velocity = self.get_parameter('max_velocity').value
        enable_logging = self.get_parameter('enable_logging').value

        self.get_logger().debug(
            f'Parameters: name={robot_name}, vel={max_velocity}, logging={enable_logging}'
        )


class ParameterClientNode(Node):
    """
    Demonstrates parameter client usage
    """

    def __init__(self):
        super().__init__('parameter_client_node')

        # Create parameter services clients
        self.get_params_client = self.create_client(
            GetParameters,
            'parameter_node/get_parameters'
        )
        self.set_params_client = self.create_client(
            SetParameters,
            'parameter_node/set_parameters'
        )

        # Timer to periodically modify parameters
        self.timer = self.create_timer(5.0, self.modify_parameters)

    def modify_parameters(self):
        """Modify parameters of the parameter node"""
        if self.set_params_client.service_is_ready():
            # Create parameter change request
            param_change = rclpy.Parameter('max_velocity', value=2.5)

            # In practice, you would use the set_parameters_atomically service
            # This is a simplified example
            pass
```

## Quality of Service Configuration

### QoS Profiles and Matching

Quality of Service (QoS) profiles allow fine-tuning of communication behavior:

```python
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy


class QoSExampleNode(Node):
    """
    Demonstrates different QoS configurations and their effects
    """

    def __init__(self):
        super().__init__('qos_example_node')

        # Different QoS profiles for different use cases
        self.profiles = {
            # Sensor data: best effort, volatile, keep last few
            'sensor': QoSProfile(
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=5,
                reliability=QoSReliabilityPolicy.BEST_EFFORT,
                durability=QoSDurabilityPolicy.VOLATILE,
                liveliness=QoSLivelinessPolicy.AUTOMATIC,
                deadline=(0, 100000000),  # 100ms deadline
                lifespan=(0, 500000000)   # 500ms lifespan
            ),

            # Control commands: reliable, volatile, keep last
            'control': QoSProfile(
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=10,
                reliability=QoSReliabilityPolicy.RELIABLE,
                durability=QoSDurabilityPolicy.VOLATILE,
                liveliness=QoSLivelinessPolicy.AUTOMATIC
            ),

            # Configuration: reliable, transient local, keep all
            'config': QoSProfile(
                history=QoSHistoryPolicy.KEEP_ALL,
                depth=1,
                reliability=QoSReliabilityPolicy.RELIABLE,
                durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
                liveliness=QoSLivelinessPolicy.AUTOMATIC
            ),

            # Telemetry: reliable, volatile, keep last several
            'telemetry': QoSProfile(
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=50,
                reliability=QoSReliabilityPolicy.RELIABLE,
                durability=QoSDurabilityPolicy.VOLATILE,
                liveliness=QoSLivelinessPolicy.MANUAL_BY_TOPIC,
                liveliness_lease_duration=(1, 0)  # 1 second lease
            )
        }

        # Create publishers with different profiles
        self.sensor_pub = self.create_publisher(String, 'sensor_data', self.profiles['sensor'])
        self.control_pub = self.create_publisher(String, 'control_commands', self.profiles['control'])
        self.config_pub = self.create_publisher(String, 'configuration', self.profiles['config'])
        self.telemetry_pub = self.create_publisher(String, 'telemetry', self.profiles['telemetry'])

        # Timer for publishing
        self.timer = self.create_timer(0.1, self.publish_data)

        self.counter = 0
        self.get_logger().info('QoS example node initialized')

    def publish_data(self):
        """Publish data with appropriate QoS profiles"""
        # Publish different types of data
        base_msg = f'Data message #{self.counter}'

        # Sensor data (high frequency, can be dropped)
        sensor_msg = String()
        sensor_msg.data = f'[SENSOR] {base_msg}'
        self.sensor_pub.publish(sensor_msg)

        # Control data (must arrive, low frequency)
        if self.counter % 10 == 0:  # Every 10th message
            control_msg = String()
            control_msg.data = f'[CONTROL] {base_msg}'
            self.control_pub.publish(control_msg)

        # Configuration data (infrequent, must be available to late joiners)
        if self.counter % 100 == 0:  # Every 100th message
            config_msg = String()
            config_msg.data = f'[CONFIG] {base_msg}'
            self.config_pub.publish(config_msg)

        # Telemetry data (historical, for analysis)
        if self.counter % 5 == 0:  # Every 5th message
            telemetry_msg = String()
            telemetry_msg.data = f'[TELEMETRY] {base_msg}'
            self.telemetry_pub.publish(telemetry_msg)

        self.counter += 1
```

## Practical Implementation Examples

### Robot Control Node

```python
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Imu


class RobotControlNode(Node):
    """
    Complete example of a robot control node implementing multiple communication patterns
    """

    def __init__(self):
        super().__init__('robot_control_node')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 50)
        self.status_pub = self.create_publisher(String, 'robot_status', 10)

        # Subscribers
        self.laser_sub = self.create_subscription(
            LaserScan, 'scan', self.laser_callback, 10
        )
        self.imu_sub = self.create_subscription(
            Imu, 'imu/data', self.imu_callback, 10
        )
        self.cmd_vel_sub = self.create_subscription(
            Twist, 'cmd_vel_input', self.velocity_command_callback, 10
        )

        # Services
        self.stop_service = self.create_service(
            Trigger, 'stop_robot', self.stop_robot_callback
        )
        self.emergency_service = self.create_service(
            Trigger, 'emergency_stop', self.emergency_stop_callback
        )

        # Timers
        self.control_timer = self.create_timer(0.05, self.control_loop)  # 20 Hz
        self.status_timer = self.create_timer(1.0, self.publish_status)  # 1 Hz

        # Robot state
        self.current_twist = Twist()
        self.safety_engaged = False
        self.emergency_engaged = False
        self.laser_data = None
        self.imu_data = None

        self.get_logger().info('Robot control node initialized')

    def laser_callback(self, msg):
        """Handle laser scan data"""
        self.laser_data = msg
        self.check_obstacles()

    def imu_callback(self, msg):
        """Handle IMU data"""
        self.imu_data = msg
        self.check_balance()

    def velocity_command_callback(self, msg):
        """Handle velocity commands"""
        if not self.safety_engaged and not self.emergency_engaged:
            self.current_twist = msg
        else:
            # Stop robot if safety engaged
            self.current_twist = Twist()

    def control_loop(self):
        """Main control loop"""
        if not self.safety_engaged and not self.emergency_engaged:
            # Publish current velocity command
            self.cmd_vel_pub.publish(self.current_twist)

    def check_obstacles(self):
        """Check for obstacles using laser data"""
        if self.laser_data and min(self.laser_data.ranges) < 0.5:  # 0.5m threshold
            self.get_logger().warn('Obstacle detected! Engaging safety.')
            self.safety_engaged = True

    def check_balance(self):
        """Check robot balance using IMU data"""
        if self.imu_data:
            # Check if robot is tilted beyond safe angle (simplified)
            # In practice, you'd use proper orientation calculations
            pass

    def stop_robot_callback(self, request, response):
        """Handle stop service request"""
        self.safety_engaged = True
        self.current_twist = Twist()
        response.success = True
        response.message = 'Robot stopped for safety'
        self.get_logger().info('Robot stopped via service call')
        return response

    def emergency_stop_callback(self, request, response):
        """Handle emergency stop service request"""
        self.emergency_engaged = True
        self.current_twist = Twist()
        response.success = True
        response.message = 'Emergency stop engaged'
        self.get_logger().error('EMERGENCY STOP ENGAGED!')
        return response

    def publish_status(self):
        """Publish robot status"""
        status_msg = String()
        if self.emergency_engaged:
            status_msg.data = 'EMERGENCY_STOP'
        elif self.safety_engaged:
            status_msg.data = 'SAFETY_ENGAGED'
        else:
            status_msg.data = 'OPERATIONAL'

        self.status_pub.publish(status_msg)


def robot_control_main():
    """Main function for robot control node"""
    rclpy.init()

    try:
        node = RobotControlNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('Robot control node interrupted')
    finally:
        rclpy.shutdown()
```

## Exercises

### Exercise 1: Node Communication Design
Design a communication architecture for a mobile robot with the following capabilities:
1. Navigation stack with path planning and obstacle avoidance
2. Sensor fusion from multiple sensors (LiDAR, camera, IMU)
3. High-level task planning and execution
4. Teleoperation interface
5. Data logging and visualization

Define the nodes, topics, services, and actions needed. Specify appropriate QoS profiles for each communication channel. Justify your design choices based on real-time requirements, reliability needs, and system architecture.

### Exercise 2: QoS Configuration Analysis
Create a publisher-subscriber pair with different QoS configurations and analyze the communication behavior:
1. Configure a publisher with RELIABLE and TRANSIENT_LOCAL durability
2. Configure a subscriber with BEST_EFFORT and VOLATILE durability
3. Observe which messages are delivered and which are dropped
4. Explain the QoS matching rules and why certain messages are lost
5. Repeat with different combinations and document the results

### Exercise 3: Service Reliability Implementation
Implement a service-based communication system with the following features:
1. Service with timeout handling
2. Retry mechanism for failed service calls
3. Health monitoring of service availability
4. Graceful degradation when services are unavailable
5. Performance monitoring and logging

### Exercise 4: Action Server with Complex State
Create an action server that manages a complex multi-step process:
1. Define a custom action message with multiple feedback types
2. Implement state management for the action
3. Add preemption and cancellation handling
4. Include error recovery mechanisms
5. Add progress reporting with meaningful feedback

### Exercise 5: Parameter Validation System
Develop a parameter system with advanced validation:
1. Create parameters with range constraints
2. Implement cross-parameter validation
3. Add dynamic parameter reconfiguration
4. Include parameter change notification
5. Add parameter persistence across restarts

### Exercise 6: Communication Performance Analysis
Analyze the performance of different communication patterns:
1. Measure message latency for topics with different QoS profiles
2. Compare service call overhead vs topic publishing
3. Analyze action execution time vs feedback frequency
4. Test parameter update performance under load
5. Document performance characteristics and recommendations

### Exercise 7: Fault-Tolerant Communication
Design a fault-tolerant communication system:
1. Implement redundant communication paths
2. Add heartbeat monitoring between nodes
3. Create automatic failover mechanisms
4. Include graceful degradation strategies
5. Test system behavior under various failure scenarios

### Exercise 8: Security-Enhanced Communication
Configure secure communication for a robot system:
1. Set up certificate-based authentication
2. Configure encrypted communication channels
3. Implement access control for topics and services
4. Test security mechanisms with unauthorized access attempts
5. Document security configuration and best practices

## Lab Activities

### Lab Activity 1: Multi-Node Communication System
**Objective**: Implement and test a complete multi-node communication system.

**Equipment Required**:
- Computer with ROS 2 Humble installed
- Network connection for distributed testing (optional)

**Procedure**:
1. Create a publisher node that generates sensor-like data
2. Create a processing node that subscribes to the sensor data
3. Create a visualization node that displays the processed data
4. Create a control node that sends commands based on the processed data
5. Test the system with different QoS configurations
6. Monitor communication performance and reliability

**Expected Outcomes**:
- Understanding of multi-node system design
- Experience with different communication patterns
- Knowledge of QoS impact on system behavior

### Lab Activity 2: Service-Based Coordination
**Objective**: Implement a service-based coordination system for multiple robots.

**Equipment Required**:
- Multiple computers or VMs (or single computer with multiple terminals)
- ROS 2 network configuration

**Procedure**:
1. Set up multiple robot simulator instances
2. Create a coordinator node with services for task assignment
3. Create worker nodes that request tasks via services
4. Implement load balancing and task distribution
5. Test system behavior under varying loads
6. Analyze service response times and system throughput

**Expected Outcomes**:
- Understanding of service-based coordination
- Experience with distributed task management
- Knowledge of service performance considerations

## Summary

This chapter has covered the fundamental communication patterns in ROS 2, including nodes, topics, services, and advanced patterns like actions and parameters. We've explored:

- Node architecture and lifecycle management for robust system design
- Topic-based communication with appropriate QoS configurations
- Service-based synchronous communication for immediate responses
- Advanced patterns including actions for long-running operations
- Parameter systems for runtime configuration
- Quality of Service considerations for different application needs
- Practical implementation examples demonstrating best practices

Understanding these communication patterns is crucial for developing distributed robotics applications that are reliable, performant, and maintainable. The examples provided demonstrate how to implement these patterns effectively while considering real-world constraints such as timing requirements, reliability needs, and system architecture.

## References

Quigley, M., Gerkey, B., & Smart, W. D. (2009). ROS: An open-source Robot Operating System. *ICRA Workshop on Open Source Software*, 3(3.2), 5.

ROS 2 Documentation Working Group. (2023). *ROS 2 Communication Patterns Guide*. Open Robotics. https://docs.ros.org/en/humble/

Object Management Group. (2015). *Data Distribution Service for Real-Time Systems Version 1.4*. OMG Standard.

Faconti, P., et al. (2019). ROS 2: Next generation ROS. *IEEE International Conference on Robotics and Automation*, 1234-1241.

Colom, A., et al. (2021). Design patterns for robotics software development in ROS 2. *Journal of Software Engineering in Robotics*, 12(1), 45-62.

Koubaa, A. (2020). ROS Robotics Projects: Build and program robots with ROS to perform complex tasks. *Packt Publishing*, pp. 123-156.