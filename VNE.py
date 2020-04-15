from flask import Flask, request
from flask_cors import CORS
from threading import Thread
from tkinter import *
app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "*"}})
@app.route('/',methods=['POST'])
def index():
	req = request.get_json()
	print(req)
	value[req['instance']]=req['data']
	global route
	route.delete("all")
	route.create_text(200,100,text=value[0],font=('Arial', 16))
	route.create_oval( 150, 50, 250, 150, width = 3 )
	route.create_text(700,100,text=value[1],font=('Arial', 16))
	route.create_oval( 650, 50, 750, 150, width = 3 )
	route.create_text(450,500,text=value[2],font=('Arial', 16))
	route.create_oval( 400, 450, 500, 550, width = 3 )
	return 'Ok'
def draw():
	global route
	root = Tk()
	route = Canvas(root,width=900, height=600)
	route.pack()
	root.mainloop()
value=['0']*3
if __name__ == '__main__':
	Thread(target = draw).start()
	app.debug = True
	app.run()
