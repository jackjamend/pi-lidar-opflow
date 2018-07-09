# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 12:08:30 2018

@author: jza0069
"""
import cv2
from adv_opt_flow import App


def main():
    # video_src = "car.mp4"
    video_src = "tcp://192.168.1.1:5555"
    # video_src = 0
    try:
        app = App(video_src, plot_graphs=False, full_track=True, reduction=10)
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
