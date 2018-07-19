# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15, 2018

@author: Jack J Amend

Inherits from the Thread class. Takes the current sensor information and 
places it into a given queue that is provided during initialization. This 
thread class assumes that the camera being used is a PiCamera. 
"""
import queue
import threading

from picamera import PiCamera
from picamera.array import PiRGBArray


class SensorThread(threading.Thread):
    def __init__(self, sensor_q: queue.Queue, threshold, resolution=(640, 480),
                 framerate=32, name=None):
        """
        Initializes an instance of a sensor thread. Thread records sensor 
        information.
        
        :param sensor_q: 
            queue that saves the sensor data.
        :param threshold: 
            minimum distance required for drone to be in the danger zone. 
        :param resolution: 
            a tuple of the number of pixels as height by width.
        :param framerate: 
            frame rate required parameter for the PiCamera.
        :param name: 
            name of the thread.
        """
        super(SensorThread, self).__init__(name=name)
        self.stop_request = threading.Event()

        # Camera
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.sensor_q = sensor_q

        # LiDAR
        self.lidar = self._setup_lidar()
        self.lidar_threshold = threshold
        self.current_value = None
        self.in_danger_zone = False

    def run(self):
        """
        Runs thread while stop request is not set. Reads in images from the 
        PiCamera and the LiDAR at the current time and puts it into the 
        sensor queue to be processed by the analyze thread.
        """
        while not self.stop_request.isSet():
            for image in self.camera.capture_continuous(self.rawCapture,
                                                        format="bgr",
                                                        use_video_port=True):
                frame = image.array
                self.current_value = self.lidar.getDistance()

                if self.current_value < self.lidar_threshold:
                    self.in_danger_zone = True
                else:
                    self.in_danger_zone = False
                self.sensor_q.put((frame, (self.current_value,
                                           self.in_danger_zone)))
                self.rawCapture.truncate(0)

    def join(self, timeout=None):
        """
       Joins the thread.
       :param timeout: 
           time until timeout of attempting to join thread 
       """
        self.stop_request.set()
        super(SensorThread, self).join(timeout)

    def _setup_lidar(self):
        """
        Creates a LiDAR object from the file and checks to see if it is 
        connected.
        
        :raise Exception: 
            raises an exception if LiDAR is not connected
        :return: 
            LiDAR object
        """
        from lidar_lite import Lidar_Lite as lidar
        lidar = lidar()
        connect = lidar.connect(1)
        if connect < -1:
            raise Exception("No LiDAR found")
        return lidar
