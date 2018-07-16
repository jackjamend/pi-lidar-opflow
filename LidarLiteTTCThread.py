import threading, queue
import time
from lidar_lite import Lidar_Lite as lidar


class LidarLiteTTCThread(threading.Thread):
    def __init__(self, high_value_q: queue.Queue, name=None):
        super(LidarLiteTTCThread, self).__init__(name=name)
        self.stop_request = threading.Event()
        self.high_value_q = high_value_q
        self.lidar = lidar()
        connect = self.lidar.connect(1)
        if connect < -1:
            raise Exception("No LiDAR found")
        self.lidar.setThreshold(100)
        self.current_value = None

    def run(self):
        start_time = time.time()
        current_distance = self.lidar.getDistance() / 100
        while not self.stop_request.isSet():
            previous_distance = current_distance
            prev_time = start_time
            start_time = time.time()
            current_distance = self.lidar.getDistance() / 100
            self.ttc(prev_time, start_time, current_distance,
                     previous_distance)

    def ttc(self, prev_t, start_t, current_d, prev_d):
        elapsed_time = start_t-prev_t
        # print(elapsed_time)
        distance_moved = prev_d-current_d
        # print(distance_moved)
        if distance_moved > .035 or distance_moved < -.035:
            velocity = distance_moved / elapsed_time
            if velocity > 0:
                current_ttc = current_d/velocity
                print("Current ttc is %d seconds; speed is %d mps..." %
                      (current_ttc, velocity))
        else:
            print("there is no current ttc available: Object is not moving or "
                  "is moving away...")

    def get_current(self):
        value = self.current_value
        self.current_value = None
        return value

    def join(self, timeout=None):
        self.stop_request.set()
        super(LidarLiteTTCThread, self).join(timeout)