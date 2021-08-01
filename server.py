from flask import Flask, request, jsonify
from time import time

app = Flask(__name__)

@app.route('/',methods=['POST'])
def test():
    req=request.get_json(force=True)
    print(req)
    start=time()
    result=dict()
    for i in range(req['round']):
        f=open('realtime.jpg', 'rb')
        b=f.read()
        d=open('test.png', 'wb')
        d.write(b)
    result['t']=time()-start
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)