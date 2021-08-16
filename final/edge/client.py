import numpy as np
import requests
import json

#隨機產生load
load=dict()
load['round']=int(np.random.randint(1000,2000)/100)
#r=requests.post('http://35.236.175.215:80', data = json.dumps(load))
#發request並等待response
r=requests.post('http://127.0.0.1:4000', data = json.dumps(load))
print(json.loads(r.text)['t'])