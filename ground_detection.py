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
import math
import numpy as np


def histogram_normalization():
    print('See research/RAS09-sridharan.pdf')


def initial_mean_values():
    print('See research/bolotnikova_thesis.pdf')


def lower_corner(image):
    height, width, depth = image.shape

    def calc(left):
        for x in range(width-1):
            x = x if left else width - x - 1
            for y in range(height-1):
                y = height - y - 1
                if sum(image[y, x]) == 0:
                    return x, y  # no idea why the swap is needed here. Maybe numpy vs openCV ?

    return calc(True), calc(False)


def highest_corner(image, lowc):
    """This algorithm checks the pixels above the low corner points whether a colored pixel can be found within
    the snap square of 20 pixels. The highest of those pixels are then returned. """
    epsilon_snap = 20  # magic number 20 from pape
    results = []
    for l in lowc:
        x, y = l
        max_y = y
        while y > 0:  #todo: change to snap to points left and right as well
            y -= 1
            if sum(image[y, x]) > 0:
                max_y = y
            elif abs(y-max_y) > epsilon_snap:
                break
        results.append((x, max_y))
    return results


def get_weighted_edges(image, mid):
    height, width, depth = image.shape
    sl, sr = 0, 0
    slc, src = None, None
    for x in range(width):
        for y in range(height):
            if not sum(image[y, x]) > 0:
                continue
            if x < mid:
                d = math.sqrt(x ** 2 + y ** 2)
                w = math.sqrt(y)/d
                if w > sl:
                    sl = w
                    slc = (x, y)
            else:
                d = math.sqrt((width + 1 - x) ** 2 + y ** 2)
                w = math.sqrt(y) / d
                if w > sr:
                    sr = w
                    src = (x, y)
    return slc, src


def get_minima(image, mid):
    ml, mr = (0, 10**10), (0, 10**10)
    height, width, depth = image.shape
    for y in range(height - 1):
        for x in range(width - 1):
            if sum(image[y, x]) != 0:
                if x < mid and y < ml[1]:
                    ml = (x, y)
                elif x >= mid and y < mr[1]:
                    mr = (x, y)
    return ml, mr


def tarvas_geometric(raw_image):
    # resize
    factor = 0.3  # in the paper 1/3 is used
    image = cv2.resize(raw_image, (0, 0), fx=factor, fy=factor)
    # color thresholding
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green = np.uint8([[[0, 255, 0]]])
    hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    print(hsv_green)  # use [H-X, 100, 100] and [H+X, 255, 255] for separation
    x = 90
    lower_green, upper_green = np.array([40-x, 100, 100]), np.array([60+x, 255, 255])
    mask = cv2.inRange(image_hsv, lower_green, upper_green)
    # erode and dilate
    kernel = np.ones((10, 10), np.uint8)  # magic number 10 from paper
    mask = cv2.erode(mask, kernel)
    mask = cv2.dilate(mask, kernel)
    masked = cv2.bitwise_and(image, image, mask=mask)
    # corner detection
    lowc = lower_corner(masked)
    highc = highest_corner(masked, lowc)
    mid = (lowc[0][0]+lowc[1][0])/2+5
    sl, sr = get_weighted_edges(masked, mid)
    ml, mr = get_minima(masked, mid)

    # visualize results
    cv2.circle(masked, lowc[0], 3, color=(255, 0, 0), thickness=3)  # L in paper (blue)
    cv2.circle(masked, lowc[1], 3, color=(255, 0, 0), thickness=3)  # L in paper (blue)
    cv2.circle(masked, highc[0], 3, color=(128, 128, 0), thickness=3)  # A in paper (blue-green)
    cv2.circle(masked, highc[1], 3, color=(128, 128, 0), thickness=3)  # A in paper (blue-green)
    cv2.circle(masked, sl, 3, color=(0, 0, 255), thickness=3)  # S in paper (red)
    cv2.circle(masked, sr, 3, color=(0, 0, 255), thickness=3)  # S in paper (red)
    #cv2.circle(masked, ml, 3, color=(0, 128, 128), thickness=3)  # M in paper (olive)
    #cv2.circle(masked, mr, 3, color=(0, 128, 128), thickness=3)  # M in paper (olive)
    cv2.line(masked, (mid, 0), (mid, 10000), color=(0, 0, 255))
    cv2.imshow('original', raw_image)
    cv2.imshow('masked', masked)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    img = cv2.imread('sample3.png', cv2.IMREAD_COLOR)
    tarvas_geometric(img)
