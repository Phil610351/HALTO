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
	value[req['instance']]=req['data']
	global route
	global a
	global b
	global c
	if req['instance']==0:
		route.delete(a)
		a=route.create_text(100,100,text=req['data'],font=('Arial', 16))
	elif req['instance']==1:
		route.delete(b)
		b=route.create_text(600,100,text=req['data'],font=('Arial', 16))
	elif req['instance']==2:
		route.delete(c)
		c=route.create_text(350,500,text=req['data'],font=('Arial', 16))
	return '200 OK'

def draw():
	global route
	root = Tk()
	route = Canvas(root,width=1000, height=600)
	route.pack()
	route.bind( "<Button-1>", gen_task)
	global a
	global b
	global c
	a=route.create_text(100,100,text='0',font=('Arial', 16))
	route.create_oval( 50, 50, 150, 150, width = 3 )
	b=route.create_text(600,100,text='0',font=('Arial', 16))
	route.create_oval( 550, 50, 650, 150, width = 3 )
	c=route.create_text(350,500,text='0',font=('Arial', 16))
	route.create_oval( 300, 450, 400, 550, width = 3 )
	root.mainloop()

def gen_task(event):
	def gen():
		load=[0]*3
		task=list()
		for i in range(np.random.randint(2,6)):	task.append(np.random.poisson(20))
		text=''
		route.create_text( 850,50,text='Task:',font=('Arial', 16))
		for i in range(len(task)):
			route.create_text( 850,75+20*i,text='Subtask'+str(i+1)+' : '+str(task[i])+'%CPU',font=('Arial', 12))
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
				else:	index+=1
		r=requests.request('POST','http://192.168.43.170:11111', headers=headers, data=json.dumps({'data':task[0]}))
		r=requests.request('POST','http://192.168.43.170:22222', headers=headers, data=json.dumps({'data':task[1]}))
		#r=requests.request('POST','http://127.0.0.1:12345', headers=headers, data=json.dumps({'data':task[2]}))
	Thread(target=gen).start()

value=['0']*3
if __name__ == '__main__':
	Thread(target=draw).start()
	app.debug = True
	app.run(host='0.0.0.0')