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
	def computing():
		command="stress-ng -c 0 -l "+str(req['data'])+' --timeout 5'
		os.system(command)
	Thread(target=computing).start()			
	i=0
	while i<5:
		with open("output.txt") as f:
			cpu_data={'instance':0,'data':f.read()[-56:-51]}
			print(cpu_data)
			r=requests.request('POST','http://127.0.0.1:5000', headers=headers, data=json.dumps(cpu_data))
			time.sleep(1)
		i+=1
		print(i)
if __name__ == '__main__':
	def writing():
		os.system("sar 1 >output.txt")
	Thread(target=writing).start()
	app.debug = True
	app.run(port=12345)
