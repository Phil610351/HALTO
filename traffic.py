import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.arima_model import ARIMA
from keras.layers import Flatten, Dense, Activation
from keras.models import Sequential

zeta=300
alpha=0.7

def optimal():
	pass

def gen_task():
	tasks=dict()
	for i in range(users):
		buf=dict()
		buf['a']=np.random.uniform(100,1000)*2/1000
		buf['d']=buf['a']
		buf['fl']=np.random.uniform(1.5,2.5)
		buf['Tm']=np.random.uniform(avg,1)
		buf['pri']=np.random.uniform(0.1,1)
		buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
		tasks[i]=buf
	return tasks

train_x=list()
train_y=list()
y=list()
with open("train.dat") as f:
	a=f.read().split('\n')
	count=0
	hour=0
	buf=list()
	for e in a:
		e=e.split()
		#if int(e[0][:10])-1189809385>3600*hour:
		if int(e[0][:10])-1201639675>3600*hour:
			count+=1
			#for i in range( (int(int(e[0][:10])-1201639675))-60*hour):
			#	y.append(0)
			#y.append(count*0.3-zeta*count/2000)
			buf.append(count)
			count=0
			hour+=1
			#hour=int(int(e[0][:10])-1201639675)+1

			if len(buf)>10:
				buf.pop(0)
				train_y.append(buf[-1])
				train_x.append(buf[:])
		else:
			count+=1

#plt.plot(y)
#plt.show()

train_y.pop(0)
train_x.pop()
print(len(train_x),len(train_y))

DNN = Sequential()
DNN.add(Dense(32, input_shape=(10,)) )
DNN.add(Dense(32, activation="relu"))
DNN.add(Dense(1))
DNN.compile(loss='mae', optimizer='adam', metrics=['mae'])
DNN.fit([train_x], [train_y], epochs=1000, batch_size=100)

y=list()
train_x=list()
train_y=list()

#165天
with open("test.dat") as f:
	a=f.read().split('\n')
	count=0
	hour=0
	buf=list()
	for e in a:
		e=e.split()
		if int(e[0][:10])-1189809385>3600*hour:
			y.append(count)
			buf.append(count)
			count=0
			hour+=1
			
			if len(buf)>10:
				buf.pop(0)
				train_y.append(buf[-1])
				train_x.append(buf[:])
		else:
			count+=1
		if hour>5000:
			break

print(train_x)
RL_p=DNN.predict( np.array(train_x))
RL=list()

for i in range(len(RL_p)):
	RL.append(y[i]*0.3-RL_p[i]*zeta/2000)

'''plt.plot(y[:48], label='DNN')
plt.plot(train_y[:48], label='real')
plt.plot(fit3[10:58], label='ARIMA')'''
plt.plot(RL, label='DNN')
plt.plot(y, label='real')
plt.legend()
plt.show()

'''
for i in range(len(train_x)):
	print(np.array(train_x[i]).shape)
	print(model.predict( np.array(train_x[i]) ) )'''