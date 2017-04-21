import cv2
import numpy as np
import math
import argparse
import os
from collections import namedtuple
from itertools import groupby


class PerfDetector(object):
    sixteen = {'perfs': 2, 'frame_area': 20, 'perf_area': 100}

    def __init__(self, **kwargs):
        try:
            self.resolution = kwargs['resolution']  # tuple like so (w,h)
            if kwargs['gauge'] == '16mm':
                self._gauge = PerfDetector.sixteen
        except KeyError as error:
            print(error)

    def detect_perfs(self, raw_pixels):
        image = raw_pixels
        h, w, channels = image.shape
        image = image[0:h, 0:math.floor(w / self._gauge['frame_area'])]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]

        _, thresh = cv2.threshold(saturation, 25, 255, cv2.THRESH_BINARY)
        (_, contours, h) = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for contour in sorted_contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            contour_area = cv2.contourArea(contour)
            if len(approx) == 4 and contour_area >= self.gauge['perf_area']:
                return True
        return False
