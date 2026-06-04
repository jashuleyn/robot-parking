# parking_sim (ROS 2)

A small autonomous parking demo for TurtleBot3 in Gazebo.

## What it does
The node reads `/odom`, drives the robot using `/cmd_vel`, and parks it at a target pose with a simple go-to-goal controller.

## How to run on The Construct
1. Open your rosject.
2. In one terminal, start Gazebo:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

3. In another terminal, run the controller:

```bash
cd ~/ros2_ws
colcon build --packages-select parking_sim
source install/setup.bash
ros2 run parking_sim parking_controller --ros-args -p target_x:=1.5 -p target_y:=0.0 -p target_yaw:=0.0
```

## Notes
- The TurtleBot3 Gazebo launch command above follows the official TurtleBot3 simulation docs.
- The controller publishes `geometry_msgs/msg/Twist` to `/cmd_vel` and uses odometry feedback from `/odom`.
