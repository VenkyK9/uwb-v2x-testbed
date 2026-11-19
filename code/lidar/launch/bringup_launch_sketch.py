# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Pseudocode (imports are incomplete). Not runnable as written.
# About  : Outline of one bring-up launch file with mode:=handheld|robot.
# ----------------------------------------------------------------------------
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, IncludeLaunchDescription

def generate_launch_description():
    mode = LaunchConfiguration('mode')

    declare_mode = DeclareLaunchArgument(
        'mode', default_value='handheld', choices=['handheld', 'robot'])

    # Common: slam_toolbox, Nav2
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=['config/slam_handheld.yaml']  # or slam_robot.yaml later
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            '/opt/ros/humble/share/nav2_bringup/launch/bringup_launch.py'),
        launch_arguments={
            'params_file': 'config/nav2_handheld.yaml',
            'use_sim_time': 'false'
        }.items()
    )

    handheld_group = GroupAction([
        # lidar driver
        Node(package='sllidar_ros2', executable='sllidar_node', name='sllidar_node'),
        # static TF base_link->laser
        Node(
          package='tf2_ros',
          executable='static_transform_publisher',
          arguments=['0','0','0','0','0','0','base_link','laser']
        ),
        # no robot_state_publisher, no wheel odom
    ])

    robot_group = GroupAction([
        # robot_state_publisher
        # wheel odometry / EKF
        # base_link->laser from URDF
    ])

    return LaunchDescription([
        declare_mode,
        slam,
        nav2,
        OpaqueFunction(function=lambda context: handheld_group if context.perform_substitution(mode) == 'handheld' else robot_group)
    ])
