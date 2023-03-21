import utils

import typing
import numpy as np
import json
import matplotlib

from std_msgs.msg import Float64MultiArray
from nav_msgs.msg import Odometry
import rospy

matplotlib.use('Agg')

with open('mapper.json') as json_file:
    mapper = json.load(json_file)

obstacle_avoidance = utils.ObstacleAvoidance()


class Node:
    def __init__(self, release_time, tag=0):
        self.tag = tag
        self.release_time = release_time
        self.address = mapper[str(tag)]['address']
        self.start_pos = np.array(mapper[str(tag)]['pos'])
        self.start_orien = np.array(mapper[str(tag)]['orien'])

        # Initialize ros subscriber messages
        self.robot_meas_pose = np.array([np.NaN, np.NaN])
        self.robot_meas_orien = np.NaN
        self.robot_meas_time = np.NaN

        # initialize theoretical positioning
        self.pos = np.array([self.start_pos, self.start_pos, self.start_pos, self.start_pos, self.start_pos])
        self.orien = np.array([self.start_orien, self.start_orien, self.start_orien, self.start_orien, self.start_orien])

        # Initialize rostopic listeners/writers
        self.listener_robot_pose = rospy.Subscriber('elisa3_robot_{}/odom'.format(self.tag), Odometry,
                                                    self.listen_robot_pose_callback)

        # Initialize shared update message attributes
        self.update_leds = False
        self.msg_leds = np.array([0,0,0])
        self.update_auto_motive = False
        self.msg_auto_motive = np.array([0,0,0,0])
        self.update_reset = False
        self.msg_reset = np.array([0, 0, 0, 0])
        self.trigger_auto_motive = 103

    def publish_greenLed(self, intensity = np.array([0])):
        self.update_leds = True
        self.msg_leds[0] = intensity

    def publish_redLed(self, intensity = np.array([0])):
        self.update_leds = True
        self.msg_leds[1] = intensity

    def publish_blueLed(self, intensity = np.array([0])):
        self.update_leds = True
        self.msg_leds[2] = intensity

    def listen_robot_pose_callback(self, odomMsg):
        self.robot_meas_pose = np.round(np.array([float(odomMsg.pose.pose.position.x),
                                                  float(odomMsg.pose.pose.position.y)]),3)
        self.robot_meas_orien = np.round(float(odomMsg.pose.pose.position.z),3)
        self.robot_meas_time = odomMsg.header.stamp.secs

    def led_off(self):
        self.publish_greenLed(intensity=np.array([0]))
        self.publish_blueLed(intensity=np.array([0]))
        self.publish_redLed(intensity=np.array([0]))

    def reset(self, type = 'odom'):
        if type == 'odom':
            if np.isnan(sum(self.robot_meas_pose)) or np.isnan(self.robot_meas_orien):
                print('robot: {} odom measures give nan, keep theoretical measure')
            else:
                self.pos[-1] = self.robot_meas_pose
                self.orien[-1] = self.robot_meas_orien
            self.update_reset = False
        elif type == 'theor':
            self.update_reset = True
            self.msg_reset = np.array([0, self.pos[-1][0], self.pos[-1][1], self.orien[-1]])

    def compute_move(self, pol: np.array):
        """
        :param pol: intended change in location nin polar coordinates np.array([rho, phi]) g
        :return: ros instruction [left or right, degrees to turn, forward or backward, longitudinal move]
        """
        self.print_position_measures()

        orien_cor = self.orien[-1]
        if orien_cor < 0:
            orien_cor += 2 * np.pi
        orien_cor %= (2 * np.pi)
        if orien_cor > np.pi:
            orien_cor -= 2*np.pi

        phi_cor = pol[1]
        if phi_cor < 0:
            phi_cor += 2 * np.pi
        phi_cor %= (2 * np.pi)
        if phi_cor > np.pi:
            phi_cor -= 2*np.pi

        delta_phi = phi_cor - orien_cor

        if delta_phi >= 0:
            self.msg_auto_motive = np.array([1, delta_phi, 0, pol[0]])
        else:
            self.msg_auto_motive = np.array([0, -delta_phi, 0, pol[0]])

        self.update_auto_motive = True

        if self.trigger_auto_motive == 103:
            self.trigger_auto_motive = 104
        else:
            self.trigger_auto_motive = 103

        # UPDATE POSITION
        prop_move_cart = utils.pol2cart(np.array([pol[0], phi_cor]))
        calc_point, obs_avoid_mode = obstacle_avoidance.obstacle_avoidance(self.pos[-1], prop_move_cart)

        self.pos = utils.renew_vec(self.pos)
        self.orien = utils.renew_vec(self.orien)

        self.pos[-1] = calc_point
        self.orien[-1] += delta_phi

    def print_position_measures(self):
        msg = """ 
                ID: {}
                Theoretical: 
                position: {} - orientation: {}
                Odom Measure: 
                position: {} - orientation: {}
                  """.format(self.tag,
                             self.pos[-1], self.orien[-1],
                             self.robot_meas_pose, self.robot_meas_orien)
        print(msg)


class Nodes:
    def __init__(self, active_robots = ['0000']):
        for tag in active_robots:
            if tag not in mapper:
                raise ValueError('mapper robot: ' + str(tag) +' is missing ')

        self.active_robots = active_robots

        rospy.init_node('python_node')
        self.publisher_auto_motive = rospy.Publisher("elisa3_all_robots/auto_motive", Float64MultiArray,
                                                     queue_size=10)
        self.msg_auto_motive = Float64MultiArray()

        self.publisher_leds = rospy.Publisher("elisa3_all_robots/leds", Float64MultiArray,
                                                     queue_size=10)
        self.msg_leds = Float64MultiArray()

        self.publisher_reset = rospy.Publisher("elisa3_all_robots/reset", Float64MultiArray,
                                              queue_size=10)
        self.msg_reset = Float64MultiArray()

        self.nodes = {tag: Node(release_time=0, tag=tag) for tag in active_robots}


    def move(self, step_size: float = 5., theta: float =0.):
        for tag in self.nodes:
            self.nodes[tag].compute_move(pol=np.array([step_size, theta])) # \TODO change to move

        # SETUP MESSAGE
        self.msg_auto_motive.data = np.array([len(self.nodes)])
        for tag in self.nodes:
            self.msg_auto_motive.data = np.concatenate((self.msg_auto_motive.data,
                    np.array([int(self.nodes[tag].address)]), self.nodes[tag].msg_auto_motive), axis=0)

        # SEND MOVE MESSAGE
        rospy.sleep(1)
        self.publisher_auto_motive.publish(self.msg_auto_motive)
        rospy.sleep(10)

    def update_leds(self, subset_tags: typing.Optional[list] = None):
        self.msg_leds.data = np.array([0])
        count = 0

        if subset_tags:
            ToIterateOver = subset_tags
        else:
            ToIterateOver = self.nodes.keys()

        for tag in ToIterateOver:
            self.msg_leds.data = np.concatenate((self.msg_leds.data, np.array([int(self.nodes[tag].address)]),
                             self.nodes[tag].msg_leds), axis=0)
            count += 1
        self.msg_leds.data[0] = count

        self.publisher_leds.publish(self.msg_leds)

    def reset(self, type = 'odom', subset_tags: typing.Optional[list] = None):
        self.msg_reset.data = np.array([0])

        if subset_tags:
            ToIterateOver = subset_tags
        else:
            ToIterateOver = self.nodes.keys()

        count = 0
        for tag in ToIterateOver:
            self.nodes[tag].reset(type=type)

            # ONLY REPLENISH MESSAGE IF THEOR UPDATE TYPE
            if self.nodes[tag].update_reset:
                self.msg_reset.data = np.concatenate((self.msg_reset.data, np.array([int(self.nodes[tag].address)]),
                                                      self.nodes[tag].msg_reset), axis=0)
                count += 1

        if count != 0:
            self.msg_reset.data[0] = count
            self.publisher_reset.publish(self.msg_reset)

    def print_position_measures(self):
        for tag in self.nodes:
            self.nodes[tag].print_position_measures()

    def turn_off_leds(self):
        for tag in self.nodes:
            self.nodes[tag].led_off()
        self.update_leds()

    def set_leds(self, green=0, blue=0, red=0):
        for tag in self.nodes:
            self.nodes[tag].publish_greenLed(intensity=np.array([green]))
            self.nodes[tag].publish_blueLed(intensity=np.array([blue]))
            self.nodes[tag].publish_redLed(intensity=np.array([red]))
        self.update_leds()