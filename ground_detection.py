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
                if sum(image[y, x]) != 0:
                    return x, y  # no idea why the swap is needed here. Maybe numpy vs openCV ?
        else:
            raise Exception('Could not find corners. Maybe green detection failed ?')

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


def tarvas_geometric(raw_image, visualize):
    # resize
    f = 0.3  # in the paper 1/3 is used
    image = cv2.resize(raw_image, (0, 0), fx=f, fy=f)
    # color thresholding
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color = 145 // 2  # green to hue
    dx = 33
    lower_green = np.array([max(0, color-dx), 100, 100])
    upper_green = np.array([max(0, color+dx), 255, 255])
    mask = cv2.inRange(image_hsv, lower_green, upper_green)
    if mask.max() == 0:
        raise Exception('Could not detect any green')
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

    points = np.array([lowc[0], highc[0], sl, ml, mr, sr, highc[1], lowc[1]])
    overlay = image.copy()
    cv2.fillPoly(overlay, np.int32([points]), (255, 255, 255))
    image = cv2.addWeighted(overlay, 0.3, image, 0.7, 0)
    # visualize results
    if visualize:
        cv2.circle(masked, lowc[0], 3, (255, 0, 0), 3)  # L in paper (blue)
        cv2.circle(masked, lowc[1], 3, (255, 0, 0), 3)  # L in paper (blue)
        cv2.circle(masked, highc[0], 3, (128, 128, 0), 3)  # A in paper (blue-green)
        cv2.circle(masked, highc[1], 3, (128, 128, 0), 3)  # A in paper (blue-green)
        cv2.circle(masked, sl, 3, (0, 0, 255), 3)  # S in paper (red)
        cv2.circle(masked, sr, 3, (0, 0, 255), 3)  # S in paper (red)
        cv2.circle(masked, ml, 3, (0, 128, 128), 3)  # M in paper (olive)
        cv2.circle(masked, mr, 3, (0, 128, 128), 3)  # M in paper (olive)
        cv2.line(masked, (mid, 0), (mid, 10000), (0, 0, 255))
        masked = cv2.addWeighted(overlay, 0.3, masked, 0.7, 0)
        cv2.imshow('original', raw_image)
        cv2.imshow('masked', masked)
        cv2.imshow('result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return image


if __name__ == '__main__':
    img = cv2.imread('6.jpg', cv2.IMREAD_COLOR)
    tarvas_geometric(img, True)
    cap = cv2.VideoCapture('vid.mp4')
    factor = 1
    while cap.isOpened():
        ret, frame = cap.read()
        try:
            tarvas = frame
            tarvas = tarvas_geometric(frame, False)
            tarvas = cv2.resize(tarvas, (0, 0), fx=factor, fy=factor)
        except:
            pass
        cv2.imshow('frame', tarvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


