import threading, queue
import cv2


class FrameThread(threading.Thread):

    def __init__(self, frame_q: queue.Queue):
        super(FrameThread, self).__init__()
        self.stop_request = threading.Event()
        # Camera
        self.cam = cv2.VideoCapture(0)
        self.frame_q = frame_q
        # LiDAR
        self.lidar = self.setup_lidar(100)
        self.current_value = None
        self.in_danger_zone = False

    def run(self):
        while not self.stop_request.isSet():
            ret, frame = self.cam.read()
            self.current_value = self.lidar.getDistance()
            if self.current_value < self.lidar.thresh:
                self.in_danger_zone = True
            else:
                self.in_danger_zone = False
            self.frame_q.put((frame, self.current_value, self.in_danger_zone))

    def join(self, timeout=None):
        self.stop_request.set()
        super(FrameThread, self).join(timeout)

    def setup_lidar(self, threshold):
        from lidar_lite import Lidar_Lite as lidar
        lidar = lidar()
        connect = lidar.connect(1)
        if connect <-1:
            raise Exception("No LiDAR found")
        lidar.setThreshold(threshold)