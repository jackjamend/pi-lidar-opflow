# import cv2
import numpy as np

# cam = cv2.VideoCapture(0)
# ret, frame = cam.read()

# height, width, channel = frame.shape
# height = height // 2
# width = width // 2
# color = (0,0,0)
lookup = np.zeros((8,8))
lookup[0][1] = 1
lookup[3][2] = 1
lookup[5][2] = 1
lookup[5][7] = 1
lookup[4][4] = 1
lookup[4][3] = 4
print(lookup)
lookup *= .95
print('r', np.unravel_index(np.argmax(lookup), lookup.shape))

# zone1, zone2, zone3, = np.split(tran, [3, 5])
tran = np.transpose(lookup)
zones = np.split(tran, [3, 5])
score = []
for zone in zones:
    score.append(np.sum(zone) / np.size(zone))
print(score)
print(np.argmin(score))



# while True:
#     ret, frame = cam.read()
#     frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
#     frame = cv2.rectangle(frame,(0,0),(int(.375 * width), height), color, 1)
#     frame = cv2.rectangle(frame, (int(.375 * width), 0),
#                           (int(.625*width), height), color, 1)
#     frame = cv2.rectangle(frame, (int(.625*width), 0), (width, height),
#                           color, 1)
#
#     cv2.imshow('Cam Feed', frame)
#
#     ch = 0xFF & cv2.waitKey(1)
#     if ch == 27:
#         break
#
# cv2.destroyAllWindows()