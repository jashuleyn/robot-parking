import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute
from std_msgs.msg import String
from std_srvs.srv import Empty
import math
import json

PARKING_SPOTS = [
    {"id": 0, "x": 2.0, "y": 8.0, "occupied": True},
    {"id": 1, "x": 5.5, "y": 8.0, "occupied": False},
    {"id": 2, "x": 9.0, "y": 8.0, "occupied": True},
    {"id": 3, "x": 2.0, "y": 2.0, "occupied": False},
    {"id": 4, "x": 5.5, "y": 2.0, "occupied": True},
    {"id": 5, "x": 9.0, "y": 2.0, "occupied": False},
]

START_X = 5.5
START_Y = 5.5


class ParkingSimNode(Node):
    def __init__(self):
        super().__init__("parking_sim")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subscriber = self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
        self.status_publisher = self.create_publisher(String, "/parking_status", 10)
        self.teleport_client = self.create_client(TeleportAbsolute, "/turtle1/teleport_absolute")
        self.clear_client = self.create_client(Empty, "/clear")
        self.pose = None
        self.parked = False
        self.resetting = False
        self.reset_done = False
        self.reset_timer = None
        self.park_count = 0
        self.target = self.find_free_spot()
        self.timer = self.create_timer(0.1, self.drive_to_spot)
        if self.target:
            self.get_logger().info("Run 1: Heading to spot " + str(self.target["id"] + 1))

    def find_free_spot(self):
        for spot in PARKING_SPOTS:
            if not spot["occupied"]:
                return spot
        return None

    def pose_callback(self, msg):
        self.pose = msg
        status = {
            "x": round(msg.x, 2),
            "y": round(msg.y, 2),
            "theta": round(msg.theta, 2),
            "parked": self.parked,
            "resetting": self.resetting,
            "park_count": self.park_count,
            "target": self.target["id"] if self.target else -1,
            "spots": PARKING_SPOTS,
        }
        m = String()
        m.data = json.dumps(status)
        self.status_publisher.publish(m)

    def drive_to_spot(self):
        if self.pose is None or self.resetting:
            return
        if self.parked:
            if not self.reset_done:
                self.reset_done = True
                self.park_count += 1
                self.get_logger().info("Parked! Waiting 2s... total: " + str(self.park_count))
                self.reset_timer = self.create_timer(2.0, self.reset_car)
            return
        if self.target is None:
            self.get_logger().info("All spots occupied! Done.")
            return
        dx = self.target["x"] - self.pose.x
        dy = self.target["y"] - self.pose.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 0.15:
            self.stop()
            self.parked = True
            self.target["occupied"] = True
            self.get_logger().info("Parked at spot " + str(self.target["id"] + 1) + "!")
            return
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.pose.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
        msg = Twist()
        msg.linear.x = min(1.5, distance)
        msg.angular.z = 4.0 * angle_diff
        self.publisher.publish(msg)

    def reset_car(self):
        if self.reset_timer is not None:
            self.reset_timer.cancel()
            self.reset_timer = None
        if self.clear_client.wait_for_service(timeout_sec=1.0):
            self.clear_client.call_async(Empty.Request())
        if self.teleport_client.wait_for_service(timeout_sec=1.0):
            req = TeleportAbsolute.Request()
            req.x = START_X
            req.y = START_Y
            req.theta = 0.0
            self.teleport_client.call_async(req)
        self.stop()
        self.parked = False
        self.resetting = False
        self.reset_done = False
        self.target = self.find_free_spot()
        if self.target:
            self.get_logger().info("Run " + str(self.park_count + 1) + ": Heading to spot " + str(self.target["id"] + 1))
        else:
            self.get_logger().info("All spots occupied! Simulation complete.")

    def stop(self):
        self.publisher.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = ParkingSimNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
