import queue
import time
import cv2
import numpy as np
import os
import csv
import datetime
from termcolor import colored

from PiFrameThread import PiFrameThread
from AnalyzeThread import AnalyzeThread
from OverlayThread import OverlayThread


class DroneData:
    def __init__(self, resolution, reduction, show_image = False):
        self.frame_q = queue.Queue()
        self.analyze_q = queue.Queue()
        self.overlay_q = queue.Queue()
        self.screen_shots_q = queue.Queue()
        self.csv_q = queue.Queue()

        self.pi_frame = PiFrameThread(self.frame_q, name='pi_frame')
        self.analyze = AnalyzeThread(self.frame_q, self.analyze_q,
                                     name='analyze')
        self.overlay = OverlayThread(self.analyze_q, self.overlay_q,
                                     resolution=resolution,
                                     reduction=reduction, name='overlay')
        self.threads = [self.pi_frame, self.analyze, self.overlay]
        for thread in self.threads:
            thread.setDaemon(True)
        self.lookup = []
        self.scores = []
        self.verbose = True
        self.image_folder = "./data/screen-shots"
        self.csv_file = './data/drone-data.csv'
        self._setup()
        self.image_number = 1
        self.passed_safety_zone = False
        self.file = open(self.csv_file, 'w')
        self.writer = csv.writer(self.file)
        self.show_image = show_image

    def _setup(self):
        os.popen('mkdir -p %s' % self.image_folder)
        os.popen('touch ' + self.csv_file)

    def run(self):
        self.pi_frame.start()
        time.sleep(.1)
        self.analyze.start()
        time.sleep(.1)
        self.overlay.start()
        time.sleep(2)
        print('Started!')
        frame = None
        while True:
            time_string = datetime.datetime.time(
                datetime.datetime.now()).strftime('%H:%M:%S')
            if not self.overlay_q.empty():
                frame, self.lookup, self.scores, lidar = self.overlay_q.get()
                lidar_value, in_danger_zone = lidar
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

                cv2.putText(frame, 'Current LiDAR Distance: %d' % lidar_value,
                            (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 100, 0),
                            lineType=cv2.LINE_AA)
                try:
                    cv2.putText(frame, 'Safe Travel Zone: %d' %
                                self.overlay.travel_zone,
                                (20, 40), cv2.FONT_HERSHEY_PLAIN, 1.0,
                                (0, 100, 0), lineType=cv2.LINE_AA)
                except IndexError:
                    continue
                except TypeError:
                    continue

                if self.show_image:
                    try:
                        # print('image displayed')
                        cv2.imshow("Camera Feed", frame)
                    except cv2.error:
                        # print("Whoops, cv2 error!")
                        pass

            if in_danger_zone and not self.passed_safety_zone and\
                    frame is not None:
                print(colored("Object within LiDAR threshold", 'red'))
                self.screen_shots_q.put((self.image_folder +
                                         '/unsafe-screen-shot' + time_string
                                         + '--' +
                                        str(self.image_number)+'.jpeg', frame))
                self.csv_q.put((time_string, 'in danger zone',
                                lidar_value, self.overlay.travel_zone,
                                self.scores,
                                np.transpose(self.lookup).flatten()))
                self.passed_safety_zone = True
                print('Safe zone: %d' % self.overlay.travel_zone)

            elif self.passed_safety_zone and not in_danger_zone:
                print(colored("Object outside of LiDAR threshold\n", 'green'))
                self.screen_shots_q.put(
                    (self.image_folder + '/safe-screen-shot' + time_string
                     + '--' + str(self.image_number) + '.jpeg', frame))
                self.csv_q.put((time_string, 'out of danger zone',
                                lidar_value, self.overlay.travel_zone,
                                self.scores,
                                np.transpose(self.lookup).flatten()))
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
        print('writing csv file...')
        while not self.csv_q.empty():
            self.writer.writerow(self.csv_q.get())
        self.file.close()
        print('Done!')
        print('Saving images...')
        count = 0
        size = self.screen_shots_q.qsize()
        while not self.screen_shots_q.empty():
            name, img = self.screen_shots_q.get()
            cv2.imwrite(name, img)
            count += 1
            print('Image %d saved oud of %d!' % (count, size))
        print('All images saved!')

    def kill_threads(self):
        print('Closing threads...')
        for thread in self.threads:
            thread.join(5)
            if thread.is_alive():
                print('Thread %s closed!' % thread.getName())
            else:
                print('Thread %s not closed!' % thread.getName())
        print('Closed!')

