from flask import Flask, request
from threading import Thread
import requests
import json
import os
import time
headers = {'Content-Type': 'application/json'}
app = Flask(__name__)

@app.route('/',methods=['POST'])
def sockeeet():
	req=request.get_json()
	print(req)
	def writing():	os.system("sar 1 >output.txt")
	Thread(target=writing).start()	
	def computing():	os.system("stress-ng -c 2 -l "+str(req['data'])+' --timeout 15')
	Thread(target=computing).start()
	i=0
	MA=list()
	while i<15:
		with open("output.txt") as f:
			try:		
				read=f.read()[-56:-51]
				count.append(float(read))
				cpu_data={'instance':0,'data':round(sum(MA)/1.25/len(MA),2)}
				print(cpu_data,read)
				r=requests.request('POST','http://192.168.8.155:5000', headers=headers, data=json.dumps(cpu_data))
				MA.pop(0)
			except:	pass
			time.sleep(1)
		i+=1
	#r=requests.request('POST','http://192.168.8.139:5000', headers=headers, data=json.dumps({'instance':0,'data':round(count/15,2)}))
	r=requests.request('POST','http://192.168.8.155:5000', headers=headers, data=json.dumps({'instance':7,'data':0}))
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=11111)