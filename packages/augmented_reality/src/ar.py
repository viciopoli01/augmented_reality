#!/usr/bin/env python

import cv2
import numpy as np
import os
import rospy
import yaml
import sys
from duckietown import DTROS
from sensor_msgs.msg import CompressedImage
from duckietown_msgs.msg import WheelsCmdStamped
from cv_bridge import CvBridge, CvBridgeError

import augmenter as au

class Node(DTROS):

    def __init__(self, node_name):

        # Initialize the DTROS parent class
        super(Node, self).__init__(node_name=node_name)
        self.veh = "cristina" #rospy.get_namespace().strip("/")
        self.robot_name=rospy.get_param('~robot_name')
        self.map_file_name=rospy.get_param('~map_file')

        # Read yaml file for the camera claibration
        self.extrinsic = self.readParamFromFile("/data/config/calibrations/camera_extrinsic/"+self.veh+".yaml")
        self.intrinsic = self.readParamFromFile("/data/config/calibrations/camera_intrinsic/"+self.veh+".yaml")
        
        # Create a well sized homografy matrix
        self.homografy_matrix = np.matrix(self.extrinsic.get('homography'))
        self.homografy_matrix.resize((3,3))

        # Read the map file
        self.map_file = self.readParamFromFile("/code/catkin_ws/src/augmented_reality/packages/augmented_reality/config/"+self.map_file_name+".yaml")
        
        # inizialize the augmenter map_file, intrinsic, homografy_matrix
        self.ar = au.Augmenter(self.map_file, self.intrinsic, self.homografy_matrix)
        
        # Subscribe to topic
        camera_topic="/"+self.veh+"/camera_node/image/compressed"

        #Setup the camera subscriber
        self.camera = rospy.Subscriber(camera_topic, CompressedImage, self.imageCallback)

        # publisher on the topic robot name/node_name/map file basename
        self.pub = rospy.Publisher("~/"+self.robot_name+"/"+node_name+"/"+self.map_file_name+"/image/compressed", CompressedImage, queue_size=1)
        
        # initialize bridge to convert image to opencv image
        self.bridge = CvBridge()

        self.log("Initialized")

    #
    # MY CODE
    #
    #
    #
    #

    def imageCallback(self,data):
        """called when the image/compressed publish something"""
        # convert compressed image to opencv images
        img = self.readIamge(data)

        # rectify the image
        img = self.ar.process_image(img)

        # write features on the image
        img = self.ar.render_segments(img)

        # publish image
        cmprsmsg = self.bridge.cv2_to_compressed_imgmsg(img)
        self.pub.publish(cmprsmsg)

    def readIamge(self,msg_image):
        """Convert images to OpenCV images
            Args:
                msg_image (:obj:`CompressedImage`) the image from the camera node
            Returns:
                OpenCV image
        """
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(msg_image)
            return cv_image
        except CvBridgeError as e:
            print(e)
            return []
    
    #
    # TEMPLATE CODE
    #
    #
    #
    #

    def readParamFromFile(self,fname):
        """
        Reads the saved parameters from
        `/data/config/calibrations/filename/DUCKIEBOTNAME.yaml` or
        uses the default values if the file doesn't exist. Adjsuts
        the ROS paramaters for the node with the new values.

        """
        # Check file existence
        # Use the default values from the config folder if a
        # robot-specific file does not exist.
        with open(fname, 'r') as in_file:
            try:
                yaml_dict = yaml.load(in_file)
            except yaml.YAMLError as exc:
                self.log("YAML syntax error. File: %s fname. Exc: %s"
                         %(fname, exc), type='fatal')
                rospy.signal_shutdown()
                return
        return yaml_dict


    def onShutdown(self):
        super(Node, self).onShutdown()


if __name__ == '__main__':
    # Initialize the node
    camera_node = Node(node_name='augmented_reality_node')
    # Keep it spinning to keep the node alive
    rospy.spin()