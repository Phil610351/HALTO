from time import time

start=time()
for i in range(10):
	for j in range(100):
		f=open('realtime.jpg','rb')
		b=f.read()
		d=open('test.png','wb')
		d.write(b)
print((time()-start)/10)