from rplidar import RPLidar
import time
import math
import numpy as np


class RPLiDAR:
    def __init__(self):
        self.lidar = RPLidar("\\\\.\\com4") #Check to see if this runs on mac
        #  laptop. If not make change. May be the /dev/ thing
        time.sleep(1)
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        print(info, health, sep='\n')

    def scan_area(self, limit=100):
        for i, scan in enumerate(self.lidar.iter_scans()):
            print('%d: Got %d measurements' % (i, len(scan)))
            ar = [0]*6
            warning_flag = False
            for j in scan:
                k = math.floor(j[1]/60)
                if j[2]<1000:
                    # print("Warning: object at %f degrees is too close"
                    # % (j[1]))
                    ar[k] += -math.inf
                    warning_flag = True
                else:
                    ar[k] += j[2]
                if math.floor(j[1])%60 == 0:
                    k += 1

            if warning_flag:
                print(ar)
                print("Object(s) are too close...")
                fre = max(ar)
                if fre<1000:
                    print("There is nowhere safe to venture, immediate landing"
                          " to avoid damage...")
                    break
                evac = (ar.index(fre)+1)*60 - 30
                print("Evacuate in the direction of %d degrees" % evac)

            if i > limit:
                break

    def stop(self):
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()


