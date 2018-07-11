# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 12:08:30 2018

@author: Jack J Amend
"""

'''
Calls the adv_opt_flow file to run optical flow on give input. Adjust this file for desired
camera input. The tcp://192.168.1.1:5555 accesses the Parrot ARDrone 2.0 camera when connected
to it via wifi.
'''
import cv2
from adv_opt_flow import App


def main():
<<<<<<< HEAD
    # video_src = "car.mp4"
    # video_src = "tcp://192.168.1.1:5555"
    video_src = 0
=======
    video_src = "car.mp4"
    # video_src = "tcp://192.168.1.1:5555"
    # video_src = 0
>>>>>>> c1201e31185cc1ebbd9d2e974f87a7fca5dd0610
    try:
        app = App(video_src, plot_graphs=False, full_track=True, reduction=8)
        app.run()
        cv2.waitKey(0)
        app.close()
    except AttributeError:
        print("Whoops! You forgot to switch the WiFi again :/")
    except KeyboardInterrupt:
        print("Keyboard Interruption. Closing app")
        app.close()



if __name__ == '__main__':
    main()
