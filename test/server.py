from flask import Flask, request, jsonify
from time import time

app = Flask(__name__)

@app.route('/',methods=['POST'])
def test():
    tasks=request.get_json(force=True)
    result=list()
    for i in range(len(tasks)):
        start=time()
        for j in range(tasks[str(i)]):
            f=open('realtime.jpg', 'rb')
            b=f.read()
            d=open('test.png', 'wb')
            d.write(b)
        result.append(time()-start)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)