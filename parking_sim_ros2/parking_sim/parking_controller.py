#!/usr/bin/env python3
import math
from enum import Enum

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def clamp(value, low, high):
    return max(low, min(high, value))


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class ParkingState(Enum):
    APPROACH = 1
    ALIGN = 2
    STOPPED = 3


class ParkingController(Node):
    def __init__(self):
        super().__init__('parking_controller')

        self.declare_parameter('target_x', 1.5)
        self.declare_parameter('target_y', 0.0)
        self.declare_parameter('target_yaw', 0.0)

        self.target_x = float(self.get_parameter('target_x').value)
        self.target_y = float(self.get_parameter('target_y').value)
        self.target_yaw = float(self.get_parameter('target_yaw').value)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)

        self.x = None
        self.y = None
        self.yaw = None

        self.state = ParkingState.APPROACH
        self.arrival_distance = 0.18
        self.yaw_tolerance = 0.08
        self.stop_sent = False

        self.get_logger().info(
            f'Parking target set to x={self.target_x:.2f}, y={self.target_y:.2f}, yaw={self.target_yaw:.2f}'
        )

    def odom_callback(self, msg: Odometry):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(siny_cosp, cosy_cosp)

    def publish_stop(self):
        twist = Twist()
        self.cmd_pub.publish(twist)

    def control_loop(self):
        if self.x is None or self.y is None or self.yaw is None:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        heading_to_target = math.atan2(dy, dx)
        heading_error = normalize_angle(heading_to_target - self.yaw)
        final_yaw_error = normalize_angle(self.target_yaw - self.yaw)

        twist = Twist()

        if self.state == ParkingState.APPROACH:
            if distance <= self.arrival_distance:
                self.state = ParkingState.ALIGN
                self.get_logger().info('Reached parking spot. Aligning final orientation.')
                return

            linear_speed = clamp(0.55 * distance, 0.0, 0.18)
            angular_speed = clamp(1.8 * heading_error, -1.5, 1.5)

            if abs(heading_error) > 0.7:
                linear_speed *= 0.25

            twist.linear.x = linear_speed
            twist.angular.z = angular_speed
            self.cmd_pub.publish(twist)
            return

        if self.state == ParkingState.ALIGN:
            if abs(final_yaw_error) <= self.yaw_tolerance:
                self.state = ParkingState.STOPPED
                self.get_logger().info('Parked successfully.')
                self.publish_stop()
                self.stop_sent = True
                return

            twist.angular.z = clamp(1.6 * final_yaw_error, -1.0, 1.0)
            self.cmd_pub.publish(twist)
            return

        if self.state == ParkingState.STOPPED:
            if not self.stop_sent:
                self.publish_stop()
                self.stop_sent = True
            return


def main(args=None):
    rclpy.init(args=args)
    node = ParkingController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
