import threading
from lidar_lite import Lidar_Lite as lidar


class LidarThread(threading.Thread):
    def __init__(self, name=None):
        super(LidarThread, self).__init__(name=name)
        self.stop_request = threading.Event()
        self.lidar = lidar()
        connect = self.lidar.connect(1)
        if connect < -1:
            raise Exception("No LiDAR found")
        self.lidar.setThreshold(100)
        self.current_value = None
        self.in_danger_zone = False

    def run(self):
        while not self.stop_request.isSet():
            self.current_value = self.lidar.getDistance()
            if self.current_value < self.lidar.thresh:
                self.in_danger_zone = True
            else:
                self.in_danger_zone = False

    def join(self, timeout=None):
        self.stop_request.set()
        super(LidarThread, self).join(timeout)