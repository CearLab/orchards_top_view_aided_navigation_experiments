import subprocess
import numpy as np
import pandas as pd
import yaml
import os
import time
import cv2
import rospy
import rosbag
import rosnode
from geometry_msgs.msg import Pose2D

import utils
import logger


_logger = logger.get_logger()


def start_master(use_sim_time=True):
    _logger.info('Launching ROS master')
    ros_proc = utils.new_process(['roscore'], output_to_console=False)
    time.sleep(2)
    if use_sim_time:
        param_set_proc = utils.new_process(['rosparam', 'set', 'use_sim_time', 'true'])
        param_set_proc.communicate()
    return ros_proc


def kill_master():
    _logger.info('Killing all live ROS master processes')
    for proc_name in ['roscore', 'rosmaster', 'rosout']:
        utils.kill_process(proc_name)


def launch(**kwargs):
    if kwargs.has_key('direct_path'):
        launch_proc = utils.new_process(['roslaunch', kwargs.get('direct_path')])
    else:
        launch_proc = utils.new_process(['roslaunch', kwargs.get('package'), kwargs.get('launch_file')])
    return launch_proc


def play_bag(bag_file, use_clock=True):
    _logger.info('Starting bag playing')
    if type(bag_file) == tuple:
        bags = [rosbag.Bag(single_bag_file) for single_bag_file in bag_file]
        duration_in_seconds = sum([bag.get_end_time() - bag.get_start_time() for bag in bags])
        path_for_command_line = ' '.join(bag_file)
    else:
        bag = rosbag.Bag(bag_file)
        duration_in_seconds = bag.get_end_time() - bag.get_start_time()
        path_for_command_line = bag_file
    if use_clock:
        play_proc = utils.new_process(['rosbag', 'play', path_for_command_line, '--clock'], output_to_console=True)
    else:
        play_proc = utils.new_process(['rosbag', 'play', path_for_command_line], output_to_console=True)
    return play_proc, duration_in_seconds


def start_recording_bag(path, topics=None):
    if topics is None:
        topics = ['-a']
    record_proc = utils.new_process(['rosbag', 'record'] + topics + ['-O', path])
    return record_proc


def stop_recording_bags():
    nodes_list = rosnode.get_node_names()
    for node_name in nodes_list:
        if node_name.find('record') != -1:
            rosnode.kill_nodes([node_name])


def save_map(map_name, dir_name):
    save_map_proc = subprocess.Popen(['rosrun', 'map_server', 'map_saver', '-f', map_name], cwd=dir_name)
    time.sleep(1)
    save_map_proc.kill()


def bag_to_dataframe(bag_path, topic, fields):
    data = {}
    timestamps = []
    for field in fields:
        data[field] = np.array([])
    if type(bag_path) is not tuple:
        bag_path = (bag_path,)
    for single_bag_path in bag_path:
        single_bag = rosbag.Bag(single_bag_path)
        for _, message, timestamp in single_bag.read_messages(topics=topic):
            for field in fields:
                data[field] = np.append(data[field], utils._rgetattr(message, field))
            timestamps.append(timestamp.to_sec())
    df = pd.concat([pd.Series(data[field], index=timestamps, name=field) for field in fields], axis=1)
    return df


def save_image_to_map(image, resolution, map_name, dir_name):
    cv2.imwrite(os.path.join(dir_name, map_name + '.pgm'), image)
    yaml_content = {'image' : map_name,
                    'resolution' : resolution,
                    'origin' : [0.0, 0.0, 0.0],
                    'negate' : 1,
                    'occupied_thresh' : 0.9,
                    'free_thresh' : 0.1}
    with open(os.path.join(dir_name, map_name + '.yaml'), 'w') as yaml_file:
        yaml.dump(yaml_content, yaml_file)


def trajectory_to_bag(pose_time_tuples_list, bag_path, topic='vehicle_pose'):
    bag_file = rosbag.Bag(bag_path, 'w')
    start_time = pose_time_tuples_list[0]
    for pose_time in pose_time_tuples_list:
        # TODO: go over legacy code and see where IMAGE_HEIGHT is subtracted
        x = pose_time[0]
        y = pose_time[1]
        t = pose_time[2] - start_time
        ros_time = rospy.rostime.Time(secs=t.seconds, nsecs=t.microseconds*1e3)
        pose_2d_message = Pose2D(x, y)
        bag_file.write(topic, pose_2d_message, ros_time)
    bag_file.close()