from tkinter import *
from time import time, sleep
from threading import Thread

c=list()
data1=['0.00','98.50','99.50',98.01,100.0,'99.00',98.99,100.0,'98.50','99.00', '0.00']
data2=['0.00','99.00',100.0,100.0,98.99,'99.00',98.99,98.51,98.99,'99.00', '0.00']
data3=['0.00',100.0,'99.00',100.0,98.49,'99.00',98.49,'99.00',100.0,'99.00', '0.00']
data4=['0.00',100.0,'99.00','98.50','99.00','98.50','98.50','99.00',98.99,98.51, '0.00']
data5=['0.00','99.00',98.99,'99.00',98.99,100.0,100.0,'98.50','99.00','99.00', '0.00']

def draw():

	def update():
		for i in range(11):
			sleep(1)
			for e in c:
				route.delete(e)
			c.append(route.create_text(200,490,text=data1[i],font=('Arial', 16)))
			c.append(route.create_text(350,490,text=data2[i],font=('Arial', 16)))
			c.append(route.create_text(500,490,text=data3[i],font=('Arial', 16)))
			c.append(route.create_text(650,490,text=data4[i],font=('Arial', 16)))
			c.append(route.create_text(800,490,text=data5[i],font=('Arial', 16)))

	global route
	global c
	root=Tk()
	route=Canvas(root,width=1000, height=800)
	route.pack()
	
	control=PhotoImage(file = 'control.png')
	compute=PhotoImage(file = 'compute.png')
	
	route.create_image(500,300, image = control)
	route.create_text(500,360,text='Control node',font=('Arial', 20))
	route.create_text(200,570,text='Compute 1',font=('Arial', 16))
	route.create_text(350,570,text='Compute 2',font=('Arial', 16))
	route.create_text(500,570,text='Compute 3',font=('Arial', 16))
	route.create_text(650,570,text='Compute 4',font=('Arial', 16))
	route.create_text(800,570,text='Compute 5',font=('Arial', 16))

	route.create_image(200,500, image = compute)
	route.create_image(350,500, image = compute)
	route.create_image(500,500, image = compute)
	route.create_image(650,500, image = compute)
	route.create_image(800,500, image = compute)
	route.create_line(500, 375, 200, 455, fill='green', width= 3 )
	route.create_line(500, 375, 350, 455, fill='green', width= 3 )
	route.create_line(500, 375, 500, 455, fill='green', width= 3 )
	route.create_line(500, 375, 650, 455, fill='green', width= 3 )
	route.create_line(500, 375, 800, 455, fill='green', width= 3 )
	Thread(target=update).start()
	root.mainloop()

draw()