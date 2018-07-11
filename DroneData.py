import queue
import time
import cv2

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

        self.lidar = LidarThread()
        self.pi_frame = PiFrameThread(self.frame_q)
        self.analyze = AnalyzeThread(self.frame_q, self.analyze_q)
        self.overlay = OverlayThread(self.analyze_q, self.overlay_q,
                                     resolution, reduction)
        self.threads = [self.pi_frame, self.analyze, self.overlay]

    def run(self):
        self.pi_frame.start()
        time.sleep(.1)
        self.analyze.start()
        time.sleep(.1)
        self.overlay.start()
        while True:
            if not self.overlay_q.empty():
                frame = self.overay_q.get()
                try:
                    cv2.imshow("Camera Feed", frame)
                except cv2.error:
                    print("Whoops, cv2 error!")
                    pass

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    def close(self):
        for thread in self.threads:
            thread.join()
            time.sleep(.5)