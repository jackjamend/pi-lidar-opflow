import threading
import queue
import cv2
import time
import numpy as np

lk_params = dict( winSize  = (25, 25),
                  maxLevel = 1,
                  criteria = (cv2.TERM_CRITERIA_EPS |
                              cv2.TERM_CRITERIA_COUNT, 10, 0.03))
feature_params = dict( maxCorners = 50,
                       qualityLevel = 0.5,
                       minDistance = 10,
                       blockSize = 5)


class AnalyzeThread(threading.Thread):

    def __init__(self, frame_q: queue.Queue, analyze_q: queue.Queue):
        super(AnalyzeThread, self).__init__()
        self.stop_request = threading.Event()
        self.frame_q =  frame_q
        self.analyze_q = analyze_q
        self.prev_frame = None

        self.track_len = 5
        self.detect_interval = 10
        self.tracks = []
        self.frame_idx = 0
        # self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

    def run(self):
        while not self.stop_request.isSet():
            if not self.frame_q.empty():
                start = time.time()
                frame = self.frame_q.get()
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                vis = frame.copy()
                # vis = self.fgbg.apply(frame)

                if len(self.tracks) > 0:
                    img0, img1 = self.prev_gray, frame_gray
                    p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1,
                                                                            1,
                                                                            2)
                    p1, _st, _err = cv2.calcOpticalFlowPyrLK(img0, img1, p0,
                                                            None, **lk_params)
                    p0r, _st, _err = cv2.calcOpticalFlowPyrLK(img1, img0, p1,
                                                             None, **lk_params)
                    d = abs(p0 - p0r).reshape(-1, 2).max(-1)
                    good = d < 1
                    new_tracks = []
                    for tr, (x, y), good_flag in zip(self.tracks,
                                                     p1.reshape(-1, 2), good):
                        if not good_flag:
                            continue
                        tr.append((x, y))
                        if len(tr) > self.track_len:
                            del tr[0]
                        new_tracks.append(tr)
                        cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                    self.tracks = new_tracks
                    cv2.polylines(vis, [np.int32(tr) for tr in self.tracks],
                                 False, (0, 255, 0))


                if self.frame_idx % self.detect_interval == 0:
                    mask = np.zeros_like(frame_gray)
                    mask[:] = 255
                    for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                        cv2.circle(mask, (x, y), 5, 0, -1)
                    p = cv2.goodFeaturesToTrack(frame_gray, mask=mask,
                                               **feature_params)
                    if p is not None:
                        for x, y in np.float32(p).reshape(-1, 2):
                            self.tracks.append([(x, y)])

                self.frame_idx += 1
                self.prev_gray = frame_gray

                self.analyze_q.put((vis, self.tracks))
                print('Analyze thread ran for %.2f seconds' %
                      (time.time()-start))


    def join(self, timeout=None):
        self.stop_request.set()
        super(AnalyzeThread, self).join(timeout)