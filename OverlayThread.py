# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15, 2018

@author: Jack J Amend

Inherits from the Thread class. Takes the information from the analyze 
queue. The information is then taken and an overlay frame is created to 
identify the regions where the points are located.
"""
import queue
import threading

import cv2
import numpy as np
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


class OverlayThread(threading.Thread):
    def __init__(self, analyze_q: queue.Queue, overlay_q: queue.Queue,
                 resolution, reduction, name=None):
        """
        Initializes an instance of an overlay thread. Checks list of points 
        and creates a table that is then displayed as an overlay on the frame.
        
        :param analyze_q: 
            queue that holds the frame, tracks, and lidar information.
        :param overlay_q: 
            queue that contains the overlay frame, the table with the 
            points, the scores for each zone, and the LiDAR data.
        :param resolution: 
            a tuple of the number of pixels as height by width.
        :param reduction: 
            the factor to reduce the frame size by.
        :param name: 
            name of the thread.
        """
        super(OverlayThread, self).__init__(name=name)
        self.stop_request = threading.Event()
        self.analyze_q = analyze_q
        self.overlay_q = overlay_q
        self.reduction = reduction
        self.resolution = resolution
        self.dx = resolution[0] // reduction
        self.dy = resolution[1] // reduction
        self.lookup = np.zeros((reduction, reduction))
        self.history = np.zeros((reduction, reduction))
        self.travel_zone = 1
        self.scores = []

    def run(self):
        while not self.stop_request.isSet():
            while not self.analyze_q.empty():
                # start = time.time()
                frame, tracks, lidar = self.analyze_q.get()
                _, danger_zone = lidar
                output = self._image_with_boxes(frame, tracks,
                                                show_image=False)
                self.overlay_q.put((output, self.lookup, self.scores, lidar))
                if danger_zone:
                    self.find_zone()
                    self.history *= .95
                # print('Overlay thread ran for %.2f seconds and %d tracks' %
                #       ((time.time()-start), len(tracks)))

    def join(self, timeout=None):
        self.stop_request.set()
        super(OverlayThread, self).join(timeout)

    '''Analyze the image to overlay with boxes'''

    def _image_with_boxes(self, image, tracks, show_image=True):
        # If there are no points to track, return
        if len(tracks) <= 0:
            return
        new_image = image.copy()

        # finds corners and retrieves x y points
        corner_coordinates = self._get_coordinates_of_corners(tracks)
        self._create_fill_in_array(corner_coordinates)
        self._overlay_image(new_image)
        if show_image:
            cv2.imshow('Show image option window', new_image)
        return new_image

    def _get_coordinates_of_corners(self, tracks, full_track=True):
        coordinates = []
        '''Changed good_tracks from self.tracks'''
        # good_tracks = self.good_tracks()
        for track in tracks:
            # May need to adjust this line to account for past path
            # Right now, looks at most recent
            if full_track and len(track) > 2:
                x, y = track[0]
                coordinates.append((x, y))

            x, y = track[len(track) - 1]
            coordinates.append((x, y))
        return coordinates

    def _create_fill_in_array(self, points):
        width, height = self.dx, self.dy

        for point in points:
            px, py = point
            x_sector = px // width
            y_sector = py // height
            if x_sector != 8 and y_sector != 8:
                self.lookup[x_sector][y_sector] += 1
                self.history[x_sector][y_sector] += 1

    def _overlay_image(self, image):
        overlay = image.copy()
        for index, x in np.ndenumerate(self.lookup):
            top_x = index[0] * (self.resolution[0] // self.reduction)
            top_y = index[1] * (self.resolution[1] // self.reduction)
            bottom_x = top_x + (self.resolution[0] // self.reduction)
            bottom_y = top_y + (self.resolution[1] // self.reduction)
            cv2.rectangle(image, (top_x, top_y), (bottom_x, bottom_y),
                          (0, 0, 0), 1)  # Grid Lines
            if x:
                cv2.rectangle(overlay, (top_x, top_y), (bottom_x, bottom_y),
                              colors[2], -1)
        alpha = .4
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    def _find_zone(self):
        zones = np.split(self.lookup, [3, 5])
        # zones = np.delete(zones, 0, 1)
        self.scores = []
        for zone in zones:
            self.scores.append(np.sum(zone) / np.size(zone))
        self.travel_zone = np.argmin(np.delete(self.scores, 1)) * 2
        self.lookup = np.zeros((self.reduction, self.reduction))
