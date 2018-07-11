import threading
import queue
import cv2

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


class OverlayThread(threading.Thread):
    def __init__(self, analyze_q: queue.Queue, overlay_q: queue.Queue,
                 resolution, reduction):
        super(OverlayThread, self).__init__()
        self.stop_request = threading.Event()
        self.analyze_q = analyze_q
        self.overlay_q = overlay_q
        self.rect_corners_top_bottom = self.set_rect_coors(resolution,
                                                           reduction)

    def run(self):
        while not self.stop_request.isSet():
            while not self.analyze_q.empty():
                frame, tracks = self.analyze_q.get()
                output = self.image_with_boxes(frame, tracks, show_image=False)
                self.overlay_q.put(output)

    def join(self, timeout=None):
        self.stop_request.set()
        super(OverlayThread, self).join(timeout)

    '''Set up the cordinates for the top left of rectangles and bottom 
    right.'''

    def set_rect_coors(self, resolution, reduction):
        rect_coords = self.rect_coordinates(resolution, reduction)
        rect_corners = self.rect_corners(rect_coords)
        return rect_corners

    def rect_coordinates(self, resolution, reduction):
        width, height = resolution
        x_points = []
        y_points = []
        for i in range(reduction + 1):
            x_points.append(int(i / reduction * width))
            y_points.append(int(i / reduction * height))
        return x_points, y_points

    def rect_corners(self, rect_coordinates):
        x_points, y_points = rect_coordinates
        coords = []
        for i in range(len(x_points) - 1):
            for j in range(len(y_points) - 1):
                point = (
                    (x_points[j], y_points[i], x_points[j + 1],
                     y_points[i + 1]))
                coords.append(point)
        # print('coords:',coords)
        return coords

    '''Analyze the image to overlay with boxes'''

    def image_with_boxes(self, image, tracks, show_image=True):
        # If there are no points to track, return
        if len(tracks) <= 0:
            return
        new_image = image.copy()

        # finds corners and retrieves x y points
        corner_coordinates = self.get_coordinates_of_corners(tracks)
        fill_array = self.create_fill_in_array(self.rect_corners_top_bottom,
                                               corner_coordinates)
        self.overlay_image(new_image, self.rect_corners_top_bottom, fill_array)
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
