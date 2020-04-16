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
			data=f.read()[-58:54]
			print(data)
			cpu_data={'data':data}
			print(cpu_data)
			r=requests.request('POST','http://127.0.0.1:5000', headers=headers, data=json.dumps(cpu_data))
		i+=1

if __name__ == '__main__':
	app.debug = True
	app.run(port=12345)