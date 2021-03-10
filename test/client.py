import numpy as np
import requests
import json

tasks=dict()
#for i in range(1):
	#tasks[i]=int(np.random.uniform(100,1000)*1.5)
	#tasks[i]=750
print(tasks)
#while 1:
r=requests.post('http://35.221.185.18:80', data = json.dumps(tasks).encode('utf-8'))
#r=requests.post('http://127.0.0.1:80', data = json.dumps(tasks))
print(r.text)