from rplidar import RPLidar
import time
import math
import numpy as np


class RPLiDAR:
    def __init__(self):
        self.lidar = RPLidar("\\\\.\\com4") # Check to see if this runs on mac
        #  laptop. If not make change. May be the /dev/ thing
        time.sleep(1)
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        print(info, health, sep='\n')

    def scan_area(self, limit=100):
        for i, scan in enumerate(self.lidar.iter_scans()):
            if i > limit:
                break

            print('%d: Got %d measurements' % (i, len(scan)))
            sector_space = np.zeros(6)
            warning_flag = False
            for j in scan:
                k = math.floor(j[1]/60)
                if j[2] < 1000:
                    # print("Warning: object at %f degrees is too close"
                    # % (j[1]))
                    sector_space[k] += -math.inf # Set to say space is unsafe
                    warning_flag = True
                else:
                    sector_space[k] += j[2] # adding distance to sector array

            if warning_flag:
                print(sector_space) # outputs six values
                print("Object(s) are too close...")
                free_space = max(sector_space)
                if free_space < 1000:
                    print("There is nowhere safe to venture, immediate landing"
                          " to avoid damage...")
                    break
                evacuation_direction = \
                    (sector_space.index(free_space)+1) * 60 - 30
                print("Evacuate in the direction of %d degrees"
                      % evacuation_direction) # This is the safest spot

    def area_report(self, limit=100, sectors=6):
        for i, scans in enumerate(self.lidar.iter_scans()):
            if i > limit:
                break
            sector_space = {}
            divisor = 360 // sectors

            for scan in scans:
                section = math.floor(scan[1] / divisor)
                try:
                    sector_space[section].put(scan[2])
                except KeyError:
                    sector_space[section] = np.array(scan[2])
            print('evaluate space', self._evaluate_spcae(sector_space,
                                                         sectors))

    def _evaluate_spcae(self, sector_space, sectors, min_threshold=1000):
        evaluation = []
        for i in range(sectors):
            section = sector_space[i]
            evaluation.append((section, np.min(section), np.max(section),
                               np.average(section)))
        return evaluation




    def stop(self):
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()


if __name__ == '__main__':
    lidar = RPLiDAR()
    lidar.area_report(50,6)