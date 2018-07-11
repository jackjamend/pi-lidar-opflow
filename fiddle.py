# import numpy as np
# import cv2 as cv
# cap = cv.VideoCapture(0)
# fgbg = cv.bgsegm.createBackgroundSubtractorMOG()
# while(1):
#     ret, frame = cap.read()
#     fgmask = fgbg.apply(frame)
#     cv.imshow('frame',fgmask)
#     k = cv.waitKey(30) & 0xff
#     if k == 27:
#         break
# cap.release()
# cv.destroyAllWindows()

from lidar_lite import Lidar_Lite

lidar = Lidar_Lite()
connected = lidar.connect(1)

if connected < -1:
  print "Not Connected"

print lidar.getDistance()
print lidar.getVelocity()
