import numpy as np
import requests
import json

#tasks=dict()
#for i in range(1):
	#tasks[i]=int(np.random.uniform(100,1000))
	#tasks[i]=750
#print(tasks)
#while 1:
load=dict()
load['round']=int(np.random.randint(1000,2000)/100)
#r=requests.post('http://35.236.175.215:80', data = json.dumps(load))
r=requests.post('http://127.0.0.1:4000', data = json.dumps(load))
print(json.loads(r.text)['t'])