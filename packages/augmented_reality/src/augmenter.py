#!/usr/bin/env python

import cv2
import numpy as np

class Augmenter():
    """This class converts point to the camera coordinate
        and write the features of the map file on the rectified image"""

    def __init__(self, map_file, intrinsic, homografy_matrix):
        self.map_file = map_file
        self.intrinsic = intrinsic
        self.homografy_matrix = homografy_matrix

    def render_segments(self, img):
        """"""
        points=self.map_file['points']
        #print("these are the points : "+str(points))

        #{'color': 'red', 'points': ['TL', 'TR']}
        #['image01', [1, 0]]

        for edge in self.map_file["segments"]:
            color = edge['color']
            poi = edge['points']
            coord_type, p1 = points[poi[0]]
            coord_type, p2 = points[poi[1]]

            if coord_type == 'image01':
                p1 = self.scaleToCamera(p1)
                p2 = self.scaleToCamera(p2)
            elif coord_type == 'axle':
                p1 = self.ground2pixel(np.array(p1))
                p2 = self.ground2pixel(np.array(p2))

            #print("point start = "+str(p1))
            #print("point end = "+str(p2))
            img = self.draw_segment(img, [p1[0], p2[0]], [p1[1], p2[1]], color)

        return img
    
    def scaleToCamera(self, point):
        """Scale Point to the camera size"""
        return [point[0]*self.intrinsic['image_width'],point[1]*self.intrinsic['image_height']]

    def process_image(self,image):
        """This function return the undirstorted image"""
        height, width, _ = image.shape
        border_values = np.zeros(np.shape(image))
        mapx = np.ndarray(shape=(height, width, 1), dtype='float32')
        mapy = np.ndarray(shape=(height, width, 1), dtype='float32')

        # Get the camera matrix from intrinsic calibration
        camera_matrix=np.matrix(self.intrinsic.get('camera_matrix')['data']).reshape(3,3)

        # Get the distortion coefficients
        dist = np.array(self.intrinsic.get('distortion_coefficients')['data']).reshape(1,5)

        # Get the distortion coefficients
        rectification_matrix = np.matrix(self.intrinsic.get('rectification_matrix')['data']).reshape(3,3)

        # Get the distortion coefficients
        projection_matrix = np.matrix(self.intrinsic.get('projection_matrix')['data']).reshape(3,4)

        mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix,
                                                 dist,
                                                 rectification_matrix,
                                                 projection_matrix,
                                                 (width, height),
                                                 cv2.CV_32FC1,
                                                 mapx,
                                                 mapy)
        image_rectified = cv2.remap(image, mapx, mapy, cv2.INTER_CUBIC, border_values)
        return image_rectified

    def ground2pixel(self, point):
        """This function trasform the ground real world points to pixel coordinate"""
        # add the 3rd element
        point = np.asarray(point)
        point[2]=1
        new_point=np.linalg.solve(self.homografy_matrix,point)
        pixel = new_point[0:2]/new_point[2]
        pixel = np.round(pixel, decimals=0)
        return pixel.astype(int)

    def draw_segment(self, image, pt_x, pt_y, color):
        defined_colors = {
            'red': ['rgb', [1, 0, 0]],
            'green': ['rgb', [0, 1, 0]],
            'blue': ['rgb', [0, 0, 1]],
            'yellow': ['rgb', [1, 1, 0]],
            'magenta': ['rgb', [1, 0 , 1]],
            'cyan': ['rgb', [0, 1, 1]],
            'white': ['rgb', [1, 1, 1]],
            'black': ['rgb', [0, 0, 0]]}
        _color_type, [r, g, b] = defined_colors[color]
        cv2.line(image, (pt_x[0], pt_y[0]), (pt_x[1], pt_y[1]), (b * 255, g * 255, r * 255), 5)
        return image
