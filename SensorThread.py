# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15, 2018

@author: Jack J Amend

Inherits from the Thread class. Takes the current sensor information and 
places it into a given queue that is provided during initialization. This 
thread class assumes that the camera being used is a PiCamera. 
"""
import threading
import queue
from picamera.array import PiRGBArray
from picamera import PiCamera


class SensorThread(threading.Thread):
    def __init__(self, frame_q: queue.Queue,
                 resolution=(640, 480), framerate=32, name=None):
        super(SensorThread, self).__init__(name=name)
        self.stop_request = threading.Event()
        # Camera
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.frame_q = frame_q
        # LiDAR
        self.lidar = self._setup_lidar(100)
        self.current_value = None
        self.in_danger_zone = False

    def run(self):
        while not self.stop_request.isSet():
            for image in self.camera.capture_continuous(self.rawCapture,
                                                        format="bgr",
                                                        use_video_port=True):
                frame = image.array
                self.current_value = self.lidar.getDistance()
                if self.current_value < self.lidar.thresh:
                    self.in_danger_zone = True
                else:
                    self.in_danger_zone = False
                self.frame_q.put((frame, (self.current_value,
                                  self.in_danger_zone)))
                self.rawCapture.truncate(0)
                # time.sleep(.1)

    def join(self, timeout=None):
        self.stop_request.set()
        super(SensorThread, self).join(timeout)

    def _setup_lidar(self, threshold):
        from lidar_lite import Lidar_Lite as lidar
        lidar = lidar()
        connect = lidar.connect(1)
        if connect <-1:
            raise Exception("No LiDAR found")
        lidar.setThreshold(threshold)
        return lidar