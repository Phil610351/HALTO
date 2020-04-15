import requests
import json
import os
import numpy as np
import time
headers = {'Content-Type': 'application/json'}
while 1:
	#os.system("sar 1 1 >output.txt")
	#with open("output.txt") as f:
	time.sleep(1)
	cpu_data={'data':str(np.random.randint(1,10))}
	print(cpu_data)
	r=requests.request('POST','http://127.0.0.1:5000', headers=headers, data=json.dumps(cpu_data))