from flask import Flask, request
from threading import Thread
from tkinter import *
from math import log
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
	route = Canvas(root,width=1200, height=1000)
	route.pack()
	route.bind( "<Button-1>", gen_traffic)	

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
	c.append(route.create_text(250,300,text='0',font=('Arial', 16)))
	route.create_oval( 200, 250, 300, 350, width = 3 )
	c.append(route.create_text(400,300,text='0',font=('Arial', 16)))
	route.create_oval( 350, 250, 450, 350, width = 3 )
	c.append(route.create_text(550,300,text='0',font=('Arial', 16)))
	route.create_oval( 500, 250, 600, 350, width = 3 )
	c.append(route.create_text(700,300,text='0',font=('Arial', 16)))
	route.create_oval( 650, 250, 750, 350, width = 3 )
	c.append(route.create_text(850,300,text='0',font=('Arial', 16)))
	route.create_oval( 800, 250, 900, 350, width = 3 )
	
	route.create_line(950, 0, 950, 1000, width= 5 )
	root.mainloop()

def gen_traffic(event):
	def sine():
		traffic=2
		incre=1	
		while 1:
			start=time.time()
			global d
			for e in d:	route.delete(e)
			d=list()

			total_task=list()
			if traffic>3 and traffic<7:	d.append(route.create_text(150,50,text='Hybrid',fill='green',font=('Arial', 24)))
			elif traffic>=7:	d.append(route.create_text(150,50,text='Online',fill='red',font=('Arial', 24)))
			else:	d.append(route.create_text(150,50,text='Offline',fill='blue',font=('Arial', 24)))
			anchor=0
			for n_u in range(traffic):
				task=list()
				for i in range(np.random.randint(2,6)):	task.append(np.random.poisson(20))
				total_task.append(task)
				d.append(route.create_text(1000,25+anchor,text='User'+str(n_u+1)+':',font=('Arial', 16)))
				anchor+=20
				for i in range(len(task)):
					d.append(route.create_text(1050,25+anchor,text='Subtask'+str(i+1)+' : '+str(task[i])+'%CPU',font=('Arial', 12)))
					anchor+=20
				anchor+=10
			index=0
			bias=[0]*6
			load=[0]*6
			decision=genetic(total_task)
			for i in range(len(total_task)):
				for j in range(len(total_task[i])):
						load[int(decision[index])]+=total_task[i][j]
						d.append(route.create_text(position[int(decision[index])][0],370+bias[int(decision[index])],text='('+str(i)+','+str(j)+')',font=('Arial', 16)))
						bias[int(decision[index])]+=20
						index+=1
			print(decision)
			print(load)
			def node1():	r=requests.request('POST','http://192.168.8.126:11111', headers=headers, data=json.dumps({'data':load[0]}))
			def node2():	r=requests.request('POST','http://192.168.8.161:11111', headers=headers, data=json.dumps({'data':load[1]}))
			def node3():	r=requests.request('POST','http://192.168.8.177:11111', headers=headers, data=json.dumps({'data':load[2]}))
			def node4():	r=requests.request('POST','http://192.168.8.134:11111', headers=headers, data=json.dumps({'data':load[3]}))
			def node5():	r=requests.request('POST','http://192.168.8.165:11111', headers=headers, data=json.dumps({'data':load[4]}))
			def node6():	r=requests.request('POST','http://192.168.8.110:11111', headers=headers, data=json.dumps({'data':load[5]}))
			Thread(target=node1).start()
			Thread(target=node2).start()
			Thread(target=node3).start()
			Thread(target=node4).start()
			Thread(target=node5).start()
			Thread(target=node6).start()
			while time.time()-start<3:	pass
			traffic+=incre
			if traffic>7:
				incre=-1
			if traffic<3:
				incre=1
	Thread(target=sine).start()

def cal_reward(state, decision):
	load=[0]*6
	index=0
	for i in range(len(state)):
		for j in range(len(state[i])):
			load[int(decision[index])]+=state[i][j]
			index+=1
	entropy=0
	for e in load:
		entropy-=e/1000*log(e/1000+0.1)
	return entropy

def genetic(state):
	Maternal=dict()
	def generate(size):
		for a in range(size):
			decision=''
			for i in range(len(state)):	
				for j in range(len(state[i])):
					decision+=str(np.random.randint(6))
			Maternal[decision]=cal_reward(state, decision)

	def crossover(pairs, rank):
		parent=set()
		for e in range(2*pairs):
			a=np.random.rand()
			if a<rank[0][1]:	parent.add(rank[0][0])
			else:
				accu=rank[0][1]
				for i in range(1, len(rank)):
					if a>accu and a<accu+rank[i][1]:
						parent.add(rank[i][0])
						break
					else:	accu+=rank[i][1]
		while len(parent)>2:
			a=parent.pop()
			b=parent.pop()
			start, end=np.random.randint(len(a)), np.random.randint(len(a))
			if start>end:   start,end=end,start
			aa,bb='',''
			for j in range(start):
				aa+=a[j]
				bb+=b[j]
			for j in range(start, end):
				aa+=b[j]
				bb+=a[j]
			for j in range(end, len(a)):
				aa+=a[j]
				bb+=b[j]
			if aa not in Maternal:  Maternal[aa]=cal_reward(state, aa)
			if bb not in Maternal:  Maternal[bb]=cal_reward(state, bb)
			
			if np.random.rand()<0.06:
				muta1, muta2='', ''
				tar=np.random.randint(len(aa))
				for i in range(len(aa)):
					if i!=tar:
						muta1+=aa[i]
						muta2+=bb[i]
					else:
						muta1+=str(np.random.randint(6))
						muta2+=str(np.random.randint(6))
				if muta1 not in Maternal:  Maternal[muta1]=cal_reward(state, muta1)
				if muta2 not in Maternal:  Maternal[muta2]=cal_reward(state, muta2)

		if len(Maternal)>len(rank):
			for i in range(1, len(Maternal)-len(rank)+1):
				Maternal.pop(rank[-i][0])

	generate(1000)
	cou=0
	st1=0
	while 1:
		total=0
		Roulette=Maternal.copy()
		for e in Roulette.values(): total+=e
		for e in Roulette.keys():   Roulette[e]/=total
		crossover(25, sorted(Roulette.items(), key=lambda kv: -kv[1]))
		if st1==sorted(Maternal.items(), key=lambda kv: -kv[1])[0][1]:  cou+=1
		else:
			st1=sorted(Maternal.items(), key=lambda kv: -kv[1])[0][1]
			cou=0
		if cou>10:   break
	decision=sorted(Maternal.items(), key=lambda kv: -kv[1])[0][0]
	return decision

if __name__ == '__main__':
	Thread(target=draw).start()
	app.run(host='0.0.0.0')