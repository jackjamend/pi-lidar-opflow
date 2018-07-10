# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 11:28:59 2018

@author: Jack J Amend
"""

'''
Optical flow using openCV
====================

Adapted from openCV example 
(https://github.com/opencv/opencv/blob/master/samples/python/lk_track.py). 
Class file to find various points of interest and track them. Using the points, 
identify areas as occupied and overlays a red rectangle on section. To stop, 
press the ESC key. This file should not be run, instead use the controller 
file to keep everything nice and organized.
'''

import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import os
import math

# Parameter for Lucas Kanade optical flow
lk_params = dict(winSize=(25, 25),
                 maxLevel=1,
                 criteria=(cv2.TERM_CRITERIA_EPS |
                           cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for ShiTomasi corner detection
feature_params = dict(maxCorners=50,
                      qualityLevel=0.5,
                      minDistance=10,
                      blockSize=5)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


class App:
    def __init__(self, video_src, make_file=False, plot_graphs=False,
                 full_track=False, reduction=15):
        self.track_len = 15
        self.detect_interval = 5
        self.tracks = []
        self.cam = cv2.VideoCapture(video_src)
        self.frame_idx = 0
        self.create_file = make_file
        self.full_track = full_track
        if self.create_file:
            a = time.strptime(time.asctime(time.localtime()))
            form_time = '-'.join([str(a.tm_mon), str(a.tm_mday),
                                  str(a.tm_year), str(a.tm_hour),
                                  str(a.tm_min), str(a.tm_sec), ])
            self.file = open("data_" + form_time + ".txt", 'w+')
        self.plotting = plot_graphs
        self.rect_corners_top_bottom = []
        self.reduction = reduction
        self.setup()
        self.fbgb = cv2.createBackgroundSubtractorMOG2()
        ''' cv2.createBackgroundSubtractorMOG2()'''

    def close(self):
        if self.plotting:
            plt.close('all')
        if self.create_file:
            self.close_file()
        cv2.destroyAllWindows()

    def close_file(self):
        self.file.close()
        self.cam.release()

    def plot_graph(self):
        plt.figure(self.frame_idx - 1 % 10)
        fig = plt.gcf()
        plt.ylim((720, 0))
        plt.xlim((0, 1280))
        for track in self.tracks:
            if len(track) == 1:
                x, y = track[0]
                plt.scatter(x, y)
            else:
                x = []
                y = []
                for values in track:
                    x.append(values[0]), y.append(values[1])
                plt.plot(x, y)
        # plt.show()
        try:
            fig.savefig('./graph_pics/plot' + str(
                int((int(self.frame_idx) - 1) / 10)) + '.png', dpi=fig.dpi)
        except FileNotFoundError:
            os.system("mkdir ./graph_pics")
            fig.savefig('./graph_pics/plot' + str(
                int((int(self.frame_idx) - 1) / 10)) + '.png', dpi=fig.dpi)

    def write_file(self):
        self.file.write('[')
        for i in range(len(self.tracks)):
            self.file.write(str(self.tracks[i]))
            if i == len(self.tracks) - 1:
                self.file.write(']')
            else:
                self.file.write(',')
        self.file.write('\n')

    def analyze(self):
        # I think this was going to be used to find line of best fit
        point_list = []
        for tracks in self.tracks:
            if len(self.tracks) > 8:
                point_list.append(tracks)
                # point_list

    def good_tracks(self):
        good_tracks = []
        for track in self.tracks:
            if len(track) > 8:
                point1 = track[0]
                point2 = track[len(track) - 1]
                distance = self.distance(point1, point2)
                if distance > (.05 * self.width):
                    good_tracks.append(track)
            else:
                good_tracks.append(track)
        return good_tracks

    def distance(self, point1, point2):
        x1, y1 = point1
        x2, y2, = point2
        x_sqrt = math.pow((x2 - x1), 2)
        y_sqrt = math.pow((y2 - y1), 2)
        return math.sqrt(x_sqrt + y_sqrt)

    def image_with_boxes(self, image, show_image=True):
        # If there are no points to track, return
        if len(self.tracks) <= 0:
            return
        new_image = image.copy()

        # finds corners and retrieves x y points
        corner_coordinates = self.get_coordinates_of_corners()
        fill_array = self.create_fill_in_array(self.rect_corners_top_bottom,
                                               corner_coordinates)
        self.overlay_image(new_image, self.rect_corners_top_bottom, fill_array)
        if show_image:
            cv2.imshow('image 5', new_image)
        return new_image

    def get_coordinates_of_corners(self):
        coordinates = []
        '''Changed good_tracks from self.tracks'''
        # good_tracks = self.good_tracks()
        for track in self.tracks:
            # May need to adjust this line to account for past path
            # Right now, looks at most recent
            if self.full_track:
                x, y = track[0]
                coordinates.append((x, y))

            x, y = track[len(track) - 1]
            coordinates.append((x, y))
        return coordinates

    def rect_coordinates(self, image, reduction):
        height, width, channels = image.shape
        x_points = []
        y_points = []
        for i in range(reduction + 1):
            x_points.append(int(i / reduction * width))
            y_points.append(int(i / reduction * height))
        return (x_points, y_points)

    def rect_corners(self, rect_coordinates):
        x_points, y_points = rect_coordinates
        coords = []
        for i in range(len(x_points) - 1):
            for j in range(len(y_points) - 1):
                point = (
                (x_points[j], y_points[i], x_points[j + 1], y_points[i + 1]))
                coords.append(point)
        # print('coords:',coords)
        return coords

    def create_fill_in_array(self, rect_corners, points):
        rect_fill = []
        for rect in rect_corners:
            for point in points:
                px, py = point
                rx1, ry1, rx2, ry2 = rect
                if px >= rx1 and px <= rx2 and py >= ry1 and py <= ry2:
                    rect_fill.append(rect)
                    break
        return rect_fill

    def overlay_image(self, image, top_bottom_rect, fill_rects):
        for rect in top_bottom_rect:
            rx1, ry1, rx2, ry2 = rect
            cv2.rectangle(image, (rx1, ry1), (rx2, ry2), (0, 0, 0), 1)

        color_index = 0
        overlay = image.copy()
        for rect in fill_rects:
            rx1, ry1, rx2, ry2 = rect
            # color_index%len(colors) to change colors
            cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), colors[2], -1)
            color_index += 1
        alpha = .4
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    def set_rect_coors(self, frame, reduction):
        rect_coords = self.rect_coordinates(frame, reduction)
        rect_corners = self.rect_corners(rect_coords)
        self.rect_corners_top_bottom = rect_corners

    def setup(self):
        ret, frame = self.cam.read()
        self.height, self.width, self.channels = frame.shape
        self.set_rect_coors(frame, self.reduction)

    def run(self):
        start = time.time()
        while True:
            ret, frame = self.cam.read()
            ''' Edits for cropping video '''
            # height, width, channels = frame.shape
            # center_width = int(width / 2)
            # frame = frame[int(height * .10):int(height * .90),
            # int(center_width * .65):int(center_width * 1.35)]
            ''' End Edits '''
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            '''Background subtraction Edits'''
            frame_gray = self.fbgb.apply(frame)
            ''' End Edits'''
            vis = frame.copy()

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1,
                                                                        2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None,
                                                       **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None,
                                                        **lk_params)
                d = abs(p0 - p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks,
                                                 p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False,
                              (100, 255, 0))
                cv2.putText(vis, 'track count: %d' % len(self.tracks),
                            (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.0,
                            (255, 255, 255), lineType=cv2.LINE_AA)
                cv2.putText(vis, 'fps: %d' % int(
                    self.frame_idx / (time.time() - start)), (20, 40),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255),
                            lineType=cv2.LINE_AA)
                cv2.putText(vis, 'total frames: %d' % int(self.frame_idx),
                            (20, 60), cv2.FONT_HERSHEY_PLAIN,
                            1.0, (255, 255, 255), lineType=cv2.LINE_AA)
            print('before', len(self.tracks), end=' ')
            # self.good_tracks()
            print('after', len(self.tracks))
            # First time will evaluate as true
            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                # Mask is created of same size as frame_gray with all values
                # set to 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    # print('inside weird for idx',self.frame_idx,'track',
                    # self.tracks)
                    cv2.circle(mask, (x, y), 5, 0, -1)
                # p is assigned cordinate of corners to track
                p = cv2.goodFeaturesToTrack(frame_gray, mask=mask,
                                            **feature_params)
                # print('p', p)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])

            self.frame_idx += 1
            self.prev_gray = frame_gray
            vis = self.image_with_boxes(vis, False)

            if ret:
                try:
                    cv2.imshow('Drone Cam', vis)
                except cv2.error:
                    print("Problem showing the frame")
                    pass

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

            if self.create_file:
                self.write_file()
            if self.plotting and (int(self.frame_idx) - 1) % 10 == 0:
                self.plot_graph()


if __name__ == '__main__':
    print('Oops! This is the wrong file. Try running controller!')
