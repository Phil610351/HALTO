from flask import Flask, request
from flask_cors import CORS
from threading import Thread
import requests
import json
import os
import numpy as np
import time
headers = {'Content-Type': 'application/json'}
app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "*"}})

@app.route('/',methods=['POST'])
def sockeeet():
	req=request.get_json()
	print(req)
	def computing():	os.system("stress-ng -c 0 -l "+str(req['data'])+' --timeout 5')
	Thread(target=computing).start()			
	i=0
	while i<5:
		with open("output.txt") as f:
			cpu_data={'instance':0,'data':f.read()[-56:-51]}
			print(cpu_data)
			if cpu_data['data'][0] in {'1','2','3','4','5','6','7','8','9','0'}:
				r=requests.request('POST','http://192.168.43.101:5000', headers=headers, data=json.dumps(cpu_data))
			time.sleep(1)
		i+=1
if __name__ == '__main__':
	def writing():	os.system("sar 1 >output.txt")
	Thread(target=writing).start()
	app.debug = True
	app.run(host='0,0,0,0',port=11111)
