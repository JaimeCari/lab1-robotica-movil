import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.xml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.txt')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jaimecari',
    maintainer_email='jaimecari@todo.todo',
    description='Lab 1 - Robotica Movil IIC-2685: dead reckoning, teleoperacion y percepcion de obstaculos',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'teleop_key = scripts.teleop_key:main',
            'dead_reckoning_nav = scripts.dead_reckoning_nav:main', 
            'pose_loader = scripts.pose_loader:main',
            'obstacle_detector = scripts.obstacle_detector:main',
            'pose_recorder_csv = scripts.pose_recorder_csv:main',
        ],
    },
)