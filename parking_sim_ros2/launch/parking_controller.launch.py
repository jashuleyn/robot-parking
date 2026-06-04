from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    target_x = LaunchConfiguration('target_x')
    target_y = LaunchConfiguration('target_y')
    target_yaw = LaunchConfiguration('target_yaw')

    return LaunchDescription([
        DeclareLaunchArgument('target_x', default_value='1.5'),
        DeclareLaunchArgument('target_y', default_value='0.0'),
        DeclareLaunchArgument('target_yaw', default_value='0.0'),
        Node(
            package='parking_sim',
            executable='parking_controller',
            name='parking_controller',
            output='screen',
            parameters=[{
                'target_x': target_x,
                'target_y': target_y,
                'target_yaw': target_yaw,
            }],
        ),
    ])
