#!/usr/bin/env python3

"""
Simple Gazebo Controller Node
This example demonstrates basic integration between ROS 2 and Gazebo simulation
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math


class SimpleGazeboController(Node):
    """
    A simple controller that demonstrates basic Gazebo integration with ROS 2
    """

    def __init__(self):
        super().__init__('simple_gazebo_controller')

        # Create publishers for robot control
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Create subscribers for sensor feedback
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Robot state variables
        self.current_scan = None
        self.current_odom = None
        self.obstacle_detected = False
        self.robot_pose = None

        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Simple Gazebo Controller initialized')

    def scan_callback(self, msg):
        """
        Handle laser scan data from Gazebo
        """
        self.current_scan = msg

        # Simple obstacle detection
        if self.current_scan.ranges:
            min_range = min(self.current_scan.ranges)
            self.obstacle_detected = min_range < 1.0  # Obstacle within 1 meter

    def odom_callback(self, msg):
        """
        Handle odometry data from Gazebo
        """
        self.current_odom = msg
        self.robot_pose = msg.pose.pose

    def control_loop(self):
        """
        Main control loop for the robot
        """
        cmd_vel = Twist()

        if self.obstacle_detected:
            # Stop if obstacle detected
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0

            self.get_logger().warn('Obstacle detected! Stopping robot.')
        else:
            # Move forward with slight turning motion
            cmd_vel.linear.x = 0.5  # Forward at 0.5 m/s
            cmd_vel.angular.z = 0.2  # Slow turn

        # Publish velocity command
        self.cmd_vel_pub.publish(cmd_vel)

        # Log robot status
        if self.robot_pose:
            self.get_logger().debug(
                f'Robot position: ({self.robot_pose.position.x:.2f}, '
                f'{self.robot_pose.position.y:.2f}), '
                f'Linear: {cmd_vel.linear.x:.2f}, Angular: {cmd_vel.angular.z:.2f}'
            )


def main(args=None):
    """
    Main function to run the Gazebo controller node
    """
    rclpy.init(args=args)

    controller = SimpleGazeboController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Controller interrupted by user')
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()