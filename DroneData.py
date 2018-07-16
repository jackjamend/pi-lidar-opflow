import queue
import time
import cv2
import numpy as np
import os
import csv
import datetime
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
        self.screen_shots_q = queue.Queue()
        self.csv_q = queue.Queue()

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
        self.scores = []
        self.verbose = True
        self.image_folder = "./data/screen-shots"
        self.data_folder = ""
        self._setup()
        self.image_number = 1
        self.passed_safety_zone = False
        self.csv_file = './data/drone-data'
        self.file = open(self.csv_file, 'w')
        self.writer = csv.writer(self.file)

    def _setup(self):
        os.popen('mkdir -p %s' % self.image_folder)


    def run(self):
        self.pi_frame.start()
        time.sleep(.1)
        self.analyze.start()
        time.sleep(.1)
        self.overlay.start()
        self.lidar.start()
        while True:
            if not self.overlay_q.empty():
                frame, self.lookup, self.scores = self.overlay_q.get()
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
                                self.lidar.current_value, (20, 20),
                                cv2.FONT_HERSHEY_PLAIN, 1.0,
                                (255, 255, 255), lineType=cv2.LINE_AA)
                cv2.putText(frame, 'Safe Travel Zone: %d' %
                            int(self.overlay.travel_zone), (20, 40),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255),
                            lineType=cv2.LINE_AA)
                try:
                    cv2.imshow("Camera Feed", frame)
                except cv2.error:
                    # print("Whoops, cv2 error!")
                    pass

            if not self.lidar_q.empty() and self.lidar.in_danger_zone:
                # print(colored("Object within LiDAR threshold", 'yellow'))
                cv2.imwrite(self.image_folder + '/unsafe-screen-shot' +
                            str(self.image_number), frame)
                self.passed_safety_zone = True
                self.csv_q.put((datetime.datetime.time(
                                datetime.datetime.now()).strftime(
                                '%H:%M:%S'), 'in danger zone',
                                self.lidar_q.get(),
                                self.overlay.travel_zone, self.scores[0] if
                                self.scores[0] < self.scores[2] else
                                self.scores[2], self.lookup.flatten()))

                print('Safe zone: %d' % self.scores[0] if
                                self.scores[0] < self.scores[2] else
                                self.scores[2])
                # Empty the LiDAR Queue
                with self.lidar_q.mutex:
                    self.lidar_q.queue.clear()
            elif self.passed_safety_zone and not self.lidar.in_danger_zone:
                cv2.imwrite(self.image_folder + '/safe-screen-shot' +
                            str(self.image_number), frame)
                self.csv_q.put((datetime.datetime.time(
                    datetime.datetime.now()).strftime(
                    '%H:%M:%S'), 'out of danger zone',
                                self.lidar_q.get(),
                                self.overlay.travel_zone, self.scores[0] if
                                self.scores[0] < self.scores[2] else
                                self.scores[2], self.lookup.flatten()))
                self.image_number += 1
                self.passed_safety_zone = False

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    def close(self):
        # print(self.overlay.history)
        self._write_file()
        self.kill_threads()

    def _write_file(self):
        while not self.csv_q.empty():
            self.writer.writerow(self.csv_q.get())
        self.writer.close()
        self.file.close()

    def kill_threads(self):
        print('Closing threads...')
        for thread in self.threads:
            thread.join(5)
            if thread.is_alive():
                print('Thread %s closed!' % thread.getName())
            else:
                print('Thread %s not closed!' % thread.getName())
        print('Closed')

