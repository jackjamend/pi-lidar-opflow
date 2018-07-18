import time
import datetime
from termcolor import colored
import queue

print(colored("Object outside of LiDAR threshold", 'red'))
print(colored("Object outside of LiDAR threshold", 'green'))

q = queue.Queue()

q.put(('frame', (300,True)))

frame, lidar = q.get()
print(frame)
print(lidar)

def test(point, length):
    x, y = point
    total = (x + y) * length
    return total

p = (360, 480)
legg = 4

print(test(p, legg))
