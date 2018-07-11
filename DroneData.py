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

        self.lidar = LidarThread(self.lidar_q)
        self.pi_frame = PiFrameThread(self.frame_q)
        self.analyze = AnalyzeThread(self.frame_q, self.analyze_q)
        self.overlay = OverlayThread(self.analyze_q, self.overlay_q,
                                     resolution, reduction)
        self.threads = [self.lidar_q, self.pi_frame, self.analyze,
                        self.overlay]

    def run(self):
        self.pi_frame.start()
        time.sleep(.1)
        self.analyze.start()
        time.sleep(.1)
        self.overlay.start()
        self.lidar.start()
        while True:
            if not self.overlay_q.empty():
                frame = self.overay_q.get()
                cv2.putText(frame,
                            'Total frames in frame_q: %d' %
                            self.frame_q.qsize(),(20, 20),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255,255,255),
                            lineType=cv2.LINE_AA)
                cv2.putText(frame,
                            'Total frames in analyze_q: %d' %
                            self.analyze_q.qsize(),(20, 40),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255,255),
                            lineType=cv2.LINE_AA)
                cv2.putText(frame,
                            'Total frames in overlay_q: %d' %
                            self.overlay_q.qsize(), (20, 60),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255),
                            lineType=cv2.LINE_AA)
                try:
                    cv2.imshow("Camera Feed", frame)
                except cv2.error:
                    print("Whoops, cv2 error!")
                    pass
            if not self.lidar_q.empty():
                print("Object within lidar threshold")
                with self.lidar_q.mutex:
                    self.lidar_q.clear()

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    def close(self):
        for thread in self.threads:
            thread.join()
            time.sleep(.5)
        for thread in self.threads:
            if not thread.is_alive():
                print('A thread is still alive')
