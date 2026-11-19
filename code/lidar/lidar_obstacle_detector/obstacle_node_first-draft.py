# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Superseded by the tuned node.
# About  : First draft that derives sector indices from angle_min / angle_increment.
# ----------------------------------------------------------------------------
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class LidarObstacleNode(Node):
    def __init__(self):
        super().__init__('lidar_obstacle_node')

        # Parameters
        self.declare_parameter('safe_distance', 0.5)
        self.safe_distance = self.get_parameter('safe_distance').get_parameter_value().double_value

        # Subscribers / publishers
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def scan_callback(self, msg: LaserScan):
        ranges = list(msg.ranges)

        # Filter invalid values
        valid_ranges = [r for r in ranges if not math.isinf(r) and not math.isnan(r)]
        if not valid_ranges:
            return

        # Compute indices for sectors based on angles
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        n = len(ranges)

        def angle_to_index(angle_rad):
            return int((angle_rad - angle_min) / angle_increment)

        # Define sectors (in radians): front ±30°, left 30°–90°, right -90°–-30°
        front_left_idx = angle_to_index(math.radians(30.0))
        front_right_idx = angle_to_index(math.radians(-30.0))
        left_idx = angle_to_index(math.radians(90.0))
        right_idx = angle_to_index(math.radians(-90.0))

        # Normalize indices to array bounds
        front_indices = range(max(0, min(front_right_idx, front_left_idx)),
                              min(n, max(front_right_idx, front_left_idx)))
        left_indices = range(max(0, min(front_left_idx, left_idx)),
                             min(n, max(front_left_idx, left_idx)))
        right_indices = range(max(0, min(right_idx, front_right_idx)),
                              min(n, max(right_idx, front_right_idx)))

        def min_range(indices):
            vals = [ranges[i] for i in indices
                    if not math.isinf(ranges[i]) and not math.isnan(ranges[i])]
            return min(vals) if vals else float('inf')

        min_front = min_range(front_indices)
        min_left = min_range(left_indices)
        min_right = min_range(right_indices)

        self.get_logger().debug(
            f'min_front={min_front:.2f}, min_left={min_left:.2f}, min_right={min_right:.2f}'
        )

        # Basic avoidance: stop & rotate if obstacle in front
        cmd = Twist()
        if min_front < self.safe_distance:
            cmd.linear.x = 0.0
            # rotate left or right depending on side clearance
            if min_left > min_right:
                cmd.angular.z = 0.5
            else:
                cmd.angular.z = -0.5
        else:
            cmd.linear.x = 0.2
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = LidarObstacleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
