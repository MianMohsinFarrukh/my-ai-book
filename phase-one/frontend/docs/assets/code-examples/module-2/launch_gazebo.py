from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """Launch Gazebo with a world file."""

    # Get the launch directory
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Declare arguments
    declared_arguments = [
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(
                get_package_share_directory('my_robot_description'),
                'worlds',
                'simple_world.sdf'
            ),
            description='Choose one of the world files from `/my_robot_description/worlds`'
        ),
    ]

    # Include the Gazebo launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    return LaunchDescription(declared_arguments + [gazebo])