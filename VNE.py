from flask import Flask, request
from threading import Thread
from tkinter import *
import json
import requests
import numpy as np
import time
headers = {'Content-Type': 'application/json'}
app = Flask(__name__)
app.debug = True
@app.route('/',methods=['POST'])
def sockeeet():
	req = request.get_json()
	print(req)
	value[req['instance']]=req['data']
	global route
	global c1
	global c2
	global c3
	global c4
	global c5
	global c6
	if req['instance']==0:
		route.delete(c1)
		c1=route.create_text(100,300,text=req['data'],font=('Arial', 16))
	elif req['instance']==1:
		route.delete(c2)
		c2=route.create_text(250,300,text=req['data'],font=('Arial', 16))
	elif req['instance']==2:
		route.delete(c3)
		c3=route.create_text(400,300,text=req['data'],font=('Arial', 16))
	elif req['instance']==3:
		route.delete(c4)
		c4=route.create_text(550,300,text=req['data'],font=('Arial', 16))
	elif req['instance']==4:
		route.delete(c5)
		c5=route.create_text(700,300,text=req['data'],font=('Arial', 16))
	elif req['instance']==5:
		route.delete(c6)
		c6=route.create_text(850,300,text=req['data'],font=('Arial', 16))
	else:
		route.delete(c1)
		route.delete(c2)
		route.delete(c3)
		route.delete(c4)
		route.delete(c5)
		route.delete(c6)			
		c1=route.create_text(100,300,text='0',font=('Arial', 16))
		c2=route.create_text(250,300,text='0',font=('Arial', 16))
		c3=route.create_text(400,300,text='0',font=('Arial', 16))
		c4=route.create_text(550,300,text='0',font=('Arial', 16))
		c5=route.create_text(700,300,text='0',font=('Arial', 16))
		c6=route.create_text(850,300,text='0',font=('Arial', 16))
		global d
		for e in d:
			route.delete(e)
		d=list()		
	return '200 OK'

def draw():
	global route
	global c1
	global c2
	global c3
	global c4
	global c5
	global c6	
	root = Tk()
	route = Canvas(root,width=950, height=700)
	route.pack()
	route.bind( "<Button-1>", gen_task)	

	route.create_oval( 425, 50, 525, 150, width = 3 )
	route.create_text(475,100,text='Control',font=('Arial', 16))
	route.create_line(475, 150, 100, 250, fill='green', width= 3 )
	route.create_line(475, 150, 250, 250, fill='green', width= 3 )
	route.create_line(475, 150, 400, 250, fill='green', width= 3 )
	route.create_line(475, 150, 550, 250, fill='green', width= 3 )
	route.create_line(475, 150, 700, 250, fill='green', width= 3 )
	route.create_line(475, 150, 850, 250, fill='green', width= 3 )

	route.create_line(150, 300, 200, 300, fill='purple', width= 3 )
	route.create_line(300, 300, 350, 300, fill='purple', width= 3 )
	route.create_line(450, 300, 500, 300, fill='purple', width= 3 )
	route.create_line(600, 300, 650, 300, fill='purple', width= 3 )
	route.create_line(750, 300, 800, 300, fill='purple', width= 3 )

	c1=route.create_text(100,300,text='0',font=('Arial', 16))
	route.create_oval( 50, 250, 150, 350, width = 3 )
	route.create_text(100,370,text='Node1',font=('Arial', 16))
	c2=route.create_text(250,300,text='0',font=('Arial', 16))
	route.create_oval( 200, 250, 300, 350, width = 3 )
	route.create_text(250,370,text='Node2',font=('Arial', 16))
	c3=route.create_text(400,300,text='0',font=('Arial', 16))
	route.create_oval( 350, 250, 450, 350, width = 3 )
	route.create_text(400,370,text='Node3',font=('Arial', 16))
	c4=route.create_text(550,300,text='0',font=('Arial', 16))
	route.create_oval( 500, 250, 600, 350, width = 3 )
	route.create_text(550,370,text='Node4',font=('Arial', 16))
	c5=route.create_text(700,300,text='0',font=('Arial', 16))
	route.create_oval( 650, 250, 750, 350, width = 3 )
	route.create_text(700,370,text='Node5',font=('Arial', 16))
	c6=route.create_text(850,300,text='0',font=('Arial', 16))
	route.create_oval( 800, 250, 900, 350, width = 3 )
	route.create_text(850,370,text='Node6',font=('Arial', 16))
	
	route.create_line(0, 400, 950, 400, width= 5 )
	root.mainloop()

def gen_task(event):
	global d
	for e in d:
		route.delete(e)
	d=list()
	load=[0]*6
	total_task=list()
	for n_u in range(np.random.randint(2,6)):
		task=list()
		for i in range(np.random.randint(2,6)):	
			cycle=np.random.poisson(15)
			task.append(cycle)
			total_task.append(cycle)	
		d.append(route.create_text(150*(n_u+1),450,text='User'+str(n_u+1)+':',font=('Arial', 16)))
		for i in range(len(task)):
			d.append(route.create_text( 150*(n_u+1),475+20*i,text='Subtask'+str(i+1)+' : '+str(task[i])+'%CPU',font=('Arial', 12)))
		task.sort()
		index=0
	for e in total_task:
		while 1:
			if index>5:
				index=0
			if load[index]<100:
				load[index]+=e
				index+=1
				break
			else:	index+=1
	#print(load)
	#def node1():	r=requests.request('POST','http://192.168.8.126:11111', headers=headers, data=json.dumps({'data':load[0]}))
	#def node2():	r=requests.request('POST','http://192.168.8.161:11111', headers=headers, data=json.dumps({'data':load[1]}))
	#def node3():	r=requests.request('POST','http://192.168.8.177:11111', headers=headers, data=json.dumps({'data':load[2]}))
	#def node4():	r=requests.request('POST','http://192.168.8.134:11111', headers=headers, data=json.dumps({'data':load[3]}))
	def node5():	r=requests.request('POST','http://192.168.8.165:11111', headers=headers, data=json.dumps({'data':load[4]}))
	#def node6():	r=requests.request('POST','http://192.168.8.110:11111', headers=headers, data=json.dumps({'data':load[5]}))
	#Thread(target=node1).start()
	#Thread(target=node2).start()
	#Thread(target=node3).start()
	#Thread(target=node4).start()
	Thread(target=node5).start()
	#Thread(target=node6).start()
d=list()
value=[0]*10
if __name__ == '__main__':
	Thread(target=draw).start()
	app.run(host='0.0.0.0')