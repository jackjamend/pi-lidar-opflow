from rplidar import RPLidar
import time
import math
import numpy as np


class RPLiDAR:
    def __init__(self, sectors):
        self.lidar = RPLidar("\\\\.\\com4") # Check to see if this runs on mac
        #  laptop. If not make change. May be the /dev/ thing
        self.sectors = sectors
        self.sector_space = {}
        self.prev_sector_space = {}
        time.sleep(1)
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        print(info, health, sep='\n')
        self.file = open('lidar-data.txt', 'r')

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
                      % evacuation_direction)  # This is the safest spot

    def area_report(self, limit=100):
        for i, scans in enumerate(self.lidar.iter_scans()):
            if i > limit:
                # self.stop()
                break
            self.sector_space = {}
            divisor = 360 // self.sectors

            for scan in scans:
                section = math.floor(scan[1] / divisor)
                try:
                    self.sector_space[section] = np.append(self.sector_space[
                                                           section], scan[2])
                except KeyError:
                    self.sector_space[section] = np.array(scan[2])
            evaluation_space = self._evaluate_spcae()
            print('evaluate space', evaluation_space, file=self.file)
            direction = self._get_direction(evaluation_space)
            if direction == -1:
                print('There are no safe regions!')
            print('Go to region %d' % direction)

    def _evaluate_spcae(self):
        evaluation = []
        for i in range(self.sectors):
            try:
                section = self.sector_space[i]
                evaluation.append((section, np.min(section), np.max(section),
                                   np.average(section)))
            except KeyError:
                evaluation.append((i, None, None, None))
        return evaluation

    def _get_direction(self, evaluation_space):
        current_section = -1
        previous_min = 1
        for section, min, max, average in evaluation_space:
            if min > previous_min:
                current_section = section
                previous_min = min
        return current_section

    def stop(self):
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()


if __name__ == '__main__':
    lidar = RPLiDAR(6)
    lidar.area_report(50)
    lidar.stop()
