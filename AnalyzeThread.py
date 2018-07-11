import threading, queue
import cv2
import numpy as np

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS |
                              cv2.TERM_CRITERIA_COUNT, 10, 0.03))
feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )


class AnalyzeThread(threading.Thread):

    def __init__(self, frame_q: queue.Queue, analyze_q: queue.Queue):
        super(AnalyzeThread, self).__init__()
        self.stop_request = threading.Event()
        self.frame_q =  frame_q
        self.analyze_q = analyze_q
        self.prev_frame = None

        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.frame_idx = 0

    def run(self):
        while not self.stop_request.isSet():
            if not self.frame_q.empty():
                frame = self.frame_q.get()
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                vis = frame.copy()

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
                    cv2.putText(vis, 'track count: %d' % len(self.tracks),
                                (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.0,
                                (255, 255, 255), lineType=cv2.LINE_AA)

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


    def join(self, timeout=None):
        self.stop_request.set()
        super(AnalyzeThread, self).join(timeout)