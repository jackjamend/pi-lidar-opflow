import threading, queue
import lidar_lite as lidar
import LidarThread

threshold_q = queue.Queue()
lidar = lidar()
lidar.setThreshold(100)

lidar_thread = LidarThread(lidar, threshold_q)
lidar_thread.start()

input = ''
while not input == 'q':
    input = input('q for quit')

print(lidar_thread.is_alive())
lidar_thread.join()
print(lidar_thread.is_alive())

print('donet')

