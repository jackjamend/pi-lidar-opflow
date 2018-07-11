import threading, queue
import cv2

class FrameThread(threading.Thread):

    def __init__(self, cam: cv2.VideoCapture, frame_q: queue.Queue):
        super(FrameThread, self).__init__()
        self.stop_request = threading.Event()
        self.cam = cam
        self.frame_q = frame_q

    def run(self):
        while not self.stop_request.isSet():
            ret, frame = self.cam.read()
            self.frame_q.put((ret, frame))

    def join(self, timeout=None):
        self.stop_request.set()
        super(FrameThread, self).join(timeout)