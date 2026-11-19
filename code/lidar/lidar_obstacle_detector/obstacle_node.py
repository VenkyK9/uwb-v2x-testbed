# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Worked on the bench: 'critical' when something is close, 'warning' a little further away. No output of the node itself was saved.
# About  : Obstacle node tuned to the A2M12 scan (1800 beams): front/left/right/rear sectors, /obstacle_state and /cmd_vel.
# ----------------------------------------------------------------------------
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class LidarObstacleNode(Node):
    def __init__(self):
        super().__init__('lidar_obstacle_node')

        # ----- Tunable parameters -----
        self.declare_parameter('safe_distance', 0.6)   # meters — tune for your robot size
        self.declare_parameter('warn_distance', 1.0)   # meters — early warning zone
        self.safe_dist = self.get_parameter('safe_distance').value
        self.warn_dist = self.get_parameter('warn_distance').value

        # Your scan has 1800 beams: angle_min=-179°, angle_max=+180°, step=0.2°
        # angle_to_index(deg) = round((deg - (-179)) / 0.2)
        self.angle_min_deg = -179.0
        self.angle_step_deg = 0.1996   # degrees per beam

        # Publisher — obstacle state string
        self.state_pub = self.create_publisher(String, '/obstacle_state', 10)
        # Publisher — velocity command (optional: drives robot)
        self.cmd_pub   = self.create_publisher(Twist,  '/cmd_vel',        10)

        # Subscriber
        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.get_logger().info('LiDAR Obstacle Node started. Listening to /scan ...')

    def angle_to_index(self, angle_deg, n_beams):
        idx = round((angle_deg - self.angle_min_deg) / self.angle_step_deg)
        return max(0, min(idx, n_beams - 1))

    def sector_min(self, ranges, start_deg, end_deg):
        """Return minimum valid range (m) in angular sector [start_deg, end_deg]."""
        n = len(ranges)
        i1 = self.angle_to_index(start_deg, n)
        i2 = self.angle_to_index(end_deg,   n)
        vals = [
            ranges[i] for i in range(i1, i2 + 1)
            if not math.isinf(ranges[i]) and not math.isnan(ranges[i])
            and ranges[i] > 0.01   # ignore zero (no return)
        ]
        return min(vals) if vals else float('inf')

    def scan_cb(self, msg: LaserScan):
        r = list(msg.ranges)

        # --- Compute minimum distance per sector ---
        front  = self.sector_min(r, -30,  30)   # ±30° ahead
        left   = self.sector_min(r,  30,  90)   # 30–90° left
        right  = self.sector_min(r, -90, -30)   # 30–90° right
        rear   = self.sector_min(r, 150, 180)   # behind (wrap handled below)

        self.get_logger().info(
            f'F={front:.2f}m  L={left:.2f}m  R={right:.2f}m  B={rear:.2f}m'
        )

        # --- Decide obstacle state ---
        state_msg = String()

        if front < self.safe_dist:
            state_msg.data = 'OBSTACLE_FRONT_CRITICAL'
        elif front < self.warn_dist:
            state_msg.data = 'OBSTACLE_FRONT_WARNING'
        elif left < self.safe_dist:
            state_msg.data = 'OBSTACLE_LEFT'
        elif right < self.safe_dist:
            state_msg.data = 'OBSTACLE_RIGHT'
        else:
            state_msg.data = 'CLEAR'

        self.state_pub.publish(state_msg)

        # --- Generate velocity command ---
        cmd = Twist()
        if state_msg.data == 'OBSTACLE_FRONT_CRITICAL':
            cmd.linear.x  = 0.0
            # Rotate toward the side with more clearance
            cmd.angular.z = 0.4 if left > right else -0.4
        elif state_msg.data == 'OBSTACLE_FRONT_WARNING':
            cmd.linear.x  = 0.05   # slow down
            cmd.angular.z = 0.2 if left > right else -0.2
        else:
            cmd.linear.x  = 0.2    # forward
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
