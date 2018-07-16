import numpy as np

arr = np.zeros((8,8))
count = 0
for i in range(len(arr)):
    for j in range(len(arr[i])):
        arr[i][j] = count
        count +=1


print(arr)
print(arr.flatten())