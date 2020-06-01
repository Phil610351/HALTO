from flask import Flask, request
from threading import Thread
from tkinter import *
import json
import requests
import numpy as np
import time

d=list()
c=list()
value=[0]*10
position=[[100,300],[250,300],[400,300],[550,300],[700,300],[850,300]]
headers = {'Content-Type': 'application/json'}
app = Flask(__name__)
app.debug = True
@app.route('/',methods=['POST'])
def sockeeet():
	req = request.get_json()
	print(req)
	value[req['instance']]=req['data']
	global route
	global c
	ident=req['instance']
	if ident!=7:
		route.delete(c[ident])
		c[ident]=route.create_text(position[ident][0],position[ident][1],text=req['data'],font=('Arial', 16))
	else:
		global d
		for e in d:
			route.delete(e)
		d=list()
	return '200 OK'

def draw():
	global route
	global c
	global d
	root = Tk()
	route = Canvas(root,width=1200, height=700)
	route.pack()
	route.bind( "<Button-1>", gen_task)	

	#route.create_text(100,50,text='State: ',font=('Arial', 20))
	d.append(route.create_text(150,50,text='Initial',fill='brown',font=('Arial', 24)))

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

	c.append(route.create_text(100,300,text='0',font=('Arial', 16)))
	route.create_oval( 50, 250, 150, 350, width = 3 )
	#route.create_text(100,370,text='Node1',font=('Arial', 16))
	c.append(route.create_text(250,300,text='0',font=('Arial', 16)))
	route.create_oval( 200, 250, 300, 350, width = 3 )
	#route.create_text(250,370,text='Node2',font=('Arial', 16))
	c.append(route.create_text(400,300,text='0',font=('Arial', 16)))
	route.create_oval( 350, 250, 450, 350, width = 3 )
	#route.create_text(400,370,text='Node3',font=('Arial', 16))
	c.append(route.create_text(550,300,text='0',font=('Arial', 16)))
	route.create_oval( 500, 250, 600, 350, width = 3 )
	#route.create_text(550,370,text='Node4',font=('Arial', 16))
	c.append(route.create_text(700,300,text='0',font=('Arial', 16)))
	route.create_oval( 650, 250, 750, 350, width = 3 )
	#route.create_text(700,370,text='Node5',font=('Arial', 16))
	c.append(route.create_text(850,300,text='0',font=('Arial', 16)))
	route.create_oval( 800, 250, 900, 350, width = 3 )
	#route.create_text(850,370,text='Node6',font=('Arial', 16))
	
	route.create_line(950, 0, 950, 700, width= 5 )
	#route.create_line(0, 400, 950, 400, width= 5 )
	root.mainloop()

def gen_task(event):
	global d
	for e in d:
		route.delete(e)
	d=list()
	load=[0]*6
	total_task=list()
	traffic=np.random.randint(2,7)
	if traffic>2 and traffic<5:	d.append(route.create_text(150,50,text='Hybrid',fill='green',font=('Arial', 24)))
	elif traffic>5:	d.append(route.create_text(150,50,text='Online',fill='red',font=('Arial', 24)))
	else:	d.append(route.create_text(150,50,text='Offline',fill='blue',font=('Arial', 24)))
	anchor=0
	for n_u in range(traffic):
		task=list()
		for i in range(np.random.randint(2,6)):	
			task.append(np.random.poisson(15))
		total_task.append(task)
		d.append(route.create_text(1000,25+anchor,text='User'+str(n_u+1)+':',font=('Arial', 16)))
		anchor+=20
		for i in range(len(task)):
			d.append(route.create_text(1050,25+anchor,text='Subtask'+str(i+1)+' : '+str(task[i])+'%CPU',font=('Arial', 12)))
			anchor+=20
		anchor+=20
		task.sort()
		index=0
	bias=[0]*6
	for i in range(len(total_task)):
		for j in range(len(total_task[i])):	
			while 1:
				if index>5:index=0
				if load[index]<100:
					load[index]+=total_task[i][j]
					d.append(route.create_text(position[index][0],370+bias[index],text='('+str(i)+','+str(j)+')',font=('Arial', 16)))
					bias[index]+=20
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

if __name__ == '__main__':
	Thread(target=draw).start()
	app.run(host='0.0.0.0')