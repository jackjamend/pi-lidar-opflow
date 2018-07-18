import queue
import time
import cv2
import numpy as np
import os
import csv
import datetime
from termcolor import colored

from SensorThread import SensorThread
from AnalyzeThread import AnalyzeThread
from OverlayThread import OverlayThread


class DroneData:
    def __init__(self, resolution, reduction, show_image=False, verbose=False):
        # Records variables given from constructor
        self.resolution = resolution
        self.reduction = reduction
        self.verbose = verbose
        self.show_image = show_image

        # Creates queues. The first three are to communicate between the
        # threads. The last two are to output data after the program has
        # terminated.
        self.frame_q = queue.Queue()
        self.analyze_q = queue.Queue()
        self.overlay_q = queue.Queue()
        self.screen_shots_q = queue.Queue()
        self.csv_q = queue.Queue()

        # Initializes threads and puts them into an array.
        self.sensor = SensorThread(self.frame_q, name='pi_frame')
        self.analyze = AnalyzeThread(self.frame_q, self.analyze_q,
                                     name='analyze')
        self.overlay = OverlayThread(self.analyze_q, self.overlay_q,
                                     resolution=self.resolution,
                                     reduction=self.reduction, name='overlay')

        self.threads = [self.sensor, self.analyze, self.overlay]
        for thread in self.threads:
            thread.setDaemon(True)

        # Gives variables to create a folder to record data
        self.image_folder_path = "./data/screen-shots"
        self.csv_file = './data/drone-data.csv'
        self._setup()

        # Variables used for the CSV file
        self.file = open(self.csv_file, 'w')
        self.writer = csv.writer(self.file)
        self.image_number = 1

        # Other variables to record current state of the drone's safety.
        self.passed_safety_zone = False
        self.lookup = []
        self.scores = []

    def _setup(self):
        """Creates a directory from the current location called data with a 
        sub-directory called screen-shots. This is where the data will be 
        saved. If a directory with the same name already exists, 
        the directory will not be deleted, instead the information will be 
        written into the folder."""
        os.popen('mkdir -p %s' % self.image_folder_path)
        os.popen('touch ' + self.csv_file)

    def run(self):
        """Runs the program. Starts the threads and then begins processing 
        data"""
        for thread in self.threads:
            thread.start()
            time.sleep(.1)
        time.sleep(2)
        print('Started!')
        frame = None
        while True:
            # Creates a time string for every iteration
            time_string = datetime.datetime.time(
                datetime.datetime.now()).strftime('%H:%M:%S')

            # Condition is true once a frame has been processed by all three
            #  threads.
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

                try:  # See if there is away to get rid of the try block
                    cv2.putText(frame, 'Safe Travel Zone: %d' %
                                self.overlay.travel_zone,
                                (20, 40), cv2.FONT_HERSHEY_PLAIN, 1.0,
                                (0, 100, 0), lineType=cv2.LINE_AA)
                except IndexError or TypeError:
                    continue

                if self.show_image:
                    # Try block used because sometimes cv2 throws an error
                    # for no obvious reason. Generally happens when large
                    # movements happen close to the camera
                    try:
                        cv2.imshow("Camera Feed", frame)
                    except cv2.error:
                        pass

            # Condition checks if the lidar reported that the drone is
            # within the safety zone and if the drone was previously in
            # the safety zone
            if in_danger_zone and not self.passed_safety_zone and\
                    frame is not None:
                print(colored("Object within LiDAR threshold", 'red'))
                print('Safe zone: %d' % self.overlay.travel_zone)

                # Changes the state of the drone to no longer in a safety zone.
                self.passed_safety_zone = True

                # Puts data in the queues to write them later
                self.screen_shots_q.put((self.image_folder_path +
                                         '/unsafe-screen-shot' + time_string
                                         + '--' + str(self.image_number) +
                                         '.jpeg', frame))
                self.csv_q.put((self.image_number, time_string,
                                'in danger zone', lidar_value,
                                self.overlay.travel_zone, self.scores,
                                np.transpose(self.lookup).flatten()))

            # Checks if the the drone was previosuly not in the safet zone
            # and the lidar is no longer reporting there is an object in the
            #  danger zone
            elif self.passed_safety_zone and not in_danger_zone:
                print(colored("Object outside of LiDAR threshold\n", 'green'))
                self.screen_shots_q.put((self.image_folder_path +
                                         '/safe-screen-shot' + time_string
                                        + '--' + str(self.image_number) +
                                         '.jpeg', frame))
                self.csv_q.put((self.image_number, time_string,
                                'out of danger zone', lidar_value,
                                self.overlay.travel_zone, self.scores,
                                np.transpose(self.lookup).flatten()))
                self.image_number += 1
                self.passed_safety_zone = False

            # Checks to see if the escape key was pressed in order to exit
            # the program. NOTE: This only works when the frame is being
            # displayed and selected
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    def close(self):
        """Calls methods to close the program"""
        self._write_file()
        self._kill_threads()

    def _write_file(self):
        """Writes information from saved queues to the CSV file created 
        earlier and then saves the screen shots to the /data/screen-shot 
        directory."""
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

    def _kill_threads(self):
        """Kills all the threads in the program."""
        print('Closing threads...')
        for thread in self.threads:
            thread.join(5)
            print('Thread %s closed!' % thread.getName(), flush=True)
        print('Closed!')
