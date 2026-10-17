from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    root=Path(get_package_share_directory('micro_dog_x430_description'))
    return LaunchDescription([
        Node(package='robot_state_publisher',executable='robot_state_publisher',parameters=[{'robot_description':(root/'urdf/micro_dog_x430_ros.urdf').read_text()}]),
        Node(package='joint_state_publisher_gui',executable='joint_state_publisher_gui'),
        Node(package='rviz2',executable='rviz2',arguments=['-d',str(root/'rviz/display.rviz')])])
