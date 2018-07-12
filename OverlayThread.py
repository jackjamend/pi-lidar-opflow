import threading
import queue
import cv2
import time
import numpy as np
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


class OverlayThread(threading.Thread):
    def __init__(self, analyze_q: queue.Queue, overlay_q: queue.Queue,
                 resolution, reduction, name=None):
        super(OverlayThread, self).__init__(name=name)
        self.stop_request = threading.Event()
        self.analyze_q = analyze_q
        self.overlay_q = overlay_q
        self.reduction = reduction
        self.resolution = resolution
        self.dx = resolution[0]// reduction
        self.dy = resolution[1] // reduction
        self.lookup = np.zeros((reduction,reduction))
        self.history = np.zeros((reduction,reduction))
        self.travel_zone = 1

    def run(self):

        while not self.stop_request.isSet():
            while not self.analyze_q.empty():
                # start = time.time()
                frame, tracks = self.analyze_q.get()
                output = self.image_with_boxes(frame, tracks, show_image=False)
                self.overlay_q.put((output, self.lookup))
                self.find_zone()
                self.history *= .95
                # print('Overlay thread ran for %.2f seconds and %d tracks' %
                #       ((time.time()-start), len(tracks)))

    def join(self, timeout=None):
        self.stop_request.set()
        super(OverlayThread, self).join(timeout)

    '''Analyze the image to overlay with boxes'''

    def image_with_boxes(self, image, tracks, show_image=True):
        # If there are no points to track, return
        if len(tracks) <= 0:
            return
        new_image = image.copy()

        # finds corners and retrieves x y points
        corner_coordinates = self.get_coordinates_of_corners(tracks)
        self.create_fill_in_array(corner_coordinates)
        self.overlay_image(new_image)
        if show_image:
            cv2.imshow('Show image option window', new_image)
        return new_image

    def get_coordinates_of_corners(self, tracks, full_track=True):
        coordinates = []
        '''Changed good_tracks from self.tracks'''
        # good_tracks = self.good_tracks()
        for track in tracks:
            # May need to adjust this line to account for past path
            # Right now, looks at most recent
            if full_track:
                x, y = track[0]
                coordinates.append((x, y))

            x, y = track[len(track) - 1]
            coordinates.append((x, y))
        return coordinates

    def create_fill_in_array(self, points):
        width, height = self.dx, self.dy

        for point in points:
            px, py = point
            x_sector = px // width
            y_sector = py // height
            self.lookup[x_sector][y_sector] += 1
            self.history[x_sector][y_sector] += 1

    def overlay_image(self, image):
        overlay = image.copy()
        for index, x in np.ndenumerate(self.lookup):
            top_x = index[0] * (self.resolution[0] // self.reduction)
            top_y = index[1] * (self.resolution[1] // self.reduction)
            bottom_x = top_x + (self.resolution[0] // self.reduction)
            bottom_y = top_y + (self.resolution[1] // self.reduction)
            cv2.rectangle(image, (top_x, top_y), (bottom_x, bottom_y),
                          (0, 0, 0), 1) #Grid Lines
            if x:
                cv2.rectangle(overlay, (top_x, top_y), (bottom_x, bottom_y),
                              colors[2], -1)
        alpha = .4
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


    def find_zone(self):
        # print(self.lookup)
        tran = np.transpose(self.lookup)
        zones = np.split(tran, [3, 5])
        score = []
        for zone in zones:
            score.append(np.sum(zone) / np.size(zone))
        self.travel_zone = np.argmin(score)
        self.lookup = np.zeros((self.reduction, self.reduction))