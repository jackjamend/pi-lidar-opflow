# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15, 2018

@author: Jack J Amend

Creates an instance of a DroneData object based on the parameters of the 
dimensions of pixels of the camera and the reduction factor. The reduction 
factor creates smaller frames by squaring the value. This program is 
designed to run on a Raspberry Pi. The program utilizes multi-threading by 
creating three additional threads in order to speed up the computation time. 
"""
from DroneData import DroneData


def main():
    """
    Driver of the program. Starts the DroneData object for object detection 
    for a UAV.
    """
    drone_data = None
    try:
        picamera_frame_size = (640, 480)
        frame_reduction_factor = 8
        drone_data = DroneData(picamera_frame_size, frame_reduction_factor)
        drone_data.run()
        print('Program ending...')
        drone_data.close()
    # Except statement in order to exit out of the program gracefully
    except KeyboardInterrupt:
        print("Keyboard Interruption. Closing app")
        if drone_data is not None:
            drone_data.close()


if __name__ == '__main__':
    main()
