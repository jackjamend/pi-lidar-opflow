import queue
import time
import cv2
import numpy as np
# from termcolor import colored

from PiFrameThread import PiFrameThread
from AnalyzeThread import AnalyzeThread
from OverlayThread import OverlayThread
from LidarThread import LidarThread


class DroneData:
    def __init__(self, resolution, reduction):
        self.frame_q = queue.Queue()
        self.analyze_q = queue.Queue()
        self.overlay_q = queue.Queue()
        self.lidar_q = queue.Queue()

        self.lidar = LidarThread(self.lidar_q, name='lidar')
        self.pi_frame = PiFrameThread(self.frame_q, name='pi_frame')
        self.analyze = AnalyzeThread(self.frame_q, self.analyze_q,
                                     name='analyze')
        self.overlay = OverlayThread(self.analyze_q, self.overlay_q,
                                     resolution=resolution,
                                     reduction=reduction, name='overlay')
        self.threads = [self.lidar, self.pi_frame, self.analyze,
                        self.overlay]
        for thread in self.threads:
            thread.setDaemon(True)
        self.lookup = []
        self.verbose = True

    def run(self):
        self.pi_frame.start()
        time.sleep(.1)
        self.analyze.start()
        time.sleep(.1)
        self.overlay.start()
        self.lidar.start()
        while True:
            if not self.overlay_q.empty():
                frame, self.lookup = self.overlay_q.get()
                if self.verbose:
                    display = ['Total frames in frame_q: %d' %
                               self.frame_q.qsize(),
                               'Total frames in analyze_q: %d' %
                               self.analyze_q.qsize(),
                               'Total frames in overlay_q: %d' %
                               self.overlay_q.qsize()]
                    for value in display:
                        cv2.putText(frame,
                                    value, (20, 20 * (display.index(value)+1)),
                                    cv2.FONT_HERSHEY_PLAIN, 1.0,
                                    (255, 255, 255),
                                    lineType=cv2.LINE_AA)

                    if self.lidar.current_value is not None:
                        cv2.putText(frame,
                                    'Current LiDAR Distance: %d' %
                                    self.lidar.get_current(), (20, 80),
                                    cv2.FONT_HERSHEY_PLAIN, 1.0,
                                    (255, 255, 255), lineType=cv2.LINE_AA)
                self.yaw()
                # try:
                #     cv2.imshow("Camera Feed", frame)
                # except cv2.error:
                #     # print("Whoops, cv2 error!")
                #     pass
            if not self.lidar_q.empty():
                # print(colored("Object within LiDAR threshold", 'yellow'))
                self.move()
                with self.lidar_q.mutex:
                    self.lidar_q.queue.clear()

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    def close(self):
        # print(self.overlay.history)
        self.kill_threads()

    def kill_threads(self):
        print('Closing threads...')
        for thread in self.threads:
            thread.join(5)
            if thread.is_alive():
                print('Thread %s closed!' % thread.getName())
            else:
                print('Thread %s not closed!' % thread.getName())
        print('Closed')

    def yaw(self):
        max_movement = np.unravel_index(np.argmax(self.lookup),
                                        self.lookup.shape)
        if max_movement[0] < 3:
            print('left', flush=True)
        elif max_movement[0] > 4:
            print('right', flush=True)

    def move(self):
        direction = self.overlay.travel_zone
        if direction == 1:
            print(0, flush=True)
        elif direction == 2:
            print(30, flush=True)
        elif direction == 0:
            print(330, flush=True)
