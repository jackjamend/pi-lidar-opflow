from lidar_lite import Lidar_Lite
from time import time as timer


class LiteTTC:
    def init(self, threshold=100):
        self.lidar = Lidar_Lite()
        connected = self.lidar.connect(1)
        self.lidar.setThreshold(threshold)
        if connected < -1:
            print("Not Connected")

    def start(self, running):
        start_time = timer()
        current_distance = self.lidar.getDistance() / 100
        while running:
            previous_distance = current_distance
            prev_time = start_time
            start_time = timer()
            current_distance = self.lidar.getDistance() / 100
            self.ttc(prev_time, start_time, current_distance,
                     previous_distance)

    def _ttc(self, prev_t, start_t, current_d, prev_d):
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

if __name__ == '__main__':
    lite_ttc = LiteTTC()
    lite_ttc.start(True)
