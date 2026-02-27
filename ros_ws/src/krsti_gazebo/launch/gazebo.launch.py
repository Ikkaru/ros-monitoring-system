#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # ─── Arguments ────────────────────────────────────────────────────────────
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # ─── Robot Description ────────────────────────────────────────────────────
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([
                FindPackageShare("krsti_description"),
                "urdf",
                "krsti.xacro",
            ]),
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    # ─── World File ───────────────────────────────────────────────────────────
    world_file = PathJoinSubstitution([
        FindPackageShare("krsti_gazebo"),
        "worlds",
        "krsti_world.sdf",
    ])

    # ─── Gazebo Sim ───────────────────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py",
            ])
        ]),
        launch_arguments={"gz_args": ["-r -v4 ", world_file]}.items(),
    )

    # ─── Robot State Publisher ────────────────────────────────────────────────
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": use_sim_time}],
    )

    # ─── Spawn Robot di Gazebo ────────────────────────────────────────────────
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_krsti",
        arguments=[
            "-topic", "robot_description",
            "-name", "krsti",
            "-z", "0.5",
        ],
        output="screen",
    )

    # ─── Controllers ──────────────────────────────────────────────────────────
    # Gunakan spawner (bukan ExecuteProcess ros2 control load_controller)
    # spawner otomatis menunggu controller_manager siap sebelum load controller
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller"],
        output="screen",
    )


    # ─── ROS-Gazebo Bridge ────────────────────────────────────────────────────
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen",
    )

    # ─── Event Handlers (urutan load controller) ──────────────────────────────
    # Load joint_state_broadcaster setelah robot di-spawn
    load_jsb_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    # Load joint_trajectory_controller setelah joint_state_broadcaster aktif
    load_jtc_after_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_trajectory_controller_spawner],
        )
    )

    return LaunchDescription([
        # Set resource path agar Gazebo bisa menemukan mesh
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value='/root/ros_ws/install/krsti_description/share'
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation (Gazebo) clock if true",
        ),
        gazebo,
        robot_state_publisher,
        bridge,
        spawn_robot,
        load_jsb_after_spawn,
        load_jtc_after_jsb,
    ])
