from flask import Flask, request
from flask_cors import CORS
from threading import Thread
from tkinter import *
import json
import requests
import numpy as np
import time
headers = {'Content-Type': 'application/json'}
app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "*"}})

@app.route('/',methods=['POST'])
def sockeeet():
	req = request.get_json()
	print(req)
	#value[req['instance']]=req['data']
	global route
	print(1)
	route.delete("all")
	print(2)
	route.create_text(200,100,text=req['data'],font=('Arial', 16))
	route.create_oval( 150, 50, 250, 150, width = 3 )
	route.create_text(700,100,text=req['data'],font=('Arial', 16))
	route.create_oval( 650, 50, 750, 150, width = 3 )
	route.create_text(450,500,text=req['data'],font=('Arial', 16))
	route.create_oval( 400, 450, 500, 550, width = 3 )
	print('done')
	return '200 OK'

def draw():
	global route
	root = Tk()
	route = Canvas(root,width=900, height=600)
	route.pack()
	Thread(target=gen_task).start()
	root.mainloop()

	def gen_task():
		while 1:
			time.sleep(5)
			load=[0]*3
			task=list()
			for i in range(np.random.randint(2,6)):
				task.append(np.random.poisson(20))
			#first fit
			task.sort()
			index=0
			for e in task:
				while 1:
					if index>2:
						index=0
					if load[index]<100:
						load[index]+=e
						index+=1
						break
					else:
						index+=1
			r=requests.request('POST','http://127.0.0.1:12345', headers=headers, data=json.dumps({'data':task[0]}))
			#r=requests.request('POST','http://127.0.0.1:12345', headers=headers, data=json.dumps({'data':task[1]}))
			#r=requests.request('POST','http://127.0.0.1:12345', headers=headers, data=json.dumps({'data':task[2]}))

value=['0']*3
if __name__ == '__main__':
	Thread(target=draw).start()
	app.debug = True
	app.run()
