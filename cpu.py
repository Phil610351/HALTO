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
		print(command)
		os.system(command)
	Thread(target=computing).start()
	i=0
	while i<5:
		os.system("sar 1 1 >output.txt")
		with open("output.txt") as f:
			cpu_data={'data':f.read()[-56:-51]}
			print(cpu_data)
			print(1)
			r=requests.request('POST','http://127.0.0.1:5000', headers=headers, data=json.dumps(cpu_data),timeout=None)
			time.sleep(1)
			print(2)
		i+=1
		print(3)
if __name__ == '__main__':
	app.debug = True
	app.run(port=12345)
