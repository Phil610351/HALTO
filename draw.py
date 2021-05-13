from tkinter import *
from time import time, sleep
from threading import Thread
import numpy as np

c=list()
data1=['0.00','98.50','99.50',98.01,100.0,'99.00',98.99,100.0,'98.50','99.00', '0.00']
data2=['0.00','99.00',100.0,100.0,98.99,'99.00',98.99,98.51,98.99,'99.00', '0.00']
data3=['0.00',100.0,'99.00',100.0,98.49,'99.00',98.49,'99.00',100.0,'99.00', '0.00']
data4=['0.00',100.0,'99.00','98.50','99.00','98.50','98.50','99.00',98.99,98.51, '0.00']
#data5=['0.00','99.00',98.99,'99.00',98.99,100.0,100.0,'98.50','99.00','99.00', '0.00']
task=[692.5,211.4,991.4,390.1,241.4,364.7,258.6,601.8,616.9,186.2,810.3,302.1,701.2,229.7,305.2]
comput1=[31.2,34.7,34.0]
comput2=[17.4,51.7,4.47,22.6,9.9]
comput3=[64.3,12.2,23.4]
comput4=[5.4,53.5,13.6,27.3]

def draw():

	def update():

		route.create_text(100,260,text='task  1:  692.5M',fill='blue',font=('Arial', 12))
		route.create_text(100,280,text='task  2:  211.4M',fill='blue',font=('Arial', 12))
		route.create_text(100,300,text='task  3:  991.4M',fill='blue',font=('Arial', 12))
		route.create_text(100,320,text='task  4:  390.1M',fill='blue',font=('Arial', 12))
		route.create_text(100,340,text='task  5:  241.4M',fill='blue',font=('Arial', 12))
		route.create_text(100,360,text='task  6:  364.7M',fill='blue',font=('Arial', 12))
		route.create_text(100,380,text='task  7:  258.6M',fill='blue',font=('Arial', 12))
		route.create_text(100,400,text='task  8:  601.8M',fill='blue',font=('Arial', 12))
		route.create_text(100,420,text='task  9:  616.9M',fill='blue',font=('Arial', 12))
		route.create_text(100,440,text='task 10:  186.2M',fill='blue',font=('Arial', 12))
		route.create_text(100,460,text='task 11:  810.3M',fill='blue',font=('Arial', 12))
		route.create_text(100,480,text='task 12:  302.1M',fill='blue',font=('Arial', 12))
		route.create_text(100,500,text='task 13:  701.2M',fill='blue',font=('Arial', 12))
		route.create_text(100,520,text='task 14:  229.7M',fill='blue',font=('Arial', 12))
		route.create_text(100,540,text='task 15:  305.2M',fill='blue',font=('Arial', 12))

		route.create_text(275,625,text='task  3: 31.2%',fill='purple',font=('Arial', 12))
		route.create_text(275,645,text='task  7: 34.7%',fill='purple',font=('Arial', 12))
		route.create_text(275,665,text='task 14: 34.0%',fill='purple',font=('Arial', 12))

		route.create_text(425,625,text='task  1: 17.4%',fill='purple',font=('Arial', 12))
		route.create_text(425,645,text='task  5: 51.7%',fill='purple',font=('Arial', 12))
		route.create_text(425,665,text='task  6: 4.7%',fill='purple',font=('Arial', 12))
		route.create_text(425,685,text='task 10: 22.6%',fill='purple',font=('Arial', 12))
		route.create_text(425,705,text='task 11:  9.9%',fill='purple',font=('Arial', 12))

		route.create_text(575,625,text='task  2: 64.3%',fill='purple',font=('Arial', 12))
		route.create_text(575,645,text='task  9: 12.2%',fill='purple',font=('Arial', 12))
		route.create_text(575,665,text='task 13: 23.4%',fill='purple',font=('Arial', 12))

		route.create_text(725,625,text='task  4:  5.4%',fill='purple',font=('Arial', 12))
		route.create_text(725,645,text='task  8: 53.5%',fill='purple',font=('Arial', 12))
		route.create_text(725,665,text='task 12: 13.6%',fill='purple',font=('Arial', 12))
		route.create_text(725,685,text='task 15: 27.3%',fill='purple',font=('Arial', 12))

		'''for i in range(11):
			sleep(1)
			for e in c:
				route.delete(e)
			c.append(route.create_text(275,490,text=data1[i],font=('Arial', 16)))
			c.append(route.create_text(425,490,text=data2[i],font=('Arial', 16)))
			c.append(route.create_text(575,490,text=data3[i],font=('Arial', 16)))
			c.append(route.create_text(725,490,text=data4[i],font=('Arial', 16)))'''

	global route
	global c
	root=Tk()
	route=Canvas(root,width=1000, height=800)
	route.pack()
	
	user=PhotoImage(file = 'user.png')
	orchestrator=PhotoImage(file = 'orchestrator.png')
	RAN=PhotoImage(file = 'RAN.png')
	control=PhotoImage(file = 'control.png')
	compute=PhotoImage(file = 'compute.png')

	route.create_image(70,120, image = user)
	route.create_text(70,190,text='Users',font=('Arial', 20))
	route.create_image(300,120, image = RAN)
	route.create_text(300,190,text='RAN',font=('Arial', 20))
	route.create_image(500,110, image = orchestrator)
	route.create_text(500,190,text='Orchestrator',font=('Arial', 20))
	route.create_image(500,300, image = control)
	route.create_text(500,360,text='Control node',font=('Arial', 20))
	route.create_text(275,570,text='Compute 1',font=('Arial', 16))
	route.create_text(425,570,text='Compute 2',font=('Arial', 16))
	route.create_text(575,570,text='Compute 3',font=('Arial', 16))
	route.create_text(725,570,text='Compute 4',font=('Arial', 16))
	route.create_line(500, 200, 500, 250, fill='brown', width=5)
	route.create_line(320, 140, 445, 140, fill='brown', width=5)

	route.create_image(275,500, image = compute)
	route.create_image(425,500, image = compute)
	route.create_image(575,500, image = compute)
	route.create_image(725,500, image = compute)
	route.create_line(500, 375, 275, 455, fill='green', width=3)
	route.create_line(500, 375, 425, 455, fill='green', width=3)
	route.create_line(500, 375, 575, 455, fill='green', width=3)
	route.create_line(500, 375, 725, 455, fill='green', width=3)
	Thread(target=update).start()
	root.mainloop()

draw()