import cv2
video_src = "tcp://192.168.1.1:5555"

cam = cv2.VideoCapture(video_src)

while True:
    ret, frame = cam.read()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Drone', frame_gray)
    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:
        break

cam.release()
cv2.destroyAllWindows()