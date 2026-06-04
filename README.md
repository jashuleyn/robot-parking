# ROS2 Parking Simulator

A simple autonomous parking simulator built with ROS2 Jazzy and Pygame on Windows 11 (WSL2).

## Features
- Autonomous car navigation to free parking spots
- Pygame visualizer with real-time status panel and car shapes
- Color-coded parking spots (green = free, red = occupied, yellow = target)
- Auto-reset and loop — car teleports back to center and finds the next free spot
- Live status panel showing position, target, and park count

## Requirements
- Windows 11 with WSL2
- Ubuntu 24.04
- ROS2 Jazzy
- Python 3.12
- pygame (`pip install pygame --break-system-packages`)

## Setup
```bash
cd ~/ros2_ws/src
# copy this folder here, then:
cd ~/ros2_ws
colcon build --packages-select parking_sim
source install/setup.bash
```

## How to Run
Open 3 terminals (all in WSL2):

**Terminal 1:**
```bash
ros2 run turtlesim turtlesim_node
```

**Terminal 2:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 run parking_sim parking_sim_node
```

**Terminal 3:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 run parking_sim visualizer
```

## How it works
- The ROS2 node subscribes to `/turtle1/pose` and publishes velocity commands to `/turtle1/cmd_vel`
- It calculates the angle and distance to the target parking spot and drives toward it
- Once parked, it waits 2 seconds, teleports back to the start, and finds the next free spot
- The Pygame visualizer subscribes to `/parking_status` and renders everything in real time
