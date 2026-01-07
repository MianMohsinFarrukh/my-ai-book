#!/usr/bin/env python3

"""
ROS 2 Node Communication Patterns Demo
This script demonstrates various communication patterns in ROS 2 including topics, services, and parameters.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy
from std_msgs.msg import String
from example_interfaces.srv import AddTwoInts, SetBool
from example_interfaces.msg import Float64
import time
from datetime import datetime


class CommunicationDemoNode(Node):
    """
    Demonstrates various ROS 2 communication patterns in a single node
    """

    def __init__(self):
        super().__init__('communication_demo_node')

        # Create different QoS profiles for different communication needs
        self.reliable_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE
        )

        self.best_effort_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )

        # Publishers for different types of data
        self.status_publisher = self.create_publisher(String, 'demo_status', self.reliable_qos)
        self.sensor_publisher = self.create_publisher(Float64, 'demo_sensor', self.best_effort_qos)

        # Subscriber
        self.command_subscriber = self.create_subscription(
            String,
            'demo_commands',
            self.command_callback,
            self.reliable_qos
        )

        # Service server
        self.calculation_service = self.create_service(
            AddTwoInts,
            'demo_calculation_service',
            self.calculation_service_callback
        )

        # Service client
        self.calculation_client = self.create_client(AddTwoInts, 'demo_calculation_service')

        # Timer for periodic publishing
        self.demo_timer = self.create_timer(1.0, self.demo_timer_callback)

        # Variables for tracking state
        self.message_counter = 0
        self.service_counter = 0
        self.is_active = True

        self.get_logger().info('Communication Demo Node initialized')

    def command_callback(self, msg):
        """
        Handle incoming command messages
        """
        self.get_logger().info(f'Received command: {msg.data}')

        # Process different types of commands
        if 'toggle' in msg.data.lower():
            self.is_active = not self.is_active
            status_msg = String()
            status_msg.data = f'Node toggled to: {self.is_active}'
            self.status_publisher.publish(status_msg)
        elif 'calculate' in msg.data.lower():
            # Call service to perform calculation
            self.call_calculation_service(5, 3)

    def calculation_service_callback(self, request, response):
        """
        Handle calculation service requests
        """
        self.service_counter += 1
        result = request.a + request.b

        response.sum = result
        self.get_logger().info(
            f'Calculation service #{self.service_counter}: {request.a} + {request.b} = {result}'
        )

        # Publish result as sensor data
        sensor_msg = Float64()
        sensor_msg.data = float(result)
        self.sensor_publisher.publish(sensor_msg)

        return response

    def call_calculation_service(self, a, b):
        """
        Call the calculation service to perform addition
        """
        while not self.calculation_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Calculation service not available, waiting...')

        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        future = self.calculation_client.call_async(request)
        future.add_done_callback(self.service_call_callback)

    def service_call_callback(self, future):
        """
        Handle the response from the service call
        """
        try:
            response = future.result()
            self.get_logger().info(f'Service call result: {response.sum}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

    def demo_timer_callback(self):
        """
        Periodic callback for demonstration purposes
        """
        if self.is_active:
            # Publish status message
            status_msg = String()
            status_msg.data = f'Demo status message #{self.message_counter} at {datetime.now().strftime("%H:%M:%S")}'
            self.status_publisher.publish(status_msg)

            # Publish sensor data
            sensor_msg = Float64()
            sensor_msg.data = float(self.message_counter * 1.5)
            self.sensor_publisher.publish(sensor_msg)

            self.message_counter += 1

            self.get_logger().debug(f'Published status and sensor data (counter: {self.message_counter})')

    def get_communication_stats(self):
        """
        Get statistics about communication patterns
        """
        return {
            'messages_published': self.message_counter,
            'services_called': self.service_counter,
            'is_active': self.is_active,
            'timestamp': datetime.now().isoformat()
        }


class CommandPublisherNode(Node):
    """
    Companion node that publishes commands to demonstrate communication
    """

    def __init__(self):
        super().__init__('command_publisher_node')

        self.command_publisher = self.create_publisher(String, 'demo_commands', 10)

        # Timer to send commands periodically
        self.command_timer = self.create_timer(2.0, self.send_commands)

        self.command_sequence = [
            'toggle',
            'calculate',
            'status_check',
            'toggle'
        ]
        self.command_index = 0

        self.get_logger().info('Command Publisher Node initialized')

    def send_commands(self):
        """
        Send commands in sequence
        """
        if self.command_index < len(self.command_sequence):
            command = self.command_sequence[self.command_index]
            cmd_msg = String()
            cmd_msg.data = f'{command} command'
            self.command_publisher.publish(cmd_msg)

            self.get_logger().info(f'Sent command: {cmd_msg.data}')
            self.command_index += 1
        else:
            # Reset sequence after completion
            self.command_index = 0


def main(args=None):
    """
    Main function to run the communication patterns demonstration
    """
    rclpy.init(args=args)

    try:
        # Create nodes
        demo_node = CommunicationDemoNode()
        command_node = CommandPublisherNode()

        # Create executor to handle multiple nodes
        executor = rclpy.executors.MultiThreadedExecutor()
        executor.add_node(demo_node)
        executor.add_node(command_node)

        # Start spinning
        executor.spin()

    except KeyboardInterrupt:
        print('Communication demo interrupted by user')
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
    finally:
        # Cleanup
        if 'demo_node' in locals():
            demo_node.destroy_node()
        if 'command_node' in locals():
            command_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()