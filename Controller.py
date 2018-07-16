# -*- coding: utf-8 -*-
from DroneData import DroneData
import time
"""
Created on Fri Jun 15 12:08:30 2018

@author: Jack J Amend
"""

'''
Calls the adv_opt_flow file to run optical flow on give input. Adjust this file 
for desired camera input. The tcp://192.168.1.1:5555 accesses the Parrot 
ARDrone 2.0 camera when connected
to it via wifi.
'''


def main():

    try:
        drone_data = DroneData((640, 480), 8)
        drone_data.verbose = True
        drone_data.run()
        print('Program ending')
        drone_data.close()
    except KeyboardInterrupt:
        print("Keyboard Interruption. Closing app")
        drone_data.close()


if __name__ == '__main__':
    main()
