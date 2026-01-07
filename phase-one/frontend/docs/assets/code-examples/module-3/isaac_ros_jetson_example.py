#!/usr/bin/env python3

"""
Isaac ROS Jetson Pipeline Example
This demonstrates a basic Isaac ROS pipeline for Jetson platforms
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Twist
from vision_msgs.msg import Detection2DArray
import numpy as np
import cv2
from cv_bridge import CvBridge


class IsaacROSJetsonNode(Node):
    def __init__(self):
        super().__init__('isaac_ros_jetson_node')

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.camera_info_sub = self.create_subscription(
            CameraInfo, 'camera/camera_info', self.camera_info_callback, 10)

        # Create publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.detection_pub = self.create_publisher(
            Detection2DArray, 'detections', 10)

        # Initialize CvBridge for image conversion
        self.bridge = CvBridge()

        # Store camera parameters
        self.camera_matrix = None
        self.dist_coeffs = None

        # Detection parameters
        self.detection_enabled = True

        self.get_logger().info('Isaac ROS Jetson Node initialized')

    def camera_info_callback(self, msg):
        """Callback for camera info messages"""
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k).reshape(3, 3)
            self.dist_coeffs = np.array(msg.d)
            self.get_logger().info('Camera parameters received')

    def image_callback(self, msg):
        """Callback for image messages"""
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Process image for perception tasks
            if self.detection_enabled:
                detections = self.process_image(cv_image)

                # Publish detections
                detection_msg = self.create_detection_message(detections)
                self.detection_pub.publish(detection_msg)

                # Simple navigation based on detections
                self.navigate_based_on_detections(detections)

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def process_image(self, image):
        """Process image for object detection and feature extraction"""
        # Convert to grayscale for feature detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Feature detection using ORB (optimized for Jetson)
        orb = cv2.ORB_create(nfeatures=500, scaleFactor=1.2, nlevels=8)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        # Object detection (example: AprilTag detection)
        # In a real implementation, you would use Isaac ROS AprilTag package
        detections = []
        if keypoints is not None:
            for kp in keypoints[:10]:  # Limit to first 10 keypoints for efficiency
                x, y = int(kp.pt[0]), int(kp.pt[1])
                detections.append({
                    'x': x,
                    'y': y,
                    'size': int(kp.size),
                    'confidence': 0.8
                })

        return detections

    def create_detection_message(self, detections):
        """Create Detection2DArray message from detections"""
        detection_array = Detection2DArray()
        detection_array.header.stamp = self.get_clock().now().to_msg()
        detection_array.header.frame_id = 'camera_frame'

        # In a real implementation, you would populate this with actual detections
        # For this example, we'll just return an empty array
        return detection_array

    def navigate_based_on_detections(self, detections):
        """Simple navigation based on detections"""
        cmd_vel = Twist()

        if len(detections) > 0:
            # Calculate average position of detections
            avg_x = np.mean([det['x'] for det in detections])
            image_width = 640  # Assumed image width

            # Simple proportional controller for navigation
            center_offset = (avg_x - image_width / 2) / (image_width / 2)
            cmd_vel.angular.z = -center_offset * 0.5  # Turn toward object
            cmd_vel.linear.x = 0.2  # Move forward
        else:
            # Stop if no detections
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0

        # Publish velocity command
        self.cmd_vel_pub.publish(cmd_vel)

    def cleanup(self):
        """Cleanup function"""
        self.get_logger().info('Cleaning up Isaac ROS Jetson Node')


def main(args=None):
    rclpy.init(args=args)

    node = IsaacROSJetsonNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted, shutting down...')
    finally:
        node.cleanup()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()