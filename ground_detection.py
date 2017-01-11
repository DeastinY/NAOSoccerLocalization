#!/usr/bin/env python2.7

# The basic idea is to divide items in two categories 'in the field' and 'not in the field'.
# Techniques used are histogram normalization (SS09) and initial mean values (Bol15)
# To improve bypass the issues introduced by occlusion a geometric approach is described in Tarvas work.
#
#
# SS09 : Mohan Sridharan and Peter Stone:
#  Color learning and illumination invariance on mobile robots: A survey.
# Bol15 : Anastasia Bolotnikova:
#  Melioration of color calibration, goal detection and self-localization systems of nao humanoid robots, 2015
import cv2
import numpy as np


def histogram_normalization():
    print('See research/RAS09-sridharan.pdf')


def initial_mean_values():
    print('See research/bolotnikova_thesis.pdf')


def tarvas_geometric(raw_image):
    # resize
    image = cv2.resize(raw_image, (0, 0), fx=0.5, fy=0.5)
    # color thresholding
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green = np.uint8([[[0, 255, 0]]])
    hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    print(hsv_green)  # use [H-X, 100, 100] and [H+X, 255, 255] for separation
    lower_green, upper_green = np.array([40, 100, 100]), np.array([80, 255, 255])
    mask = cv2.inRange(image_hsv, lower_green, upper_green)
    # erode and dilate
    kernel = np.ones((10, 10), np.uint8)  # magic number 10 from paper
    mask = cv2.erode(mask, kernel)
    mask = cv2.dilate(mask, kernel)
    # corner detection
    epsilon_snap = 20  # magic number 20 from paper


    # visualize results
    cv2.imshow('original', raw_image)
    output = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('overlay', output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    img = cv2.imread('sample.png', cv2.IMREAD_COLOR)
    tarvas_geometric(img)
