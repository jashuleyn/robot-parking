from setuptools import setup

package_name = 'parking_sim'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='iya',
    maintainer_email='iya@example.com',
    description='ROS2 Autonomous Parking Simulator',
    license='MIT',
    entry_points={
        'console_scripts': [
            'parking_sim_node = parking_sim.parking_sim_node:main',
            'visualizer = parking_sim.visualizer:main',
        ],
    },
)
