import threading, queue
import cv2

class AnalyzeThread(threading.Thread):

    def __init__(self, frame_q: queue.Queue, analyze_q: queue.Queue):
        super(AnalyzeThread, self).__init__()
        self.frame_q =  frame_q
        self.analyze_q = analyze_q