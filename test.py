import cv2
video_src = 0

cam = cv2.VideoCapture(video_src)

fgbg = cv2.createBackgroundSubtractorMOG2()

while True:
    ret, frame = cam.read()
    height, width, channels = frame.shape
    center_width = int(width/2)
    frame = cv2.line(frame, (center_width, 0), (center_width, height), (255, 0, 0), 1)
    frame = cv2.rectangle(frame, (int(center_width*.95), 0), (int(center_width*1.05),height), (0, 255, 0), 1)
    frame = cv2.rectangle(frame, (int(center_width * .65), 0), (int(center_width * 1.35), height), (0, 255, 0), 1)
    crop_frame = frame[int(height*.10):int(height*.90), int(center_width * .65):int(center_width * 1.35)]
    fgmask =  fgbg.apply(frame)
    cv2.imshow('Drone', frame)
    cv2.imshow('Crop', crop_frame)
    cv2.imshow('Mask', fgmask)
    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:
        break
    elif ch == 32:
        for var in fgmask:
            print(var)

cam.release()
cv2.destroyAllWindows()