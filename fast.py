import numpy as np
reduction = 8
width, height = (640,480).split()//reduction
arr = np.zeros((reduction,reduction))



points = [(100,40),(0,0)]

for point in points:
    x,y = point
    dx = x // width
    dy = y // height
    arr[dx][dy] = 1

print(arr)