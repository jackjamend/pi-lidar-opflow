import threading, queue
import lidar_lite as lidar

class LidarThread(threading.Thread):

    def __init__(self, high_value_q: queue.Queue):
        super(LidarThread, self).__init__()
        self.stop_request = threading.Event()
        self.high_value_q = high_value_q
        self.lidar = lidar()
        self.lidar.setThreshold(100)

    def run(self):
        while not self.stop_request.isSet():
            value = self.lidar.getDistance()
            if value < self.lidar.thresh:
                self.high_value_q.put(value)


    def join(self,timeout=None):
        self.stop_request.set()
        super(LidarThread, self).join(timeout)