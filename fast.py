frame = {}

frame['hello'] = ['world']
try:
    frame['golf'].append('gross')
except KeyError:
    frame['golf'] = ['gross']
frame['hello'].append('!')

print(frame)