"""
display.launch.py
Launch file untuk menampilkan robot di RViz2
Cara run: ros2 launch my_robot display.launch.py urdf_file:=<path_to_urdf_file>
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():  
    # Fetch the package directory
    pkg_dir = get_package_share_directory('my_robot')

    # Declare the launch argument for the URDF file path
    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=os.path.join(pkg_dir, 'urdf', 'my_robot.urdf.xacro'),
        description='Path to the URDF file to display in RViz2'
    )

    # Declare the launch argument for the RViz config file path
    rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(pkg_dir, 'rviz', 'robot.rviz'),
        description='Path ke file config RViz'
    )

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('urdf_file')]),
        value_type=str
    )

    # ── Nodes ─────────────────────────────────────────────
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen'
    )

    return LaunchDescription([
        urdf_file_arg,
        rviz_config,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node,
    ])