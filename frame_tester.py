from FrameThread import FrameThread
import queue
import cv2
import time

frame_q = queue.Queue()
cam = cv2.VideoCapture(0)

frame_thread = FrameThread(cam, frame_q)
frame_thread.start()
ready = False
lagging_threshold = 8
time.sleep(1)
color = (0,0,255)

while True:
    if not frame_q.empty():
        _, frame = frame_q.get()


    if frame_q.qsize() < lagging_threshold and not ready:
        print("Camera is ready")
        color = (255,255,255)
        ready = not ready
    elif frame_q.qsize() >= lagging_threshold and ready:
        print("Uh-oh! We laggin'!")
        color = (0, 0, 255)
        ready = not ready

    cv2.putText(frame, 'Total frames in queue: %d' % frame_q.qsize(),
                (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.0, color,
                lineType=cv2.LINE_AA)
    cv2.imshow("Thread Frame", frame)

    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:  # ESC key to exit
        break

frame_thread.join()