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


def highest_corner(image, ll, lr):
    """This algorithm checks the pixels above the low corner points whether a colored pixel can be found within
    the snap square of 20 pixels. The highest of those pixels are then returned. """
    epsilon_snap = 20  # magic number 20 from pape
    results = []
    for l in (ll, lr):
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
    height, width, depth = image.shape
    ml, mr = (0, height), (0, height)
    for y in range(height - 1):
        for x in range(width - 1):
            if sum(image[y, x]) != 0:
                if x < mid and y < ml[1]:
                    ml = (x, y)
                elif x >= mid and y < mr[1]:
                    mr = (x, y)
    return ml, mr


def color_treshold(image):
    # color thresholding
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color = 145 // 2  # green to hue
    dx = 30
    lower_green = np.array([max(0, color-dx), 100, 100])
    upper_green = np.array([max(0, color+dx), 255, 255])
    mask = cv2.inRange(image_hsv, lower_green, upper_green)
    if mask.max() == 0:
        raise Exception('Could not detect any green')
    return mask


def smooth_image(image):
    kernel = np.ones((10, 10), np.uint8)  # magic number 10 from paper
    image = cv2.erode(image, kernel)
    image = cv2.dilate(image, kernel)
    return image

def tarvas_geometric(raw_image, visualize):
    f = 0.3  # in the paper 1/3 is used
    image = cv2.resize(raw_image, (0, 0), fx=f, fy=f)
    mask = color_treshold(image)
    mask = smooth_image(mask)
    masked = cv2.bitwise_and(image, image, mask=mask)
    ll, lr = lower_corner(masked)
    al, ar = highest_corner(masked, ll, lr)
    mid = (ll[0]+lr[0])/2+5  # Offset produced slightly better results
    sl, sr = get_weighted_edges(masked, mid)
    ml, mr = get_minima(masked, mid)
    points = [ll, al, sl, ml, mr, sr, ar, lr]
    np_points = np.array(points)
    overlay = image.copy()
    cv2.fillPoly(overlay, np.int32([np_points]), (255, 255, 255))
    image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
    # visualize results
    if visualize:
        for p in points:
            cv2.circle(masked, p, 4, (255, 0, 0), 3)
        cv2.line(masked, (mid, 0), (mid, 10000), (0, 0, 255))
        masked = cv2.addWeighted(overlay, 0.3, masked, 0.7, 0)
        cv2.imshow('original', raw_image)
        cv2.imshow('masked', masked)
        cv2.imshow('result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return image, masked


def test_image():
    img = cv2.imread('images/1.jpg', cv2.IMREAD_COLOR)
    tarvas_geometric(img, True)


def test_video():
    cap = cv2.VideoCapture('video/vid2.mp4')
    factor = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is None or frame is None:
            break
        try:
            tarvas = frame
            tarvas, _ = tarvas_geometric(frame, False)
            tarvas = cv2.resize(tarvas, (0, 0), fx=factor, fy=factor)
        except:
            print('error')
        cv2.imshow('frame', tarvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

stored_masked = None
def analyse_image(image):
    global stored_masked
    _, stored_masked = tarvas_geometric(image, False)

def check_point(x, y):
    global stored_masked
    if sum(stored_masked[y, x]) != 0:
        return True
    else:
        return False



if __name__ == '__main__':
    #test_image()
    analyse_image(cv2.imread('images/1.jpg', cv2.IMREAD_COLOR))
    print(check_point(0, 0))
