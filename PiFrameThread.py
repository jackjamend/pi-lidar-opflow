import threading
import queue
import time
from picamera.array import PiRGBArray
from picamera import PiCamera


class PiFrameThread(threading.Thread):
    def __init__(self, frame_q: queue.Queue,
                 resolution=(640, 480), framerate=32):
        super(PiFrameThread, self).__init__()
        self.stop_request = threading.Event()
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.frame_q = frame_q

    def run(self):
        while not self.stop_request.isSet():
            for image in self.camera.capture_continuous(self.rawCapture,
                                                       format="bgr",
                                                   use_video_port=True):
                frame = image.array
                self.frame_q.put(frame)
                self.rawCapture.truncate(0)
                time.sleep(.1)

    def join(self, timeout=None):
        self.stop_request.set()
        super(PiFrameThread, self).join(timeout)
