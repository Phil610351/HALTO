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
	global route
	route.delete("all")
	route.create_text(760,130,text=req['data'],font=('Arial', 32))
	return 'Ok'
def draw():
	global route
	root = Tk()
	route = Canvas(root,width=1000, height=720)
	route.pack()
	root.mainloop()
if __name__ == '__main__':
	Thread(target = draw).start()
	app.debug = True
	app.run()
